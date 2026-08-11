# Manifest rewriter

A Cloudflare Worker that reshapes Telewebion's HLS manifests for players that cannot read
them, chiefly the HLS parsers built into smart TVs.

## Why

Telewebion carries IRIB's channels and is the only source for them reachable from outside
Iran. Its media playlists are valid HLS but unusual in two ways:

- `EXT-X-MEDIA-SEQUENCE` is sixteen digits, for example `1786395804195022`, which is about
  415,000 times larger than an unsigned 32 bit counter holds.
- Each playlist carries a one hour window: 1800 segments, roughly 318 KB, re-fetched every
  two seconds.

VLC, ffmpeg and Kodi cope with both. Several TV apps load one segment, show a frame and
then stall. The rewrite produces a nine digit sequence and a one minute window, about 45
times smaller.

|  | Upstream | Rewritten |
|:--|--:|--:|
| Manifest size | 325,888 bytes | 7,282 bytes |
| Segments listed | 1,800 | 30 |
| Sequence digits | 16 | 9 |

## Cost

Only the manifest passes through the Worker. Segment URLs are rewritten to absolute
Telewebion addresses, so video goes straight from the origin to the player and never
touches Cloudflare. Video is almost all of the traffic, so this is the whole game.

Cloudflare bills per incoming request. `fetch()` subrequests and the Cache API are free.
A player reloads a live playlist about once per `EXT-X-TARGETDURATION`, and that value is
an upper bound rather than a promise, so raising it slows the reload loop:

| Target duration | Requests per viewer-hour | Viewer-hours/day on the free 100k |
|--:|--:|--:|
| 2s, Telewebion's own | 1,800 | 55 |
| **12s, the default here** | **300** | **333** |
| 20s | 180 | 555 |

333 viewer-hours a day is about fourteen people watching continuously. Measured CPU is
0.67 ms against the free plan's 10 ms limit.

The rewritten manifest is cached at the edge for a few seconds. That does not reduce billed
requests, but it means many viewers of one channel cause a single origin fetch, and most
invocations return from cache having done no parsing at all.

## Deploy

```bash
npx wrangler login
npx wrangler deploy
```

Then put the deployed URL in [`../data/curated.json`](../data/curated.json):

```json
"worker": { "base": "https://iptv-iran-telewebion.<subdomain>.workers.dev" }
```

The next build writes `playlists/unlisted/iran-tv.m3u`, which routes the affected channels
through the Worker. That playlist is deliberately absent from the project README: it is
backed by one person's request budget, so the URL is meant to be shared deliberately rather
than advertised. The playlists the README does name never touch it.

## Use

```
https://<worker>/<channel>/<rendition>

https://<worker>/tv1/1080p
https://<worker>/irinn/1080p
https://<worker>/nasim/720p
```

Channel slugs are the Telewebion ones listed under `discovery.telewebion` in
`data/curated.json`.

## Watching it

```bash
npx wrangler tail                  # live logs
npx wrangler deployments list      # what is running
```
