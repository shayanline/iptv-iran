"""Turn probe results into playlists, a machine readable channel list and the README.

Every file under playlists/ and the channel tables in README.md are generated here, so
they are never edited by hand. The hand maintained input is data/curated.json.
"""
import datetime as dt
import re

import identity
import taxonomy
from lib import CANDIDATES, DATA, HERE, log, read_json, write_json

REPO = "shayanline/iptv-iran"
EPG = "https://epgshare01.online/epgshare01/epg_ripper_IR1.xml.gz"
LOGO_BASE = f"https://raw.githubusercontent.com/{REPO}/main/assets/logos"


def mirrored_logos():
    """channel id -> logo URL, taken from the images committed under assets/logos."""
    folder = HERE / "assets" / "logos"
    if not folder.is_dir():
        return {}
    return {path.stem: f"{LOGO_BASE}/{path.name}" for path in sorted(folder.glob("*.*"))}

# The probe runs fortnightly, so a stream has to fail three consecutive runs, roughly six
# weeks, before it is dropped. One bad night on a CDN must not delete a working channel.
GRACE_FAILS = 3
PLAYLISTS = HERE / "playlists"
PERSIAN = re.compile(r"[\u0600-\u06FF]")
TELEWEBION = re.compile(r"telewebion\.ir/(?:\w+/)?([^/]+)/live/(\d{3,4}p)/")


def usable(entry):
    """Is this stream good enough to publish, allowing for the grace period?

    `iran_only` counts as usable: the stream is refusing this checker's location, not
    reporting that it has stopped broadcasting, so it is published as domestic rather
    than deleted. Anything else has to have worked at least once and must still be
    inside its grace period.
    """
    state = entry.get("state")
    if state in ("ok", "iran_only"):
        return True
    return state != "gone" and entry.get("fails", 99) <= GRACE_FAILS and bool(entry.get("last_ok"))


def height_of(entry):
    resolution = str(entry.get("resolution") or "")
    if "x" in resolution:
        tail = resolution.split("x")[1]
        if tail.isdigit():
            return int(tail)
    if entry.get("known_height"):
        return int(entry["known_height"])
    # Fall back to the database's own format string, for example "720p" or "576i".
    match = re.match(r"(\d{3,4})[pi]", str(entry.get("format") or ""))
    return int(match.group(1)) if match else 0


def score(entry):
    """Rank a stream on measured evidence. Higher is better.

        reachable worldwide      100      a stream that answers beats a sharper one that does not
        uptime history        up to 30    successful checks over total, scaled by how many exist
        no custom headers        25       Referer or User-Agent only works in EXTVLCOPT clients
        resolution            up to 24    measured from the master playlist, not from a label
        adaptive bitrate          8       more than one rendition lets a client adapt
        response time         up to 3     tie break only
        malformed manifest      minus 40  breaks strict clients, so a clean equivalent wins

    The ordering is deliberate. A playlist is judged on whether channels open, so proven
    reliability outranks peak resolution, and a stream that needs custom headers is worth
    less than a plain one because many clients ignore `#EXTVLCOPT` entirely.
    """
    if entry.get("state") == "ok":
        reach = 100
    elif entry.get("state") == "iran_only":
        reach = 40
    else:
        reach = 0

    # Uptime is only meaningful once there is history, so a single check is treated as
    # neutral rather than as a perfect record.
    checks = entry.get("checks", 0)
    uptime = entry.get("uptime", 0) if checks >= 2 else 0.75
    confidence = min(checks, 8) / 8

    compatible = 0 if (entry.get("referrer") or entry.get("user_agent")) else 25
    # Scaled against 1080 rather than 2160, so the 480 to 1080 range where almost every
    # channel sits is properly separated, with a small bonus above it.
    height = height_of(entry)
    resolution_points = min(height, 1080) / 1080 * 20 + (4 if height > 1080 else 0)
    adaptive = 8 if (entry.get("variants") or 0) > 1 else 0
    # A manifest that violates the spec plays in ffmpeg and VLC but stalls in stricter
    # clients, so a clean equivalent is always preferred when one exists.
    defective = -40 if entry.get("defects") else 0
    # Capped low on purpose: latency breaks ties, it never outweighs a resolution step.
    latency = max(0, 3 - (entry.get("ms") or 3000) / 1500)

    return round(reach + uptime * confidence * 30 + compatible
                 + resolution_points + adaptive + latency + defective, 3)


