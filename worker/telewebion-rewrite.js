/**
 * Telewebion manifest rewriter, for players that cannot handle the original.
 *
 * WHY THIS EXISTS
 * Telewebion publishes IRIB's channels, and it is the only source for them reachable
 * from outside Iran. Its media playlists are valid HLS but unusual in two ways that stop
 * the HLS parsers built into smart TVs:
 *
 *   1. EXT-X-MEDIA-SEQUENCE is sixteen digits, for example 1786395804195022. That is
 *      415,000 times larger than an unsigned 32 bit counter can hold, so a parser that
 *      keeps the sequence in a 32 bit integer loses track of which segment comes next.
 *   2. The playlist carries a one hour window: 1800 segments with 170 character names,
 *      about 318 KB, re-fetched every two seconds.
 *
 * Desktop players cope with both. Several TV apps load one segment, show a frame, and
 * then stall. Rewriting fixes both: the sequence is reduced to nine digits and the window
 * is trimmed to about a minute, which is roughly 110 times smaller.
 *
 * COST CONTROL, THE POINT OF THE DESIGN
 * Only the media playlist passes through this Worker. Segment URLs are rewritten to
 * absolute Telewebion addresses, so video never touches it, and video is the overwhelming
 * majority of the traffic. Cloudflare bills a Worker per incoming request. fetch()
 * subrequests and the Cache API are free and do not count.
 *
 * A player reloads a live playlist about once per EXT-X-TARGETDURATION. Telewebion
 * declares 2 seconds, which would be 1800 requests per viewer-hour. TARGETDURATION is an
 * upper bound rather than a promise, so declaring a larger value is legal as long as it is
 * at least the longest segment, and it slows the reload loop proportionally:
 *
 *   target 2s  -> 1800 requests/viewer-hour ->    55 viewer-hours/day on the free plan
 *   target 12s ->  300 requests/viewer-hour ->   333 viewer-hours/day
 *   target 20s ->  180 requests/viewer-hour ->   555 viewer-hours/day
 *
 * The default below is 12 seconds with a 60 second window, so the player always holds
 * about five reload intervals of buffer.
 *
 * The rewritten playlist is also cached at the edge for a few seconds. That does not
 * reduce billed requests, but it means a hundred people watching the same channel cause
 * one origin fetch rather than a hundred, and most invocations return from cache using
 * almost no CPU. Parsing costs well under the free plan's 10ms limit either way.
 *
 * DEPLOY
 *   npx wrangler deploy
 *
 * USE
 *   https://<your-worker>.workers.dev/tv1/1080p
 *   https://<your-worker>.workers.dev/irinn/720p
 */

const ORIGIN = "https://ncdn.telewebion.ir";
const TARGET_DURATION = 12;   // what we advertise, throttles the player's reload loop
const WINDOW_SECONDS = 60;    // how much content to list, comfortably over the reload gap
const EDGE_CACHE_SECONDS = 4; // collapses concurrent viewers into one origin fetch
const SEQUENCE_MODULUS = 1_000_000_000;   // nine digits, safely inside 32 bits

const SLUG = /^[a-z0-9_-]{1,40}$/i;
const RENDITION = /^(\d{3,4}p)$/;

export default {
  async fetch(request, ctx) {
    const url = new URL(request.url);
    const [, slug, rendition] = url.pathname.split("/");

    if (!slug || !SLUG.test(slug)) {
      return new Response("usage: /<channel>/<rendition>, e.g. /tv1/1080p\n", { status: 400 });
    }
    const quality = RENDITION.test(rendition || "") ? rendition : "1080p";

    const cache = caches.default;
    const cacheKey = new Request(`${url.origin}/${slug}/${quality}`, { method: "GET" });
    const cached = await cache.match(cacheKey);
    if (cached) return cached;

    const source = `${ORIGIN}/${slug}/live/${quality}/index.m3u8`;
    let upstream;
    try {
      upstream = await fetch(source, {
        headers: { "User-Agent": "VLC/3.0.20 LibVLC/3.0.20", Accept: "*/*" },
        cf: { cacheTtl: 2, cacheEverything: true },
      });
    } catch {
      return new Response("upstream unreachable\n", { status: 502 });
    }
    if (!upstream.ok) {
      return new Response(`upstream ${upstream.status}\n`, { status: 502 });
    }

    // fetch() follows redirects, and upstream.url is where the manifest actually came
    // from. Relative segment paths must resolve against that, not against `source`:
    // ncdn only serves manifests and refuses segments, which is the other reason strict
    // players fail on the original URL.
    const body = await upstream.text();
    const playlist = rewrite(body, upstream.url);
    if (!playlist) return new Response("unexpected upstream format\n", { status: 502 });

    const response = new Response(playlist, {
      headers: {
        "Content-Type": "application/vnd.apple.mpegurl",
        "Cache-Control": `public, max-age=${EDGE_CACHE_SECONDS}`,
        "Access-Control-Allow-Origin": "*",
      },
    });
    ctx.waitUntil(cache.put(cacheKey, response.clone()));
    return response;
  },
};

function rewrite(body, finalUrl) {
  // Upstream lists an hour of segments and we publish about a minute of them, so the
  // hot path must stay cheap: count in a single pass, keep only the tail, and resolve
  // URLs for that tail alone. Building a URL object per line costs roughly 8ms across
  // 1800 entries, which would sit right on the free plan's 10ms CPU ceiling.
  const base = new URL(finalUrl);
  const baseDir = base.href.slice(0, base.href.lastIndexOf("/") + 1);
  const lines = body.split("\n");

  const keepMax = Math.max(3, Math.ceil(WINDOW_SECONDS / 2)) + 4;
  const infs = new Array(keepMax);
  const uris = new Array(keepMax);
  let count = 0, slot = 0, sequence = null, pendingInf = null, longest = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    if (line.charCodeAt(0) === 35) {              // '#'
      if (line.startsWith("#EXTINF")) {
        pendingInf = line;
        const seconds = parseFloat(line.slice(8));
        if (seconds > longest) longest = seconds;
      } else if (sequence === null && line.startsWith("#EXT-X-MEDIA-SEQUENCE:")) {
        sequence = Number(line.slice(22));
      }
    } else if (pendingInf !== null) {
      infs[slot] = pendingInf;                    // ring buffer, only the tail survives
      uris[slot] = line;
      slot = (slot + 1) % keepMax;
      count++;
      pendingInf = null;
    }
  }
  if (!count || sequence === null) return null;

  const segment = longest || 2;
  const keep = Math.min(count, Math.max(3, Math.ceil(WINDOW_SECONDS / segment)));
  const target = Math.max(TARGET_DURATION, Math.ceil(longest));

  const out = [
    "#EXTM3U",
    "#EXT-X-VERSION:3",
    `#EXT-X-TARGETDURATION:${target}`,
    `#EXT-X-MEDIA-SEQUENCE:${(sequence + count - keep) % SEQUENCE_MODULUS}`,
  ];
  for (let i = keep; i > 0; i--) {
    const at = (slot - i + keepMax * 2) % keepMax;
    const uri = uris[at];
    out.push(infs[at],
      uri.charCodeAt(0) === 104 && uri.startsWith("http") ? uri   // already absolute
        : uri.charCodeAt(0) === 47 ? base.origin + uri            // root relative
        : baseDir + uri);
  }
  return out.join("\n") + "\n";
}
