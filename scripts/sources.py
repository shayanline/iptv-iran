"""Harvest candidate streams from every public Iranian / Persian IPTV source.

Writes data/candidates.json: one record per distinct URL, with whatever metadata the
sources agree on. Nothing is judged here, only collected. probe.py decides what is live.
"""
import json
import re
import urllib.parse

import discover
from identity import canonical_url
from lib import HERE, fetch_text, load_json_url, log, parse_m3u, write_json

# Public sources, in descending order of metadata quality. iptv-org is the upstream
# database everything else derives from, so it is queried through its API rather than
# its generated playlists.
IPTV_ORG_API = "https://iptv-org.github.io/api"
PLAYLIST_SOURCES = [
    ("iptv-org/ir", "https://iptv-org.github.io/iptv/countries/ir.m3u"),
    ("iptv-org/fas", "https://iptv-org.github.io/iptv/languages/fas.m3u"),
    ("nexa", "https://raw.githubusercontent.com/itsyebekhe/nexa/main/playlist.m3u"),
    ("free-tv", "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"),
    ("lashkari20", "https://raw.githubusercontent.com/lashkari20/iptv/main/"
                   "ir-m3u-bestfreeiptv-10-03-22%20(1).m3u"),
]
# Free-TV keeps the domestic IRIB and provincial links in its markdown list rather than
# its playlist, because its own checker cannot reach them from outside Iran.
FREE_TV_MD = "https://raw.githubusercontent.com/Free-TV/IPTV/master/lists/iran.md"

MD_ROW = re.compile(r"\|\s*\d+\s*\|\s*(?P<name>.+?)\s*\|\s*\[.\]\((?P<url>http[^)]+)\)\s*\|(?P<rest>.*)$")


class Candidates:
    """Collects URLs, merging entries that are the same endpoint written differently."""

    def __init__(self):
        self.by_key = {}

    def add(self, url, source, channel_id=None, title=None, **extra):
        url = (url or "").strip()
        if not url.startswith(("http://", "https://")):
            return
        key = canonical_url(url)
        rec = self.by_key.get(key)
        if rec is None:
            rec = self.by_key[key] = {"url": url, "sources": [], "channel_ids": [], "titles": []}
        elif url.startswith("https://") and rec["url"].startswith("http://"):
            rec["url"] = url  # prefer the encrypted form of the same endpoint
        for field, value in (("sources", source), ("channel_ids", channel_id), ("titles", title)):
            if value and value not in rec[field]:
                rec[field].append(value)
        rec.update({k: v for k, v in extra.items() if v})


def iptv_org_database():
    """Return (channels, feeds_by_channel, logo_by_channel) from the iptv-org API."""
    channels = {c["id"]: c for c in load_json_url(f"{IPTV_ORG_API}/channels.json")}
    feeds = {}
    for feed in load_json_url(f"{IPTV_ORG_API}/feeds.json"):
        feeds.setdefault(feed["channel"], []).append(feed)
    logos = {}
    for logo in load_json_url(f"{IPTV_ORG_API}/logos.json"):
        if logo.get("in_use") and logo["channel"] not in logos:
            logos[logo["channel"]] = logo["url"]
    return channels, feeds, logos


def in_scope(channel_id, channels, feeds):
    """Iranian channels, plus any channel anywhere that carries a Persian audio feed."""
    channel = channels.get(channel_id)
    if not channel:
        return False
    if channel.get("country") == "IR":
        return True
    return any("fas" in (f.get("languages") or []) for f in feeds.get(channel_id, []))


