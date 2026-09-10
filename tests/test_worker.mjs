import assert from "node:assert/strict";
import test from "node:test";
import worker, { isNativeMediaRequest, rewrite } from "../worker/telewebion-rewrite.js";

const request = (headers) => new Request("https://worker.example/tv1/1080p", { headers });

test("recognises a browser native media request", () => {
  assert.equal(isNativeMediaRequest(request({
    range: "bytes=0-",
    "user-agent": "Mozilla/5.0 AppleWebKit/537.36 Edg/151.0.0.0",
  })), true);
});

test("redirects native browser media requests to the original manifest", async () => {
  const response = await worker.fetch(request({
    range: "bytes=0-",
    "user-agent": "Mozilla/5.0 AppleWebKit/537.36 Edg/151.0.0.0",
  }), {}, { waitUntil() {} });

  assert.equal(response.status, 302);
  assert.equal(
    response.headers.get("location"),
    "https://ncdn.telewebion.ir/tv1/live/1080p/index.m3u8",
  );
});

test("keeps hls.js and AVPlay requests on the rewritten path", () => {
  assert.equal(isNativeMediaRequest(request({
    "user-agent": "Mozilla/5.0 AppleWebKit/537.36 Edg/151.0.0.0",
  })), false);
  assert.equal(isNativeMediaRequest(request({
    range: "bytes=0-",
    "user-agent": "samsung-agent/1.1",
  })), false);
});

test("proxies Telewebion segments with browser CORS headers", async () => {
  const target = "https://live-edge.telewebion.net/ek/tv1/live/1080p/segment.ts";
  const originalFetch = globalThis.fetch;
  const originalCaches = globalThis.caches;
  const upstream = new Response("segment", { headers: { "Content-Type": "video/mp2t" } });
  Object.defineProperty(upstream, "url", { value: target });
  globalThis.fetch = async () => upstream;
  globalThis.caches = { default: { match: async () => null, put: async () => {} } };
  try {
    const response = await worker.fetch(new Request(
      `https://worker.example/segment?url=${encodeURIComponent(target)}`,
    ), {}, { waitUntil() {} });
    assert.equal(response.status, 200);
    assert.equal(response.headers.get("access-control-allow-origin"), "*");
    assert.match(response.headers.get("access-control-expose-headers"), /Content-Range/i);
    assert.equal(await response.text(), "segment");
  } finally {
    globalThis.fetch = originalFetch;
    globalThis.caches = originalCaches;
  }
});

test("rejects segment proxy targets outside Telewebion", async () => {
  const originalFetch = globalThis.fetch;
  const originalCaches = globalThis.caches;
  globalThis.fetch = async () => assert.fail("invalid target reached fetch");
  globalThis.caches = { default: { match: async () => null, put: async () => {} } };
  try {
    const target = encodeURIComponent("https://example.com/segment.ts");
    const response = await worker.fetch(
      new Request(`https://worker.example/segment?url=${target}`), {}, { waitUntil() {} },
    );
    assert.equal(response.status, 400);
  } finally {
    globalThis.fetch = originalFetch;
    globalThis.caches = originalCaches;
  }
});

test("rewrites the media sequence and resolves relative segments", () => {
  const manifest = [
    "#EXTM3U",
    "#EXT-X-TARGETDURATION:2",
    "#EXT-X-MEDIA-SEQUENCE:1786395804195022",
    "#EXTINF:2,",
    "segment-1.ts",
    "#EXTINF:2,",
    "segment-2.ts",
  ].join("\n");

  const rewritten = rewrite(
    manifest,
    "https://edge.example/live/index.m3u8",
    "https://worker.example",
  );

  assert.match(rewritten, /#EXT-X-MEDIA-SEQUENCE:804195022/);
  assert.match(rewritten,
    /https:\/\/worker\.example\/segment\?url=https%3A%2F%2Fedge\.example%2Flive%2Fsegment-2\.ts/);
});
