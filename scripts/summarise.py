"""Print a short markdown report of the last refresh, for the Actions run summary."""
from collections import Counter

import taxonomy
from lib import DATA, read_json

GRACE = 3


def main():
    status = (read_json(DATA / "status.json", {}) or {})
    streams = status.get("streams", {})
    channels = read_json(DATA / "channels.json", [])
    states = Counter(entry.get("state") for entry in streams.values())

    print(f"## Refresh {status.get('generated_at', 'unknown')}\n")
    print(f"- **{len(channels)} channels published**, "
          f"{sum(1 for c in channels if c['reach'] == 'global')} reachable worldwide, "
          f"{sum(1 for c in channels if c['reach'] == 'iran-only')} Iran only")
    print(f"- **{len(streams)} stream URLs tracked**: "
          + ", ".join(f"{count} {state}" for state, count in states.most_common()))

    failing = [(url, e) for url, e in streams.items() if e.get("fails", 0) > 0
               and e.get("state") not in ("ok", "iran_only")]
    about_to_go = [u for u, e in failing if e.get("fails", 0) >= GRACE]
    if about_to_go:
        print(f"- **{len(about_to_go)} streams past the grace period** and now dropped")

    print("\n### Channels per category\n")
    print("| Category | Channels |")
    print("|:--|--:|")
    counts = Counter(c["category"] for c in channels)
    for cid, en, *_ in taxonomy.CATEGORIES:
        if counts.get(cid):
            print(f"| {en} | {counts[cid]} |")

    if failing:
        print(f"\n<details><summary>{len(failing)} failing stream URLs</summary>\n")
        for url, entry in sorted(failing, key=lambda kv: -kv[1].get("fails", 0))[:60]:
            print(f"- `{entry.get('reason', '?')}` after {entry.get('fails')} run(s): {url}")
        print("\n</details>")


if __name__ == "__main__":
    main()