def harvest():
    cands = Candidates()
    channels, feeds, logos = iptv_org_database()
    log(f"iptv-org database: {len(channels)} channels, {len(feeds)} feeds")

    for stream in load_json_url(f"{IPTV_ORG_API}/streams.json"):
        cid = stream.get("channel")
        if cid and in_scope(cid, channels, feeds):
            cands.add(stream["url"], "iptv-org", cid, stream.get("title"),
                      quality=stream.get("quality"), user_agent=stream.get("user_agent"),
                      referrer=stream.get("referrer"), feed=stream.get("feed"))

    for label, url in PLAYLIST_SOURCES:
        try:
            text = fetch_text(url)
        except Exception as exc:
            log(f"  {label}: unreachable ({exc}), skipped")
            continue
        added = 0
        for attrs, title, stream_url in parse_m3u(text):
            cid = (attrs.get("tvg-id") or "").split("@")[0] or None
            # The Free-TV combined playlist covers the whole world, so keep Iran only.
            if label == "free-tv" and "Iran" not in (attrs.get("group-title") or "") \
                    and attrs.get("tvg-country") != "IR":
                continue
            cands.add(stream_url, label, cid, title, logo=attrs.get("tvg-logo"))
            added += 1
        log(f"  {label}: {added} entries")

    try:
        md, section = fetch_text(FREE_TV_MD), "unknown"
        for line in md.splitlines():
            if "<h2>" in line:
                section = re.sub(r"<[^>]+>", "", line).strip()
            row = MD_ROW.match(line)
            if row:
                rest = row.group("rest")
                logo = (re.search(r'src="([^"]+)"', rest) or [None, None])[1]
                epg = (re.search(r"\|\s*([\w.]+)\s*\|?\s*$", rest) or [None, None])[1]
                cands.add(row.group("url"), "free-tv/md", epg,
                          row.group("name").replace(" Ⓢ", "").strip(),
                          logo=logo, freetv_section=section)
        log("  free-tv/md: parsed")
    except Exception as exc:
        log(f"  free-tv/md: unreachable ({exc}), skipped")

    # Streams the project maintains itself, kept in data/curated.json.
    curated = json.loads((HERE / "data" / "curated.json").read_text(encoding="utf-8"))
    for stream in curated.get("streams", []):
        cands.add(stream["url"], "curated", stream.get("channel"), stream.get("title"),
                  user_agent=stream.get("user_agent"), referrer=stream.get("referrer"))

    discovered = 0
    for url, provider, slug, channel_id, height in discover.candidate_urls(curated):
        if canonical_url(url) not in cands.by_key:
            discovered += 1
        # `known_height` is the resolution read from the provider's master playlist. A
        # direct rendition URL is a media playlist and carries no RESOLUTION tag of its
        # own, so without this hint it would look lower quality than it is.
        cands.add(url, f"discovery/{provider}", channel_id, known_height=height or None)
    log(f"  discovery: {discovered} urls no public source lists")

    # Locally defined channels, for services the upstream database does not carry.
    local = curated.get("local_channels", {})
    blocked = tuple(curated.get("blocked_hosts", []))
    records = []
    for rec in cands.by_key.values():
        host = urllib.parse.urlparse(rec["url"]).hostname or ""
        if any(b in host for b in blocked):
            continue
        cid = next((c for c in rec["channel_ids"] if c in channels), None)
        if cid:
            channel = channels[cid]
            main = next((f for f in feeds.get(cid, []) if f.get("is_main")),
                        next(iter(feeds.get(cid, [])), None)) or {}
            rec["db"] = {
                "id": cid,
                "name": channel["name"],
                "alt_names": channel.get("alt_names") or [],
                "country": channel.get("country"),
                "categories": channel.get("categories") or [],
                "network": channel.get("network"),
                "closed": channel.get("closed"),
                "website": channel.get("website"),
                "logo": logos.get(cid),
                "languages": main.get("languages") or [],
                "broadcast_area": main.get("broadcast_area") or [],
                "format": main.get("format"),
            }
        else:
            local_id = next((c for c in rec["channel_ids"] if c in local), None)
            if local_id:
                entry = local[local_id]
                rec["db"] = {
                    "id": local_id,
                    "name": entry.get("en") or local_id,
                    "alt_names": [entry["fa"]] if entry.get("fa") else [],
                    "country": entry.get("country"),
                    "categories": entry.get("categories") or [],
                    "network": None, "closed": None,
                    "website": entry.get("website"),
                    "logo": entry.get("logo"),
                    "languages": entry.get("languages") or [],
                    "broadcast_area": [], "format": entry.get("format"),
                    "local": True,
                }
        records.append(rec)

    records.sort(key=lambda r: r["url"])
    write_json(HERE / "data" / "candidates.json", records)
    identified = {r["db"]["id"] for r in records if "db" in r}
    log(f"{len(records)} candidate urls, {len(identified)} identified channels, "
        f"{sum(1 for r in records if 'db' not in r)} urls without a channel identity")
    return records


if __name__ == "__main__":
    harvest()
