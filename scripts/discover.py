"""Find streams that the public playlists do not carry, and better URLs for ones they do.

Some broadcasters publish a web player whose stream endpoint follows a fixed pattern per
channel. Where that pattern is known, candidate URLs can be generated from a list of
channel identifiers and handed to probe.py, which decides which ones actually work. This
finds channels missing from the public sources, and often a higher resolution endpoint for
channels that are already listed.

Templates are used rather than scraping the players. A template keeps working when a site
rewrites its front end, needs no browser and no JavaScript execution, and the prober
already verifies every result, so a wrong guess costs one failed request.

A provider can also be marked `prefer_variant`. Telewebion's master playlist is malformed:
it writes `EXT-X-VERSION:6` without the leading `#`, so a strict client reads that line as
a stream URI, requests it, receives 403 and stalls after the first frame. ffmpeg and VLC
tolerate it, many set top box clients do not. For those providers the master is read once
to learn which renditions exist, and the direct rendition URL is published instead, which
is a clean media playlist with no malformed tags.
"""
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from lib import CANDIDATES, DATA, fetch_text, log, read_json

PROVIDERS = {
    "telewebion": {
        "template": "https://ncdn.telewebion.ir/{id}/live/playlist.m3u8",
        "variant_template": "https://ncdn.telewebion.ir/{id}/live/{rendition}",
        "prefer_variant": True,
        "note": "IRIB streaming platform. Master playlist is malformed, so renditions are used.",
    },
}

STREAM_INF = re.compile(r"#EXT-X-STREAM-INF:(?P<attrs>.*)")
RESOLUTION = re.compile(r"RESOLUTION=(\d+)x(\d+)")


def best_rendition(manifest):
    """Return (rendition_path, height) for the highest resolution entry in a master."""
    best, pending = None, None
    for line in manifest.splitlines():
        line = line.strip()
        match = STREAM_INF.match(line)
        if match:
            resolution = RESOLUTION.search(match.group("attrs"))
            pending = int(resolution.group(2)) if resolution else 0
        elif line and not line.startswith("#") and pending is not None:
            # Only a same directory relative path is safe to rewrite onto the stable host.
            if "/" in line.rstrip("/") and not line.startswith(("http://", "https://")):
                if best is None or pending > best[1]:
                    best = (line, pending)
            pending = None
    return best


def candidate_urls(curated):
    """Yield (url, provider, slug, channel_id, height) for every configured slug."""
    discovery = curated.get("discovery", {})
    for provider, config in PROVIDERS.items():
        slugs = discovery.get(provider) or {}
        if not config.get("prefer_variant"):
            for slug, channel_id in slugs.items():
                yield config["template"].format(id=slug), provider, slug, channel_id or None, 0
            continue

        def resolve(item):
            slug, channel_id = item
            master = config["template"].format(id=slug)
            try:
                found = best_rendition(fetch_text(master, timeout=15))
            except Exception:
                found = None
            return slug, channel_id, master, found

        with ThreadPoolExecutor(12) as pool:
            for slug, channel_id, master, found in pool.map(resolve, slugs.items()):
                if found:
                    rendition, height = found
                    yield (config["variant_template"].format(id=slug, rendition=rendition),
                           provider, slug, channel_id or None, height)
                # The master is still offered as a fallback for clients that accept it.
                yield master, provider, slug, channel_id or None, 0


def main():
    """Report what discovery would add, without probing. Used for local inspection."""
    curated = read_json(DATA / "curated.json", {})
    known = {record["url"] for record in read_json(CANDIDATES, [])}
    total = new = 0
    for url, provider, slug, channel_id, height in candidate_urls(curated):
        total += 1
        flag = "new " if url not in known else "    "
        if url not in known:
            new += 1
        log(f"  {flag} {provider}/{slug:16s} {str(height) + 'p':>6s}  {channel_id or 'unidentified':24s} {url}")
    log(f"{total} discovery urls configured, {new} not already in candidates.json")


if __name__ == "__main__":
    main()
