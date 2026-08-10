"""Check whether each candidate stream is actually playable.

The check walks the whole HLS chain (master playlist, variant playlist, one media
segment) and only reports `ok` when real media bytes come back, so a stale manifest that
no longer has segments behind it is not mistaken for a live channel.

Results are merged into data/status.json rather than overwriting it. Every URL keeps a
first_seen date, a last_ok date and a consecutive failure count, which is what lets
build.py wait for repeated failures before dropping a channel instead of reacting to one
bad night on a CDN.
"""
import datetime as dt
import re
import socket
import ssl
import sys
import time
import http.cookiejar
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from lib import CANDIDATES, DATA, SSL_CTX, UA, install_public_dns, log, read_json, write_json

TIMEOUT = 12
WORKERS = 24
RETRY_REASONS = ("timeout", "http502", "http503", "http504", "tls")
MEDIA_HINTS = ("video/", "audio/", "mp2t", "octet-stream", "mpegurl")

# Verified Iran-only CDNs: reachable from inside Iran, silently dropped from abroad.
# A failure against one of these is reported as `iran_only`, never as dead, because the
# probe runs on a GitHub runner outside Iran and would otherwise delete exactly the
# domestic channels this project exists to list.
IRAN_ONLY_HOSTS = ("irib.ir", "iranseda.ir", "sepehr.ir")

# Dead subscription CDNs. These answer 403 to everyone, which is an expired service
# rather than a geographic restriction, so their failures must count as dead.
DEAD_403_HOSTS = ("pandatv.tn", "onetv.app")

GEO_TEXT = ("not available in your", "your region", "your country", "geoblock",
            "geo-block", "outside iran", "خارج از ایران", "در کشور شما")


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


# Some CDNs answer the first request for a segment with a redirect back to the same URL,
# setting a cookie on the way. urllib treats that as a loop and gives up, so requests carry
# a cookie jar and a same URL redirect is followed once by hand.
_opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
    urllib.request.HTTPSHandler(context=SSL_CTX))

HEAD_BYTES = 32768
PLAYLIST_LIMIT = 4 * 1024 * 1024  # live HLS windows can list thousands of segments


def fetch(url, referrer=None, user_agent=None, limit=PLAYLIST_LIMIT, ranged=False,
          _retried=False):
    """Return (status, headers, body, final_url). status is an int, or an error keyword.

    `limit` has to be generous for playlists: a long live window can run past 300 KB, and
    reading a partial body chops the last segment URL in half, which then 403s and makes a
    perfectly healthy channel look dead.
    """
    req = urllib.request.Request(url)
    req.add_header("User-Agent", user_agent or UA)
    req.add_header("Accept", "*/*")
    if referrer:
        req.add_header("Referer", referrer)
    if ranged:
        req.add_header("Range", "bytes=0-131071")
    try:
        with _opener.open(req, timeout=TIMEOUT) as response:
            # Read a small head first. Only playlists are worth reading in full, so a live
            # video endpoint costs one small chunk instead of megabytes of transfer.
            body = response.read(HEAD_BYTES)
            if is_hls(body) and len(body) == HEAD_BYTES:
                body += response.read(max(0, limit - HEAD_BYTES))
            return response.status, dict(response.headers), body, response.geturl()
    except urllib.error.HTTPError as exc:
        if exc.code in (301, 302, 303, 307, 308) and not _retried:
            target = urllib.parse.urljoin(url, exc.headers.get("Location") or "")
            if target:
                return fetch(target, referrer, user_agent, limit, ranged, _retried=True)
        try:
            body = exc.read(4096)
        except Exception:
            body = b""
        return exc.code, dict(exc.headers or {}), body, url
    except urllib.error.URLError as exc:
        reason = exc.reason
        for kind, keyword in ((socket.gaierror, "dns"), (socket.timeout, "timeout"),
                              (ConnectionRefusedError, "refused"), (ssl.SSLError, "tls")):
            if isinstance(reason, kind):
                return keyword, {}, b"", url
        return f"conn:{type(reason).__name__}", {}, b"", url
    except socket.timeout:
        return "timeout", {}, b"", url
    except Exception as exc:
        return f"err:{type(exc).__name__}", {}, b"", url


def is_hls(body):
    return body[:512].lstrip().startswith(b"#EXTM3U")


# A tag written without its leading '#'. RFC 8216 says any line that is not blank and does
# not start with '#' is a URI, so a strict client requests the tag text as if it were a
# stream and then stalls. Telewebion's master playlist does exactly this with
# `EXT-X-VERSION:6`, which is why some players show one frame and stop.
BARE_TAG = re.compile(rb"^EXT-X-[A-Z-]+.*$", re.M)


RELATIVE_URI = re.compile(rb"^(?!#)(?!https?://)\S+\.(?:ts|m3u8|m4s|mp4|aac)", re.M)


