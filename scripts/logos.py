"""Mirror channel logos into the repository so they load everywhere.

Most upstream logos are hosted on imgur, which geo-blocks several countries including the
United Kingdom and Iran. It does not fail cleanly: it answers HTTP 200 with a 336x478
image reading "Content not viewable in your region", so a player renders that error card
next to the channel name. Wikimedia rate limits, and several broadcaster CDNs disappear
without notice. Hotlinking any of them makes the playlist's appearance depend on where the
viewer sits.

So every logo is fetched once, checked for real image bytes, and committed to
`assets/logos/`. The playlists then point at this repository, the same origin that already
serves the playlists themselves, which adds no new dependency for the viewer.

Mirroring only runs with `--mirror`, which the GitHub Actions workflow passes. A local
build reuses whatever is already committed and touches the network for logos not at all,
because a contributor behind a geo-block would otherwise re-download error cards over the
good images.
"""
import hashlib
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

from lib import CANDIDATES, DATA, HERE, SSL_CTX, install_public_dns, log, read_json

REPO = "shayanline/iptv-iran"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/assets/logos"
ASSETS = HERE / "assets" / "logos"

TIMEOUT = 15
WORKERS = 8
RETRIES = 4
MIN_BYTES = 512
MAX_BYTES = 2_000_000

# Wikimedia asks for a descriptive agent naming the project. A media player string
# invites throttling.
LOGO_UA = f"iptv-iran/1.0 (+https://github.com/{REPO}) logo-mirror"

# One request at a time per host, spaced out, so a source holding many logos is not hit
# with eight parallel requests and made to answer 429.
HOST_INTERVAL = 0.4
_host_locks = defaultdict(threading.Lock)
_host_last = defaultdict(float)

# Served with a 200 but is not the logo. Keyed by md5 of the body.
KNOWN_PLACEHOLDERS = {
    "f953f499c9824953791551bfef65fe61": "imgur geo-block placeholder",
}

MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"RIFF", "webp"),
    (b"BM", "bmp"),
]


# Magic bytes prove a file started as an image, not that all of it arrived. A read cut
# short by MAX_BYTES, or a connection dropped mid transfer, still begins with a valid
# signature, so it passed the old check and a half written logo was committed. Every
# container marks its end, so the tail is checked too.
TERMINATORS = {
    "png": lambda b: b.rstrip().endswith(b"IEND\xaeB`\x82"),
    "jpg": lambda b: b.rstrip().endswith(b"\xff\xd9"),
    "gif": lambda b: b.rstrip().endswith(b";"),
    "webp": lambda b: len(b) >= 8 and int.from_bytes(b[4:8], "little") + 8 <= len(b),
    "bmp": lambda b: len(b) >= 6 and int.from_bytes(b[2:6], "little") <= len(b),
    "svg": lambda b: b.rstrip().endswith(b">"),
}


def is_complete(body, kind):
    check = TERMINATORS.get(kind)
    return check(body) if check else True


def image_kind(body):
    for signature, name in MAGIC:
        if body.startswith(signature):
            return name
    if body[:400].lstrip().startswith((b"<svg", b"<?xml")):
        return "svg"
    return None


def fetch(url):
    """Fetch bytes, backing off when a host asks us to slow down."""
    host = urllib.parse.urlparse(url).hostname or ""
    request = urllib.request.Request(url, headers={"User-Agent": LOGO_UA, "Accept": "image/*,*/*"})
    for attempt in range(RETRIES):
        try:
            with _host_locks[host]:
                wait = HOST_INTERVAL - (time.monotonic() - _host_last[host])
                if wait > 0:
                    time.sleep(wait)
                try:
                    with urllib.request.urlopen(request, timeout=TIMEOUT, context=SSL_CTX) as response:
                        return response.status, response.read(MAX_BYTES)
                finally:
                    _host_last[host] = time.monotonic()
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < RETRIES - 1:
                time.sleep(2.0 * (attempt + 1))
                continue
            return exc.code, b""
        except Exception as exc:
            if attempt < RETRIES - 1:
                time.sleep(1.0 * (attempt + 1))
                continue
            return type(exc).__name__, b""
    return "retries", b""


