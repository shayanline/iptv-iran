"""Find streams that the public playlists do not carry, and better URLs for ones they do.

Some broadcasters publish a web player whose stream endpoint follows a fixed pattern per
channel. Where that pattern is known, candidate URLs can be generated from a list of
channel identifiers and handed to probe.py, which decides which ones actually work. This
finds channels missing from the public sources, and often a higher resolution endpoint for
channels that are already listed.

Templates are used rather than scraping the players. A template keeps working when a site
rewrites its front end, needs no browser and no JavaScript execution, and the prober
already verifies every result, so a wrong guess costs one failed request.

A provider can also be marked `prefer_variant`, which Telewebion needs for two reasons.

Its master playlist is malformed: `EXT-X-VERSION:6` is written without the leading `#`, so
a strict client reads that line as a stream URI, requests it and stalls. Reading the master
once to learn which renditions exist, then publishing the rendition directly, avoids it.

Its manifest host is also a redirector. `ncdn.telewebion.ir` answers a manifest request
with a redirect to a numbered edge node, and then refuses to serve segments itself. Segment
URIs inside the manifest are relative, so a client must resolve them against the final URL.
Clients that resolve against the requested URL instead ask ncdn for every segment and are
refused every time: the manifest loads, the picture never starts. Following the redirect
here and publishing the resolved edge URL removes the ambiguity, so the playlist works the
same in a strict client and a lenient one. The ncdn form is still offered as a fallback in
case an edge node is retired between refreshes.
"""
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from lib import CANDIDATES, DATA, fetch_text_with_final, log, read_json

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


def previous_edges(slug):
    """Edge URLs already known to work for this slug, from the last probe run.

    Reusing a node that still works keeps the published URL stable between refreshes,
    so a fortnightly run does not rewrite every Telewebion entry for no reason.
    """
    status = (read_json(DATA / "status.json", {}) or {}).get("streams", {})
    return [url for url, entry in status.items()
            if f"/{slug}/live/" in url and "live-aburayhan" in url and entry.get("state") == "ok"]


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
                text, final = fetch_text_with_final(master, timeout=15)
                found = best_rendition(text)
            except Exception:
                found, final = None, None
            return slug, channel_id, master, found, final

        with ThreadPoolExecutor(12) as pool:
            for slug, channel_id, master, found, final in pool.map(resolve, slugs.items()):
                stable = config["variant_template"].format(id=slug, rendition=found[0]) if found else None
                if found:
                    # Keep last run's node if it is still serving, to avoid needless churn.
                    for known in previous_edges(slug):
                        if known.endswith(found[0]):
                            yield known, provider, slug, channel_id or None, found[1]
                            break
                if found and final:
                    # Resolved against the edge the redirector chose, so no client has to
                    # follow a redirect to find the segments.
                    resolved = urllib.parse.urljoin(final.split("?")[0], found[0])
                    if resolved != stable:
                        yield resolved, provider, slug, channel_id or None, found[1]
                if stable:
                    yield stable, provider, slug, channel_id or None, found[1]
                # The master is still offered as a last fallback.
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