def collect():
    candidates = read_json(CANDIDATES, [])
    status = (read_json(DATA / "status.json", {}) or {}).get("streams", {})
    curated = read_json(DATA / "curated.json", {})
    overrides = curated.get("channels", {})
    worker_base = (curated.get("worker") or {}).get("base", "").rstrip("/")
    # Logos are mirrored into the repository by scripts/logos.py and served from the same
    # origin as the playlists, so the mapping is simply whatever is on disk.
    logos = mirrored_logos()

    channels, key_to_id = {}, {}
    for record in candidates:
        entry = status.get(record["url"])
        if not entry or not usable(entry):
            continue
        db = record.get("db") or {}
        cid = db.get("id")
        if not cid or db.get("closed"):
            continue

        # One channel can arrive under more than one id across sources. The normalised
        # name key merges those, and the first id seen becomes the canonical one.
        merge_key = identity.channel_key(None, db.get("name") or cid, db.get("country"))
        if merge_key and merge_key in key_to_id and key_to_id[merge_key] != cid:
            cid = key_to_id[merge_key]
        elif merge_key:
            key_to_id.setdefault(merge_key, cid)

        override = overrides.get(cid, {})
        channel = channels.get(cid)
        if channel is None:
            channel = channels[cid] = {
                "id": cid,
                "name_en": override.get("en") or db.get("name") or cid,
                "name_fa": override.get("fa") or next(
                    (a for a in db.get("alt_names", []) if PERSIAN.search(a)), ""),
                "logo": logos.get(cid, ""),
                "country": db.get("country"),
                "languages": db.get("languages") or [],
                "website": db.get("website") or "",
                "category": taxonomy.classify(cid, db.get("categories") or [], curated),
                "province_en": override.get("province_en", ""),
                "province_fa": override.get("province_fa", ""),
                "note_en": override.get("note_en", ""),
                "note_fa": override.get("note_fa", ""),
                "source_local": bool(db.get("local")),
                "streams": [],
            }
        channel["streams"].append({
            # When a master advertises renditions it does not actually serve, the best
            # rendition that answered is published instead. Clients pick the highest
            # bitrate first, or downshift into a missing one, and stop either way.
            "url": entry.get("variant_url") or entry.get("final_url") or record["url"],
            "state": entry["state"],
            "resolution": entry.get("resolution"),
            "height": height_of({**entry, "format": db.get("format"),
                                 "known_height": record.get("known_height")}),
            "bandwidth": entry.get("bandwidth"),
            "variants": entry.get("variants"),
            "kind": entry.get("kind"),
            "ms": entry.get("ms"),
            "uptime": entry.get("uptime"),
            "checks": entry.get("checks", 0),
            "user_agent": record.get("user_agent"),
            "referrer": record.get("referrer"),
            "sources": record.get("sources", []),
            "first_seen": entry.get("first_seen"),
            "last_ok": entry.get("last_ok"),
            "format": db.get("format"),
            "defects": entry.get("defects") or [],
            "hazards": entry.get("hazards") or [],
            "media_sequence": entry.get("media_sequence"),
            "manifest_bytes": entry.get("manifest_bytes"),
            "score": score({**entry, "format": db.get("format"),
                            "known_height": record.get("known_height"),
                            "user_agent": record.get("user_agent"),
                            "referrer": record.get("referrer")}),
        })

    for channel in channels.values():
        channel["streams"] = identity.dedupe_streams(
            sorted(channel["streams"], key=lambda s: -s["score"]))
        best = channel["streams"][0]
        # Three distinct situations, which were previously collapsed into two. A channel
        # with no working stream is not the same as one restricted to Iran: it is one whose
        # streams have started failing and is inside its grace period, still listed because
        # it worked recently. Calling that "Iran only" sends viewers to the wrong playlist.
        states = {s["state"] for s in channel["streams"]}
        if "ok" in states:
            channel["reach"] = "global"
        elif "iran_only" in states:
            channel["reach"] = "iran-only"
        else:
            channel["reach"] = "failing"
        channel["height"] = max(s["height"] for s in channel["streams"])
        channel["resolution"] = next((s["resolution"] for s in channel["streams"]
                                     if s.get("resolution")), None)
        channel["quality"] = taxonomy.quality_tag(channel["height"])
        channel["best"] = best
        # The best stream a limited client can actually handle, if the channel has one.
        channel["compat"] = next((s for s in channel["streams"]
                                  if s["state"] == "ok" and not s["hazards"] and not s["defects"]),
                                 None)
        # What the advertised compatibility playlist may use: no worker involved.
        channel["compat_public"] = channel["compat"]
        # A deployed rewriter can rescue a channel whose only streams carry hazards, by
        # reshaping the manifest into something a basic parser accepts.
        if channel["compat"] is None and worker_base:
            rescued = next((s for s in channel["streams"]
                            if s["state"] == "ok" and TELEWEBION.search(s["url"])), None)
            if rescued:
                match = TELEWEBION.search(rescued["url"])
                channel["compat"] = {**rescued,
                                     "url": f"{worker_base}/{match.group(1)}/{match.group(2)}",
                                     "via": "worker"}
        channel["tags"] = taxonomy.tags(channel)

    # Channels listed under `order` in curated.json lead their category, in that order.
    # The rest follow alphabetically.
    pinned = {cid: i for i, cid in enumerate(curated.get("order", []))}
    ordered = sorted(channels.values(),
                     key=lambda c: (taxonomy.ORDER.get(c["category"], 99),
                                    pinned.get(c["id"], len(pinned)),
                                    c["name_en"].lower()))
    log(f"{len(ordered)} channels publishable "
        f"({sum(1 for c in ordered if c['reach'] == 'global')} global, "
        f"{sum(1 for c in ordered if c['reach'] == 'iran-only')} Iran only, "
        f"{sum(1 for c in ordered if c['reach'] == 'failing')} in the grace period), "
        f"{sum(len(c['streams']) for c in ordered)} streams after dedup")
    return ordered


