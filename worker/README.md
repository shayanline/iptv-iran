# Telewebion manifest rewriter

This optional Cloudflare Worker reshapes Telewebion HLS media playlists for players that cannot handle their large media sequence values. Samsung and compatible desktop players load video segments directly from Telewebion, while browser JavaScript players use the restricted segment proxy required for CORS.

> **Status:** This repository publishes the source code and deployment instructions for people who need the workaround. The project does not deploy the Worker or route its published playlists through one.

## Requirements

- Use a current Node.js release and npm that Cloudflare Wrangler supports.
- Use a Cloudflare account when you intend to deploy or inspect a live Worker.
- Use a television or player affected by the Telewebion manifest problem when validating device behaviour.

The Worker source has no runtime package dependencies. `npx wrangler` may download Wrangler when it is not installed locally, so review the package and version before allowing that installation.

## Why the rewrite exists

Telewebion carries IRIB channels and is the only project source for many of them that is reachable outside Iran. Its media playlists are valid HLS, but `EXT-X-MEDIA-SEQUENCE` can contain a sixteen digit value such as `1786395804195022` because the packager derives it from a microsecond timestamp.

Samsung AVPlay stores that field in a signed 32 bit integer. Values above 2,147,483,647 overflow its window arithmetic, which causes one segment to play before the picture stops. This behaviour was measured on a Samsung QE55S90D running Tizen 9.0 by changing one manifest property at a time.

| Sequence in the manifest | Observed AVPlay behaviour |
|--:|:--|
| 2,147,483,000, just below 2³¹ | Playback continued and the window was reported correctly. |
| 2,147,484,000, just above 2³¹ | AVPlay reported the complete stream as 2000 ms. |
| 4,294,966,000, just below 2³² | The same failure occurred, which confirms a signed field. |

The playlist length does not cause the playback failure. AVPlay handled 3,600 segments and an 813 KB manifest when the sequence value was small. The Worker still keeps a short window because smaller manifests reduce its CPU use and response size.

| Measurement | Upstream | Rewritten |
|:--|--:|--:|
| Manifest size during the recorded test | 651,688 bytes | 18,082 bytes |
| Listed segments | 3,600 | 75 |
| Sequence digits | 16 | 9 |

## Request flow

1. The player requests `/<channel>/<rendition>` from the Worker.
2. VLC, ffmpeg, mpv, Kodi, GStreamer, MPlayer, and native browser media requests receive a temporary redirect to Telewebion because they can use the original stream.
3. Browser requests made through hls.js and Samsung AVPlay requests stay on the rewritten path.
4. The Worker fetches the upstream media playlist, keeps about 150 seconds of segments, and replaces the media sequence with a safe nine digit value.
5. Samsung AVPlay receives absolute Telewebion segment URLs. Browser JavaScript players receive restricted Worker segment URLs so their media responses also include browser CORS headers.

The Worker validates channel slugs and rendition labels before building the upstream address.

## Browser CORS limitation

The final Telewebion playlist and segment responses allow the Telewebion website origin rather than an arbitrary viewer origin. VLC and native media playback can still load those responses, but browser JavaScript players such as hls.js are blocked by the browser.

The Worker adds `Access-Control-Allow-Origin: *` to rewritten playlists and proxies segments requested by browser JavaScript clients. The segment route accepts only HTTPS `.ts` files on `telewebion.ir` and `telewebion.net` hosts. Samsung AVPlay and compatible desktop players continue loading segments directly from Telewebion.

## Cost and latency

Cloudflare bills Workers by incoming requests. Samsung AVPlay sends only playlist reloads through the Worker, while Telewebion receives its video segment requests. Browser JavaScript playback also sends every segment through the Worker to satisfy CORS, so that path consumes substantially more requests and transfers the video through the deployment. Edge caching reduces repeated origin parsing but does not remove billed incoming requests.

Samsung AVPlay reloads a live playlist about twice per declared `EXT-X-TARGETDURATION` and begins playback about three target durations behind the live edge. These values were measured during 64 seconds of real playback on the television.

