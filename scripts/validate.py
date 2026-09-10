"""Check the generated tree before it is published.

build.py writes every file under playlists/ from one channel list in a single pass, so
the published files share properties that hold on every honest run. A refresh commits to
main unattended, which means nothing else is looking, and the failure that prompted this
script was silent: two runs were spliced together, leaving three language variants of one
playlist carrying 666, 667 and 667 streams while data/channels.json described 662.

Every rule here is an invariant of a single build, so a tree assembled from more than one
fails, and so does a generator that quietly stops agreeing with its own data. The
expectations are re-derived from data/channels.json rather than read back from the files,
because a check that trusts the output cannot catch the output being wrong.
"""
import sys

import readme
import taxonomy
from lib import DATA, HERE, log, parse_m3u, read_json

PLAYLISTS = HERE / "playlists"
LANG_FOLDERS = ("", "en", "fa")
CATALOGUES = ((HERE / "CHANNELS.md", "en"), (HERE / "CHANNELS.fa.md", "fa"))

# What each published list should contain, in order, mirroring build.build_playlists.
EXPECTED = {
    "iran.m3u":
        lambda cs: [next(s["url"] for s in c["streams"] if not s.get("unlisted_only"))
                    for c in cs],
    "iran-all-streams.m3u":
        lambda cs: [s["url"] for c in cs for s in c["streams"]
                    if not s.get("unlisted_only")],
    "iran-compat.m3u":
        lambda cs: [c["compat_public"]["url"] for c in cs if c.get("compat_public")],
}


def read_entries(path):
    """Return (entries, declared) where declared counts the #EXTINF lines in the file.

    parse_m3u skips an #EXTINF that has no URL after it, so comparing the two numbers is
    what catches a truncated write rather than a merely surprising one.
    """
    text = path.read_text(encoding="utf-8")
    declared = sum(1 for line in text.splitlines() if line.startswith("#EXTINF"))
    return list(parse_m3u(text)), declared


def quality_in_title(attrs, title):
    """Is the resolution repeated in the name, when tvg-quality already carries it?

    Compared against this entry's own tvg-quality rather than a list of words, so a
    channel genuinely called IRIB UHD is left alone and only a repeat is reported.
    """
    quality = attrs.get("tvg-quality")
    return bool(quality) and title.removesuffix("[IR]").rstrip().endswith(f" {quality}")


def playlist_files():
    return sorted(PLAYLISTS.rglob("*.m3u"))


def difference(found, expected, reference="the channel data"):
    """Describe how two stream sequences differ, pointing at the first divergence.

    Equal lengths carrying different streams is the shape a spliced tree takes, so the
    position and the two urls matter more than the totals.
    """
    if len(found) != len(expected):
        return f"holds {len(found)} streams where {reference} implies {len(expected)}"
    for position, (got, want) in enumerate(zip(found, expected), 1):
        if got != want:
            return (f"holds {len(found)} streams, but number {position} is {got} "
                    f"where {reference} implies {want}")
    return ""


def check_structure():
    problems = []
    for path in playlist_files():
        entries, declared = read_entries(path)
        if len(entries) != declared:
            problems.append(f"{path.relative_to(HERE)}: {declared} #EXTINF lines but "
                            f"{len(entries)} have a url after them")
        for attrs, title, _ in entries:
            if not title:
                problems.append(f"{path.relative_to(HERE)}: an entry has no title")
            elif not attrs.get("tvg-id"):
                problems.append(f"{path.relative_to(HERE)}: {title} has no tvg-id")
            elif not attrs.get("group-title"):
                problems.append(f"{path.relative_to(HERE)}: {title} has no group-title")
    return problems


def check_against_channels(channels):
    """Each published list must hold exactly what the channel data implies."""
    problems = []
    for name, expected_of in EXPECTED.items():
        expected = expected_of(channels)
        for folder in LANG_FOLDERS:
            path = PLAYLISTS / folder / name
            if not path.exists():
                problems.append(f"{path.relative_to(HERE)}: missing")
                continue
            found = [url for _, _, url in read_entries(path)[0]]
            if found != expected:
                problems.append(f"{path.relative_to(HERE)}: {difference(found, expected)}")
    return problems


