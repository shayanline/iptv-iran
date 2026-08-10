"""Shared helpers: paths, HTTP, M3U parsing."""
import gzip
import io
import json
import os
import pathlib
import re
import socket
import ssl
import sys
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent.parent
# data/ holds only the three files worth keeping: the hand maintained curated.json, the
# probe history in status.json, and the published channels.json. Anything regenerated from
# scratch every run is an intermediate and belongs in build/, which is not committed.
DATA = HERE / "data"
BUILD = HERE / "build"
CANDIDATES = BUILD / "candidates.json"
UA = "VLC/3.0.20 LibVLC/3.0.20"

# Several Iranian CDNs present expired or mismatched certificates. Verification is
# disabled deliberately: this checks whether a public stream responds, it never sends
# credentials, so a bad certificate is not a reason to call a channel dead.
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

EXTINF = re.compile(r"^#EXTINF")
ATTRS = re.compile(r'([\w-]+)="([^"]*)"')


def log(message):
    print(message, flush=True)


# --- DNS ------------------------------------------------------------------------------
# A network level filter such as AdGuard Home, Pi-hole or a corporate resolver answers
# blocked names with 0.0.0.0 or NXDOMAIN. To a stream checker that is indistinguishable
# from a dead host, so a local run could mark working channels as dead and commit the
# result. Names are therefore resolved over DNS-over-HTTPS by default, which makes a probe
# produce the same answer on a laptop behind a filter as it does on a CI runner.
# Set IPTV_DNS=system to fall back to the operating system resolver.
DOH_ENDPOINT = "https://cloudflare-dns.com/dns-query"
_dns_cache = {}
_system_getaddrinfo = socket.getaddrinfo


def _resolve_doh(host):
    query = urllib.parse.urlencode({"name": host, "type": "A"})
    req = urllib.request.Request(f"{DOH_ENDPOINT}?{query}",
                                 headers={"Accept": "application/dns-json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=8, context=SSL_CTX) as response:
        payload = json.loads(response.read())
    return [a["data"] for a in payload.get("Answer", []) if a.get("type") == 1]


def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if isinstance(host, str) and not _is_ip(host):
        if host not in _dns_cache:
            try:
                _dns_cache[host] = _resolve_doh(host)
            except Exception:
                _dns_cache[host] = []
        addresses = _dns_cache[host]
        if addresses:
            return [(socket.AF_INET, type or socket.SOCK_STREAM, proto or 6, "", (ip, port))
                    for ip in addresses]
    return _system_getaddrinfo(host, port, family, type, proto, flags)


def _is_ip(host):
    try:
        socket.inet_aton(host)
        return True
    except OSError:
        return ":" in host


def install_public_dns():
    """Route hostname lookups through DNS-over-HTTPS unless IPTV_DNS=system."""
    if os.environ.get("IPTV_DNS", "").lower() == "system":
        log("dns: using the system resolver (IPTV_DNS=system)")
        return False
    try:
        _resolve_doh("cloudflare.com")
    except Exception as exc:
        log(f"dns: DNS-over-HTTPS unavailable ({type(exc).__name__}), using the system resolver")
        return False
    socket.getaddrinfo = _patched_getaddrinfo
    log("dns: resolving over DNS-over-HTTPS, so local filtering cannot skew results")
    return True


def fetch_text(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as response:
        raw = response.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    return raw.decode("utf-8", "replace")


def fetch_text_with_final(url, timeout=30):
    """Like fetch_text, but also returns the URL the response finally came from."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as response:
        raw, final = response.read(), response.geturl()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    return raw.decode("utf-8", "replace"), final


def load_json_url(url, timeout=60):
    return json.loads(fetch_text(url, timeout))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def parse_m3u(text):
    """Yield (attrs, title, url) per entry, tolerating blank lines and #EXTVLCOPT blocks."""
    lines = [line.strip() for line in text.splitlines()]
    index = 0
    while index < len(lines):
        if EXTINF.match(lines[index]):
            head = lines[index]
            attrs = dict(ATTRS.findall(head))
            title = head.split(",", 1)[1].strip() if "," in head else ""
            cursor = index + 1
            while cursor < len(lines) and (not lines[cursor] or lines[cursor].startswith("#")):
                cursor += 1
            if cursor < len(lines):
                yield attrs, title, lines[cursor]
            index = cursor
        index += 1


def die(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)