def display_name(channel, lang):
    """Channel title for a playlist entry, with the resolution tag appended."""
    if lang == "en":
        base = channel["name_en"]
    elif lang == "fa":
        base = channel["name_fa"] or channel["name_en"]
    else:
        base = f'{channel["name_en"]} | {channel["name_fa"]}' if channel["name_fa"] \
            else channel["name_en"]
    if channel["quality"] in ("HD", "FHD", "4K"):
        base += f' {channel["quality"]}'
    if channel["reach"] == "iran-only":
        base += " [IR]"   # only a genuine geographic restriction earns the tag
    return base


def extinf(channel, stream, lang):
    # The group follows the same rule as the channel name, so the bilingual playlist is
    # bilingual throughout rather than Persian titles filed under English headings.
    labels = taxonomy.LABELS[channel["category"]]
    if lang == "en":
        group = labels["en"]
    elif lang == "fa":
        group = labels["fa"]
    else:
        group = f'{labels["en"]} | {labels["fa"]}' if labels.get("fa") else labels["en"]
    parts = [
        f'#EXTINF:-1 tvg-id="{channel["id"]}"',
        f'tvg-name="{channel["name_en"]}"',
        f'tvg-logo="{channel["logo"]}"',
        f'group-title="{group}"',
    ]
    if channel["languages"]:
        parts.append(f'tvg-language="{";".join(channel["languages"])}"')
    if channel["quality"]:
        parts.append(f'tvg-quality="{channel["quality"]}"')
    lines = [" ".join(parts) + f",{display_name(channel, lang)}"]
    if stream.get("user_agent"):
        lines.append(f'#EXTVLCOPT:http-user-agent={stream["user_agent"]}')
    if stream.get("referrer"):
        lines.append(f'#EXTVLCOPT:http-referrer={stream["referrer"]}')
    lines.append(stream["url"])
    return "\n".join(lines)