def evaluate(url):
    """Return (body, kind, detail). body is empty when the logo is unusable."""
    status, body = fetch(url)
    if status != 200:
        return b"", None, f"http{status}" if isinstance(status, int) else str(status)
    if len(body) < MIN_BYTES:
        return b"", None, f"only {len(body)} bytes"
    placeholder = KNOWN_PLACEHOLDERS.get(hashlib.md5(body).hexdigest())
    if placeholder:
        return b"", None, placeholder
    kind = image_kind(body)
    if not kind:
        return b"", None, "not an image"
    if not is_complete(body, kind):
        return b"", None, f"truncated {kind}, {len(body)} bytes"
    return body, kind, "ok"


def candidates_for(channel_id, records, curated):
    """Logo URLs to try for one channel, most trusted first."""
    urls = []
    override = (curated.get("logos") or {}).get(channel_id)
    if override:
        urls.append(override)
    for record in records:
        for url in ((record.get("db") or {}).get("logo"), record.get("logo")):
            if url and url not in urls:
                urls.append(url)
    return urls


def existing_asset(channel_id):
    for path in sorted(ASSETS.glob(f"{channel_id}.*")):
        return path
    return None


def mirror(work):
    """Refresh assets/logos from the sources.

    A mirrored logo is permanent. Once an image has been captured it is only ever
    replaced by another valid image, never deleted because the URL it came from has since
    broken. Sources rot constantly, and a channel that still works should not silently
    lose its logo just because a host went away. Assets are only removed when the channel
    itself disappears from every source, which is handled by the caller.
    """
    ASSETS.mkdir(parents=True, exist_ok=True)
    rejected = []
    lock = threading.Lock()

    def handle(item):
        channel_id, urls = item
        for url in urls:
            body, kind, detail = evaluate(url)
            if body:
                return channel_id, body, kind
            with lock:
                rejected.append((channel_id, url, detail))
        return channel_id, b"", None

    added = replaced = kept = 0
    with ThreadPoolExecutor(WORKERS) as pool:
        for channel_id, body, kind in pool.map(handle, sorted(work.items())):
            current = existing_asset(channel_id)
            if not body:
                # Nothing usable this run. Whatever is already committed stays.
                kept += 1 if current else 0
                continue
            path = ASSETS / f"{channel_id}.{kind}"
            if current and current != path:
                current.unlink()  # the format changed, so the old extension is stale
            if not path.exists():
                added += 1
            elif path.read_bytes() != body:
                replaced += 1
            else:
                continue
            path.write_bytes(body)

    reasons = Counter(detail for _, _, detail in rejected)
    log(f"  {added} added, {replaced} updated, {kept} kept from a previous run")
    log(f"  {len(rejected)} candidate urls unusable: {dict(reasons.most_common(5))}")


def main():
    do_mirror = "--mirror" in sys.argv
    candidates = read_json(CANDIDATES, [])
    curated = read_json(DATA / "curated.json", {})

    by_channel = {}
    for record in candidates:
        channel_id = (record.get("db") or {}).get("id")
        if channel_id:
            by_channel.setdefault(channel_id, []).append(record)

    if do_mirror:
        install_public_dns()
        work = {cid: candidates_for(cid, records, curated) for cid, records in by_channel.items()}
        work = {cid: urls for cid, urls in work.items() if urls}
        log(f"mirroring logos for {len(work)} channels")
        mirror(work)
        # A few logos are committed directly rather than fetched, because no host serves
        # them. IRNA TV only publishes its mark inside a favicon bundle. Makran and Iran
        # Comedy are carried by no logo library at all, so their on air marks were lifted
        # from the video: many frames were reduced to a per pixel minimum, which keeps a
        # static overlay and cancels the moving picture behind it. Those channels
        # contribute no candidate url, so the loop above skips them and their committed
        # file is left alone.
        # The only reason to delete an asset: the channel is gone from every source.
        known = set(by_channel)
        for path in ASSETS.glob("*.*"):
            if path.stem not in known:
                path.unlink()
                log(f"  removed {path.name}, channel no longer in any source")
    else:
        log("reusing committed logos, pass --mirror to refresh them from the sources")

    have = sorted(p.stem for p in ASSETS.glob("*.*")) if ASSETS.exists() else []
    total = sum(p.stat().st_size for p in ASSETS.glob("*.*")) if ASSETS.exists() else 0
    log(f"{len(have)} logos in assets/logos, {total / 1024:.0f} KB")


if __name__ == "__main__":
    main()
