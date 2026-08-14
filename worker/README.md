# Manifest rewriter

A Cloudflare Worker that reshapes Telewebion's HLS manifests for players that cannot read
them, chiefly the HLS parsers built into smart TVs.

## Why

Telewebion carries IRIB's channels and is the only source for them reachable from outside
Iran. Its media playlists are valid HLS, and one number in them is larger than a television
can hold.

`EXT-X-MEDIA-SEQUENCE` is sixteen digits, for example `1786395804195022`, because the
packager derives it from a microsecond timestamp. Samsung's AVPlay keeps that field in a
**signed** 32 bit integer, so anything above 2,147,483,647 overflows and its window
arithmetic collapses: it plays one segment, shows a frame and stops. Telewebion's value is
about 831,000 times the limit.

Measured on a Samsung QE55S90D running Tizen 9.0, by serving it manifests built from this
same stream with one property changed at a time:

| Sequence in the manifest | What AVPlay did |
|--:|:--|
| 2,147,483,000, just under 2³¹ | played, and reported the window correctly |
| 2,147,484,000, just over 2³¹ | reported the whole stream as 2000ms |
| 4,294,966,000, just under 2³² | same failure, so the field is signed, not unsigned |

**The size of the playlist is not the problem.** The same test served 3600 segments and
813KB with a small sequence and it played, as did 600 segments and 120. Trimming the window
is therefore not a fix, and a shorter window on its own would not have helped anything: it
is here because it keeps this Worker's CPU and its responses small.

|  | Upstream | Rewritten |
|:--|--:|--:|
| Manifest size | 651,688 bytes | 18,082 bytes |
| Segments listed | 3,600 | 75 |
| Sequence digits | 16 | 9 |

The upstream figures are today's. They were 1,800 segments and 318KB when this was written,
so Telewebion doubled its window at some point without telling anybody.

VLC, ffmpeg, mpv and Kodi read the original perfectly well, so they are redirected to it
rather than served a rewrite, and stop costing anything. Browsers are deliberately not:
hls.js copes with the long sequence, being JavaScript, but Telewebion's
`Access-Control-Allow-Origin` names one site, so a page needs the header this Worker adds.

## Cost

Only the manifest passes through the Worker. Segment URLs are rewritten to absolute
Telewebion addresses, so video goes straight from the origin to the player and never
touches Cloudflare. Video is almost all of the traffic, so this is the whole game.

Cloudflare bills per incoming request. `fetch()` subrequests and the Cache API are free.
`EXT-X-TARGETDURATION` is an upper bound rather than a promise, so declaring a larger value
than the real two seconds slows the player's reload loop. How much was assumed here and is
now measured: **AVPlay comes back about twice per target duration, not once**, and starts
playback about three target durations behind the live edge.

| Target | Reload interval | Requests per viewer-hour | Viewer-hours/day on the free 100k | Behind live |
|--:|--:|--:|--:|--:|
| 2s, Telewebion's own | ~1s | 3,600 | 27 | 6s |
| 12s, the previous default | 6.4s | 562 | 178 | 33s |
| **20s, the default here** | **9.1s** | **394** | **253** | **58s** |
| 30s | 12.8s | 281 | 355 | 88s |

Counted over 64 seconds of real playback each, on the set. 253 viewer-hours a day is about
ten people watching continuously.

The deployed version was then measured against the same television with `wrangler tail`
running: **7 invocations in 68 seconds**, which is 371 requests per viewer-hour, playback
57 seconds behind the live edge, and 2 to 3 ms of CPU per invocation against the free plan's
10 ms limit.

Two things that would have bought fewer requests without the added delay do not work, and
both were tried on the television rather than reasoned about:

- **`EXT-X-START:TIME-OFFSET` is ignored.** Playback began 33.6s behind the edge with and
  without it, which is three targets either way.
- **`Cache-Control: max-age` is ignored** for playlist reloads: ten requests in 64 seconds
  with `max-age=10`, and ten with `no-cache`.

So the request rate and the delay behind live are welded together, and 20 seconds is the
compromise: a third fewer requests than before, and a viewer about a minute behind the
broadcast. Nobody notices that on a channel and everybody notices it during a football
match, so 12 is the number to go back to if that matters more than the budget.

The rewritten manifest is cached at the edge for eight seconds. That does not reduce billed
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