def manifest_defects(body, requested, final):
    """Spec violations, and shapes that break clients which are not strictly compliant.

    `tag-missing-hash` is a tag written without its leading '#'. RFC 8216 treats any non
    blank line that does not start with '#' as a URI, so a strict client requests the tag
    text as a stream and stalls.

    `relative-uris-behind-redirect` is the costlier one. When a manifest is served from a
    different directory than the one requested, every relative URI inside it must be
    resolved against the final URL. Telewebion's ncdn host redirects manifests to a
    numbered edge node and then refuses to serve segments itself, so a client that
    resolves against the requested URL asks ncdn for every segment and is refused each
    time. The manifest loads, the first frame never arrives.
    """
    defects = []
    if BARE_TAG.search(body[:4096]):
        defects.append("tag-missing-hash")
    if final and final.split("?")[0].rsplit("/", 1)[0] != requested.split("?")[0].rsplit("/", 1)[0]:
        if RELATIVE_URI.search(body[:8192]):
            defects.append("relative-uris-behind-redirect")
    return defects


def is_media(body, content_type):
    """Media bytes rather than an error page dressed up as a 200."""
    if body[:1024].lstrip()[:1] == b"<":
        return False
    # MPEG-TS packets open with the 0x47 sync byte, fragmented MP4 with an ftyp or styp box.
    if body[:1] == b"\x47" or body[4:8] in (b"ftyp", b"styp", b"moof"):
        return True
    ctype = (content_type or "").lower()
    return any(hint in ctype for hint in MEDIA_HINTS) and len(body) > 1024


BANDWIDTH = re.compile(r"[^-]BANDWIDTH=(\d+)")
RESOLUTION = re.compile(r"RESOLUTION=([\dx]+)")


def parse_variants(body, base):
    """Return [(bandwidth, resolution, url)] from a master playlist, highest bitrate first.

    Attribute values can contain commas (CODECS="avc1.64001f,mp4a.40.2"), so the two
    attributes that matter are matched directly instead of splitting the line.
    """
    variants, pending = [], None
    for line in body.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if line.startswith("#EXT-X-STREAM-INF"):
            bandwidth = BANDWIDTH.search(line)
            resolution = RESOLUTION.search(line)
            pending = (int(bandwidth.group(1)) if bandwidth else 0,
                       resolution.group(1) if resolution else None)
        elif line and not line.startswith("#") and pending:
            variants.append((pending[0], pending[1], urllib.parse.urljoin(base, line)))
            pending = None
    return sorted(variants, key=lambda v: -v[0])


def parse_segments(body, base, truncated=False):
    """Return absolute segment URLs. Drops the final entry when the body was cut short,
    because a half read line yields a URL that looks valid and always fails."""
    segments, take = [], False
    for line in body.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if line.startswith("#EXTINF"):
            take = True
        elif line.startswith("#EXT-X-MAP:") and 'URI="' in line:
            segments.append(urllib.parse.urljoin(base, line.split('URI="', 1)[1].split('"', 1)[0]))
        elif line and not line.startswith("#") and take:
            segments.append(urllib.parse.urljoin(base, line))
            take = False
    if truncated and len(segments) > 1:
        segments.pop()
    return segments


def classify_failure(host, status, body):
    """Decide between a geographic restriction and a genuinely dead stream."""
    if any(h in host for h in DEAD_403_HOSTS):
        return "dead"
    if any(h in host for h in IRAN_ONLY_HOSTS):
        return "iran_only"
    if status in (403, 451):
        text = body[:2048].decode("utf-8", "replace").lower()
        return "iran_only" if any(word in text for word in GEO_TEXT) else "dead"
    return "dead"