def check_visibility(channels):
    hidden = {s["url"] for c in channels for s in c["streams"] if s.get("unlisted_only")}
    problems = []
    for path in playlist_files():
        if "unlisted" in path.parts:
            continue
        leaked = hidden & {url for _, _, url in read_entries(path)[0]}
        if leaked:
            problems.append(f"{path.relative_to(HERE)}: contains an unlisted stream")
    return problems


def check_metadata(channels):
    return [f'{channel["id"]}: missing Persian display name'
            for channel in channels if not channel.get("name_fa")]


def check_variants_agree():
    """The language variants differ only in wording, never in which streams they carry."""
    problems = []
    for name in EXPECTED:
        by_folder = {}
        for folder in LANG_FOLDERS:
            path = PLAYLISTS / folder / name
            if path.exists():
                by_folder[folder or "bilingual"] = [url for _, _, url in read_entries(path)[0]]
        bilingual = by_folder.get("bilingual")
        for folder, urls in by_folder.items():
            if folder != "bilingual" and bilingual is not None and urls != bilingual:
                problems.append(f"{name}: the {folder} variant "
                                + difference(urls, bilingual, "the bilingual list"))
    return problems


def check_categories(channels):
    """Category lists partition the channels, so every channel appears in exactly one."""
    problems = []
    covered = []
    for cid, *_ in taxonomy.CATEGORIES:
        expected = [next(s["url"] for s in c["streams"] if not s.get("unlisted_only"))
                    for c in channels if c["category"] == cid]
        path = PLAYLISTS / "categories" / f"{cid}.m3u"
        if not expected:
            if path.exists():
                problems.append(f"{path.relative_to(HERE)}: no channels in this category")
            continue
        if not path.exists():
            problems.append(f"playlists/categories/{cid}.m3u: missing, {len(expected)} channels")
            continue
        found = [url for _, _, url in read_entries(path)[0]]
        if found != expected:
            problems.append(f"{path.relative_to(HERE)}: {difference(found, expected)}")
        covered += expected
    if len(covered) != len(channels):
        problems.append(f"the category lists cover {len(covered)} channels, "
                        f"data/channels.json has {len(channels)}")
    return problems


def check_catalogues(channels):
    problems = []
    for path, lang in CATALOGUES:
        if not path.exists():
            problems.append(f"{path.relative_to(HERE)}: missing")
            continue
        expected = readme.render_catalog(channels, lang)
        if path.read_text(encoding="utf-8") != expected:
            problems.append(f"{path.relative_to(HERE)}: differs from the channel data")
    return problems


def check_titles():
    """The resolution lives in tvg-quality, so a title must not repeat it."""
    problems = []
    for path in playlist_files():
        repeats = [title for attrs, title, _ in read_entries(path)[0]
                   if quality_in_title(attrs, title)]
        if repeats:
            problems.append(f"{path.relative_to(HERE)}: {len(repeats)} titles repeat the "
                            f"quality already in tvg-quality, such as {repeats[0]!r}")
    return problems


def main():
    channels = read_json(DATA / "channels.json", [])
    if not channels:
        log("data/channels.json is empty or missing, nothing to validate")
        raise SystemExit(1)

    public = [c for c in channels if c.get("public", True)]
    missing_names = check_metadata(channels)
    if missing_names:
        log(f"metadata warning: {len(missing_names)} channel(s) lack a Persian display name")
    problems = (check_structure() + check_against_channels(public)
                + check_visibility(channels) + check_variants_agree() + check_categories(public)
                + check_catalogues(public) + check_titles())
    if problems:
        log(f"the generated tree is not consistent, {len(problems)} problem(s):")
        for problem in problems:
            log(f"  {problem}")
        raise SystemExit(1)

    streams = sum(len(c["streams"]) for c in channels)
    log(f"generated tree is consistent: {len(public)} public channels, "
        f"{len(channels)} total, {streams} streams, {len(playlist_files())} playlists "
        "all agreeing with data/channels.json")


if __name__ == "__main__":
    sys.exit(main())
