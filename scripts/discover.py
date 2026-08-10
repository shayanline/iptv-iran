"""Find streams that the public playlists do not carry.

Some broadcasters publish a web player whose stream endpoint follows a fixed pattern per
channel. Where that pattern is known, candidate URLs can be generated from a list of
channel identifiers and handed to probe.py, which decides which ones actually work. This
finds channels missing from the public sources, and often a higher resolution endpoint for
channels that are already listed.

Templates are used rather than scraping the players. A template keeps working when a site
rewrites its front end, needs no browser and no JavaScript execution, and the prober
already verifies every result, so a wrong guess costs one failed request.
"""
from lib import HERE, log, read_json

PROVIDERS = {
    # Telewebion is IRIB's own streaming platform. Its live endpoint is one path per
    # channel slug, and it serves adaptive HLS up to 1080p.
    "telewebion": {
        "template": "https://ncdn.telewebion.ir/{id}/live/playlist.m3u8",
        "note": "IRIB streaming platform, adaptive HLS",
    },
}


def candidate_urls(curated):
    """Yield (url, provider, slug, channel_id) for every configured provider slug."""
    discovery = curated.get("discovery", {})
    for provider, config in PROVIDERS.items():
        for slug, channel_id in (discovery.get(provider) or {}).items():
            yield config["template"].format(id=slug), provider, slug, channel_id or None


def main():
    """Report what discovery would add, without probing. Used for local inspection."""
    curated = read_json(HERE / "data" / "curated.json", {})
    known = {record["url"] for record in read_json(HERE / "data" / "candidates.json", [])}
    total = new = 0
    for url, provider, slug, channel_id in candidate_urls(curated):
        total += 1
        if url not in known:
            new += 1
            log(f"  new  {provider}/{slug} -> {channel_id or 'unidentified'}: {url}")
    log(f"{total} discovery urls configured, {new} not already in candidates.json")


if __name__ == "__main__":
    main()