def probe_once(record):
    url = record["url"]
    referrer, user_agent = record.get("referrer"), record.get("user_agent")
    host = urllib.parse.urlparse(url).hostname or ""
    started = time.time()
    result = {"url": url}

    status, headers, body, final = fetch(url, referrer, user_agent)
    result["ms"] = int((time.time() - started) * 1000)

    # A plain http endpoint that permanently redirects to the identical https address is
    # published in its upgraded form, saving every client a redirect. The match has to be
    # exact: CDNs that redirect to a per session edge node must keep their original URL,
    # because that edge address is not stable.
    if url.startswith("http://") and final == "https://" + url.removeprefix("http://"):
        result["final_url"] = final

    if not isinstance(status, int):
        return {**result, "state": classify_failure(host, None, b""), "reason": status}
    if status >= 400:
        return {**result, "state": classify_failure(host, status, body), "reason": f"http{status}"}

    content_type = headers.get("Content-Type", "")
    if not is_hls(body):
        if b"<MPD" in body[:1024] or "dash+xml" in content_type.lower():
            return {**result, "state": "ok", "kind": "dash"}
        if is_media(body, content_type):
            return {**result, "state": "ok", "kind": "direct"}
        return {**result, "state": "dead", "reason": "not_media"}

    defects = manifest_defects(body, url, final)
    if defects:
        result["defects"] = defects

    playlist_url, playlist_body = final, body
    variants = parse_variants(body, final)
    if variants:
        result["variants"] = len(variants)
        # Walk down from the highest bitrate. Some CDNs advertise a top variant that is
        # not actually published, and a client would simply play the next one down, so
        # failing on the first variant alone would wrongly condemn a working channel.
        failure = None
        for bandwidth, resolution, variant_url in variants:
            vstatus, vheaders, vbody, vfinal = fetch(variant_url, referrer, user_agent)
            usable_variant = isinstance(vstatus, int) and vstatus < 400
            if usable_variant and not is_hls(vbody) and is_media(vbody, vheaders.get("Content-Type")):
                # This variant points straight at a media stream.
                result.update(resolution=resolution, bandwidth=bandwidth or None)
                return {**result, "state": "ok", "kind": "hls"}
            if usable_variant and is_hls(vbody):
                result.update(resolution=resolution)
                if bandwidth:
                    result["bandwidth"] = bandwidth
                playlist_url, playlist_body = vfinal, vbody
                break
            failure = vstatus
        else:
            return {**result,
                    "state": classify_failure(host, failure if isinstance(failure, int) else None, b""),
                    "reason": f"variant:{failure}", "kind": "hls"}
        if resolution:
            result["resolution"] = resolution

    segments = parse_segments(playlist_body, playlist_url,
                              truncated=len(playlist_body) >= PLAYLIST_LIMIT)
    if not segments:
        return {**result, "state": "dead", "reason": "no_segments", "kind": "hls"}

    # The decisive test: pull bytes from a real segment. The last one is the live edge.
    sstatus, sheaders, sbody, sfinal = fetch(segments[-1], referrer, user_agent,
                                             limit=196608, ranged=True)
    # A few packagers put another playlist where a segment should be. Descend once.
    if isinstance(sstatus, int) and sstatus < 400 and is_hls(sbody):
        nested = parse_segments(sbody, sfinal)
        if nested:
            sstatus, sheaders, sbody, sfinal = fetch(nested[-1], referrer, user_agent,
                                                     limit=196608, ranged=True)
    # Judge the segment on whether it is media, not on how big it is. A live edge segment
    # can be a couple of hundred bytes while it is still being written, and one MPEG-TS
    # packet is only 188, so a size floor rejects perfectly good streams.
    if isinstance(sstatus, int) and sstatus < 400 and \
            (is_media(sbody, sheaders.get("Content-Type")) or len(sbody) > 8192):
        return {**result, "state": "ok", "kind": "hls", "bytes": len(sbody)}
    return {**result, "state": classify_failure(host, sstatus if isinstance(sstatus, int) else None, sbody),
            "reason": f"segment:{sstatus}", "kind": "hls"}


def probe(record):
    """Probe once, and retry a transient looking failure before condemning the stream."""
    result = probe_once(record)
    if result["state"] != "ok" and result.get("reason") in RETRY_REASONS:
        time.sleep(1.5)
        retry = probe_once(record)
        if retry["state"] == "ok" or result["state"] == "dead":
            return retry
    return result


def main():
    install_public_dns()
    candidates = read_json(CANDIDATES, [])
    if len(sys.argv) > 1:
        candidates = candidates[: int(sys.argv[1])]
    log(f"probing {len(candidates)} urls, {WORKERS} workers")

    results = []
    with ThreadPoolExecutor(WORKERS) as pool:
        for done, result in enumerate(pool.map(probe, candidates), 1):
            results.append(result)
            if done % 50 == 0:
                log(f"  {done}/{len(candidates)}")

    status = read_json(DATA / "status.json", {}) or {}
    streams = status.get("streams", {})
    timestamp = now()
    for result in results:
        entry = streams.setdefault(result["url"],
                                   {"first_seen": timestamp, "fails": 0, "checks": 0, "oks": 0})
        entry.update({k: v for k, v in result.items() if k != "url"})
        entry["last_checked"] = timestamp
        # `checks` and `oks` accumulate across every run. Their ratio is the uptime record
        # build.py uses to rank streams, so a stream with a long clean history outranks a
        # newcomer that merely happens to answer today.
        entry["checks"] = entry.get("checks", 0) + 1
        entry["oks"] = entry.get("oks", 0) + (1 if result["state"] in ("ok", "iran_only") else 0)
        if result["state"] == "ok":
            entry["last_ok"] = timestamp
            entry["fails"] = 0
        else:
            entry["fails"] = entry.get("fails", 0) + 1
        entry["uptime"] = round(entry["oks"] / entry["checks"], 3)

    probed = {r["url"] for r in results}
    for url, entry in streams.items():
        if url not in probed:
            entry["state"] = "gone"  # no longer offered by any source

    write_json(DATA / "status.json",
               {"generated_at": timestamp, "checked": len(results), "streams": streams})

    counts = Counter(r["state"] for r in results)
    log(f"states: {dict(counts)}")
    log(f"reasons: {dict(Counter(r.get('reason') for r in results if r['state'] != 'ok').most_common(10))}")


if __name__ == "__main__":
    main()