| Declared target | Reload interval | Requests per viewer hour | Viewer hours each day within 100,000 requests | Delay behind live |
|--:|--:|--:|--:|--:|
| 2 seconds, Telewebion's value | About 1 second | 3,600 | 27 | 6 seconds |
| 12 seconds | 6.4 seconds | 562 | 178 | 33 seconds |
| **20 seconds, current default** | **9.1 seconds** | **394** | **253** | **58 seconds** |
| 30 seconds | 12.8 seconds | 281 | 355 | 88 seconds |

A deployed test recorded 7 invocations over 68 seconds, which equals 371 requests per viewer hour. Playback stayed 57 seconds behind live and each invocation used 2 to 3 ms of CPU against the recorded free plan limit of 10 ms.

AVPlay ignored `EXT-X-START:TIME-OFFSET` and playlist `Cache-Control: max-age` during device tests. The 20 second target therefore reduces requests by accepting about one minute of live delay. Change `TARGET_DURATION` to 12 when lower sports latency matters more than request capacity.

The rewritten response is cached at the edge for eight seconds. Upstream fetches use a four second Cloudflare cache lifetime, which lets concurrent viewers share origin work.

## Test and compile

Run the focused Node.js test from the repository root.

```bash
node --test tests/test_worker.mjs
```

Compile the Worker without uploading it.

```bash
cd worker
npx wrangler deploy --dry-run
```

## Deploy your own Worker

Authenticate and deploy from the `worker` directory.

```bash
npx wrangler login --use-keyring
npx wrangler deploy
```

This repository does not store or use the resulting deployment address. Add routes from your own deployment only to playlists that you operate.

## Use routes directly

Telewebion routes use `/<channel>/<rendition>`. Channel slugs are listed under `discovery.telewebion` in `data/curated.json`.

```text
https://<worker>/<channel>/<rendition>
https://<worker>/tv1/1080p
https://<worker>/irinn/1080p
https://<worker>/nasim/720p
```

## Data and privacy

The Worker defines no KV, D1, R2, Durable Object, or other persistent storage binding. Its application code stores no account, cookie, viewing history, credential, or complete video segment. Cloudflare's Cache API temporarily stores rewritten manifests for eight seconds, and Cloudflare can cache the upstream manifest for four seconds.

Observability is enabled in `wrangler.jsonc`. Cloudflare Workers Logs therefore records invocation information such as request and response metadata. No sampling rate is configured, so Cloudflare's default rate applies. The Worker emits no custom application logs. Cloudflare documents plan dependent log retention, which is currently three days for Workers Free and seven days for Workers Paid. Review [Cloudflare Workers Logs documentation](https://developers.cloudflare.com/workers/observability/logs/workers-logs/) before deployment and change the observability configuration when your privacy or retention requirements differ.

Cloudflare receives requests to the Worker and processes segment responses for browser JavaScript playback. Telewebion receives the upstream playlist and segment requests. Each service can receive normal network metadata such as IP address, request time, path, and `User-Agent`. Cloudflare processes its service data under the [Cloudflare Privacy Policy](https://www.cloudflare.com/privacypolicy/), while Telewebion's policies apply to its origin traffic.

Wrangler normally stores OAuth access and refresh tokens in a plaintext TOML file under its global configuration directory, typically `~/.config/.wrangler/config/default.toml`. The `--use-keyring` option stores credentials in an encrypted file beside it and keeps the encryption key in the operating system keychain. Run `npx wrangler whoami` to confirm the active storage location, and review [Wrangler authentication guidance](https://developers.cloudflare.com/workers/wrangler/commands/general/#login) when changing this setting. Never put API tokens, account credentials, or private routes in `wrangler.jsonc`, source files, logs, screenshots, or issues.

## Inspect a deployment

```bash
npx wrangler tail
npx wrangler deployments list
```

`wrangler tail` exposes live request logs from your deployment, so redact IP addresses, paths, and unrelated request metadata before sharing its output.

Use [SUPPORT.md](../SUPPORT.md) for project support and [SECURITY.md](../SECURITY.md) for private vulnerability reporting.
