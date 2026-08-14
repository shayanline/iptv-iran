/**
 * Telewebion manifest rewriter, for players that cannot handle the original.
 *
 * WHY THIS EXISTS
 * Telewebion publishes IRIB's channels, and it is the only source for them reachable from
 * outside Iran. Its media playlists are valid HLS, and one number in them is more than a
 * television can hold:
 *
 *   EXT-X-MEDIA-SEQUENCE is sixteen digits, for example 1786395804195022, because the
 *   packager derives it from a microsecond timestamp. Samsung's AVPlay keeps that field in
 *   a SIGNED 32 bit integer, so anything above 2,147,483,647 overflows and its window
 *   arithmetic collapses. Telewebion's value is about 831,000 times the limit.
 *
 * Measured on a Samsung QE55S90D running Tizen 9.0, one property changed at a time, by
 * serving AVPlay manifests built from this same stream:
 *
 *   sequence 2,147,483,000 (just under 2^31)  ->  plays, window reported correctly
 *   sequence 2,147,484,000 (just over 2^31)   ->  reports the stream as 2000ms, one frame
 *   sequence 4,294,966,000 (just under 2^32)  ->  same failure, so it is signed, not unsigned
 *
 * THE WINDOW IS NOT THE PROBLEM, AND THAT MATTERS
 * The same test says the size of the playlist is fine: 3600 segments and 813KB parsed
 * correctly and played, as did 600 and 120. So trimming is not what fixes anything, and a
 * shorter window on its own would not have helped. Trimming stays because it is what keeps
 * this Worker's CPU and egress small, which is a cost decision rather than a fix. Anyone
 * tempted to raise SEQUENCE_MODULUS to fit "32 bits" should read the table above first:
 * four billion is not a safe number here, two billion is.
 *
 * COST CONTROL, THE POINT OF THE DESIGN
 * Only the media playlist passes through this Worker. Segment URLs are rewritten to
 * absolute Telewebion addresses, so video never touches it, and video is the overwhelming
 * majority of the traffic. Cloudflare bills a Worker per incoming request. fetch()
 * subrequests and the Cache API are free and do not count.
 *
 * How often a player comes back was assumed here and is now measured. AVPlay reloads at
 * about HALF the declared TARGETDURATION, not once per target, and it starts playback about
 * three targets behind the live edge. Counted over 64 seconds of real playback:
 *
 *   target 12s -> reload every 6.4s -> 562 requests/viewer-hour -> 178 viewer-hours/day
 *   target 20s -> reload every 9.1s -> 394 requests/viewer-hour -> 253 viewer-hours/day
 *   target 30s -> reload every 12.8s -> 281 requests/viewer-hour -> 355 viewer-hours/day
 *
 * The right hand column is the free plan's 100,000 requests a day. The old comment here
 * claimed 300 requests per viewer-hour at a 12 second target, which was half the truth and
 * therefore twice the capacity.
 *
 * Two things that would have decoupled the request rate from the latency do not work, and
 * both were tried on the set rather than reasoned about:
 *
 *   EXT-X-START:TIME-OFFSET   ignored. Playback began 33.6s behind the edge with and
 *                             without it, which is three times the target either way.
 *   Cache-Control: max-age    ignored for playlist reloads. Ten requests in 64 seconds
 *                             with max-age=10, and ten with no-cache.
 *
 * So the only lever is TARGETDURATION, and it buys fewer requests with more delay behind
 * live. 20 seconds is the default below: a third fewer requests than before, and a viewer
 * about a minute behind the broadcast, which nobody notices on a channel and everybody
 * notices during a football match.
 *
 * DESKTOP PLAYERS ARE SENT AWAY, WHICH IS THE OTHER HALF OF THE SAVING
 * VLC, ffmpeg, mpv and Kodi read Telewebion's original manifest perfectly well, so they are
 * redirected to it and stop costing anything at all. Browsers are deliberately not, because
 * Telewebion allows one origin and a page would be refused: hls.js needs this Worker's
 * Access-Control-Allow-Origin. Anything unrecognised gets the rewrite, which is the safe
 * default. AVPlay identifies itself as "samsung-agent/1.1".
 *
 * DEPLOY
 *   npx wrangler deploy
 *
 * USE
 *   https://<your-worker>.workers.dev/tv1/1080p
 *   https://<your-worker>.workers.dev/irinn/720p
 */

const ORIGIN = "https://ncdn.telewebion.ir";
const TARGET_DURATION = 20;   // what we advertise, halved is how often a player returns
const WINDOW_SECONDS = 150;   // three targets of start latency, plus 90s of margin
const EDGE_CACHE_SECONDS = 8; // collapses concurrent viewers into one origin fetch
/**
 * Nine digits, and the ceiling is 2^31 rather than 2^32: see the table at the top. Nine
 * digits also means the number a player sees never grows past this, whatever Telewebion's
 * does, and it advances by one per segment exactly as the original does.
 */
const SEQUENCE_MODULUS = 1_000_000_000;

const SLUG = /^[a-z0-9_-]{1,40}$/i;
const RENDITION = /^(\d{3,4}p)$/;
/**
 * Players that read the original without help, and are therefore not this Worker's problem.
 *
 * Browsers are absent on purpose. hls.js copes with the sixteen digit sequence, being
 * JavaScript, but Telewebion's Access-Control-Allow-Origin names one site, so a page has to
 * come through here for the header this Worker adds.
 */
const READS_THE_ORIGINAL = /vlc|libvlc|lavf|ffmpeg|mpv|kodi|gstreamer|mplayer/i;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const [, slug, rendition] = url.pathname.split("/");

    if (!slug || !SLUG.test(slug)) {
      return new Response("usage: /<channel>/<rendition>, e.g. /tv1/1080p\n", { status: 400 });
    }
    const quality = RENDITION.test(rendition || "") ? rendition : "1080p";
    const source = `${ORIGIN}/${slug}/live/${quality}/index.m3u8`;

    /*
     * A player that can read the original is sent to it, and stops costing anything.
     *
     * Temporary rather than permanent, so nothing caches the decision: the day Telewebion
     * changes its addresses, this Worker is the only thing that has to know. If a player
     * follows the redirect but keeps asking here on every reload, the cost is this branch
     * rather than a fetch and a parse, so the worst case is still cheaper than before.
     */
    if (READS_THE_ORIGINAL.test(request.headers.get("user-agent") ?? "")) {
      return Response.redirect(source, 302);
    }

    const cache = caches.default;
    const cacheKey = new Request(`${url.origin}/${slug}/${quality}`, { method: "GET" });
    const cached = await cache.match(cacheKey);
    if (cached) return cached;

    let upstream;
    try {
      upstream = await fetch(source, {
        headers: { "User-Agent": "VLC/3.0.20 LibVLC/3.0.20", Accept: "*/*" },
        // Four seconds rather than two. A player now returns every nine seconds or so, and
        // two segments of staleness against a 150 second window is nothing, so this halves
        // the origin fetches for a channel with several viewers.
        cf: { cacheTtl: 4, cacheEverything: true },
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
  /*
   * Upstream lists two hours of segments and we publish two and a half minutes of them, so
   * the hot path must stay cheap: count in a single pass, keep only the tail in a ring
   * buffer, and resolve URLs for that tail alone. Building a URL object per line would cost
   * roughly 8ms across 1800 entries, which is where the free plan's 10ms CPU ceiling is.
   *
   * That headroom is worth watching rather than trusting, because the upstream window has
   * already doubled once: it was 1800 segments and 318KB when this was written and it is
   * 3600 and 651KB today, so the single pass walks twice the lines it used to.
   */
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
