import assert from "node:assert/strict";
import test from "node:test";
import worker, { isNativeMediaRequest } from "../worker/telewebion-rewrite.js";

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