def write_playlist(path, channels, note, lang="both", all_streams=False, use_compat=False,
                   field="compat"):
    lines = [f'#EXTM3U x-tvg-url="{EPG}"', f"# {note}",
             f"# generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC by {REPO}"]
    count = 0
    for channel in channels:
        if all_streams:
            chosen = channel["streams"]
        else:
            chosen = [channel[field] if use_compat else channel["best"]]
        for stream in chosen:
            lines.append(extinf(channel, stream, lang))
            count += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"  {path.relative_to(HERE)}: {count} entries")


def build_playlists(channels):
    # A failing channel was reachable worldwide when it last worked, so it stays in the
    # worldwide list for its grace period rather than being hidden or mislabelled.
    worldwide = [c for c in channels if c["reach"] in ("global", "failing")]
    domestic = [c for c in channels if c["reach"] == "iran-only"]

    # Channels that offer a stream free of the shapes limited clients choke on.
    # `compat_public` never routes through the worker, so the playlists named in the
    # README cannot generate traffic against someone's request budget. The worker backed
    # list is written separately, below, and is deliberately not advertised.
    compatible = [c for c in channels if c.get("compat_public")]

    for lang, folder in (("both", PLAYLISTS), ("en", PLAYLISTS / "en"), ("fa", PLAYLISTS / "fa")):
        write_playlist(folder / "iran.m3u", channels,
                       "Every channel, one stream each. [IR] needs an Iranian IP address.", lang)
        write_playlist(folder / "iran-global.m3u", worldwide,
                       "Channels that play from anywhere in the world.", lang)
        write_playlist(folder / "iran-domestic.m3u", domestic,
                       "Channels served only to Iranian IP addresses.", lang)
        write_playlist(folder / "iran-all-streams.m3u", channels,
                       "Every working stream, backups included, best first.", lang,
                       all_streams=True)
        write_playlist(folder / "iran-compat.m3u", compatible,
                       "For smart TV apps and other limited players. Only streams whose "
                       "manifests stay within what a basic HLS parser handles.", lang,
                       use_compat=True, field="compat_public")

    # Unlisted. Every channel a limited player can handle once a manifest rewriting
    # worker is in front of the awkward ones. Kept out of the README on purpose: it is
    # backed by a personal Cloudflare Worker with a finite request budget, so the URL is
    # shared deliberately rather than advertised.
    via_worker = [c for c in channels if c.get("compat")]
    if any(c["compat"].get("via") == "worker" for c in via_worker):
        for lang, folder in (("both", PLAYLISTS / "unlisted"),
                             ("en", PLAYLISTS / "unlisted" / "en"),
                             ("fa", PLAYLISTS / "unlisted" / "fa")):
            write_playlist(folder / "iran-tv.m3u", via_worker,
                           "Unlisted. Every channel a limited player can handle, with the "
                           "awkward manifests reshaped by a worker.", lang,
                           use_compat=True, field="compat")

    for cid, *_ in taxonomy.CATEGORIES:
        members = [c for c in channels if c["category"] == cid]
        if members:
            write_playlist(PLAYLISTS / "categories" / f"{cid}.m3u", members,
                           f'{taxonomy.LABELS[cid]["en"]} only.')


def build_readme(channels):
    from readme import render
    text = render(channels)
    (HERE / "README.md").write_text(text, encoding="utf-8")
    log(f"  README.md: {len(text.splitlines())} lines")


def main():
    channels = collect()
    build_playlists(channels)
    write_json(DATA / "channels.json",
               [{k: v for k, v in c.items() if k != "best"} for c in channels])
    build_readme(channels)


if __name__ == "__main__":
    main()
