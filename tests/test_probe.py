"""Reading a stream's answer. These are the judgements that decide whether a channel stays
in the playlists, and the costly mistake is calling a working stream dead, so the awkward
real world shapes each rule exists for are pinned down here."""
import unittest

import probe


class IsHls(unittest.TestCase):
    def test_a_manifest_is_recognised_with_or_without_leading_space(self):
        self.assertTrue(probe.is_hls(b"#EXTM3U\n#EXTINF:-1,x"))
        self.assertTrue(probe.is_hls(b"\n  #EXTM3U\n"))

    def test_an_error_page_is_not(self):
        self.assertFalse(probe.is_hls(b"<html><body>404</body></html>"))


class IsMedia(unittest.TestCase):
    def test_transport_stream_packets(self):
        self.assertTrue(probe.is_media(b"\x47" + b"\x00" * 300, None))

    def test_fragmented_mp4_boxes(self):
        for box in (b"ftyp", b"styp", b"moof"):
            self.assertTrue(probe.is_media(b"\x00\x00\x00\x18" + box + b"x" * 100, None))

    def test_an_error_page_dressed_as_a_200_is_rejected(self):
        self.assertFalse(probe.is_media(b"<html>not found</html>", "video/mp2t"))

    def test_a_content_type_alone_needs_some_bytes_behind_it(self):
        self.assertTrue(probe.is_media(b"z" * 2000, "video/mp2t"))
        self.assertFalse(probe.is_media(b"z" * 10, "video/mp2t"))


class ManifestDefects(unittest.TestCase):
    def test_a_tag_written_without_its_hash(self):
        # A strict client reads this line as a URI, requests it and stalls.
        body = b"#EXTM3U\nEXT-X-VERSION:6\n#EXTINF:2,\nseg.ts\n"
        self.assertIn("tag-missing-hash", probe.manifest_defects(body, "https://a/b/x.m3u8", None))

    def test_a_well_formed_manifest_has_no_defects(self):
        body = b"#EXTM3U\n#EXT-X-VERSION:6\n#EXTINF:2,\nseg.ts\n"
        self.assertEqual(probe.manifest_defects(body, "https://a/b/x.m3u8", None), [])

    def test_relative_segments_served_from_another_directory(self):
        body = b"#EXTM3U\n#EXTINF:2,\nseg1.ts\n"
        defects = probe.manifest_defects(body, "https://ncdn.example/ch/live/playlist.m3u8",
                                         "https://edge7.example/ek/ch/live/1080p/index.m3u8")
        self.assertIn("relative-uris-behind-redirect", defects)

    def test_absolute_segments_survive_a_redirect(self):
        body = b"#EXTM3U\n#EXTINF:2,\nhttps://edge7.example/ek/ch/seg1.ts\n"
        defects = probe.manifest_defects(body, "https://ncdn.example/ch/live/playlist.m3u8",
                                         "https://edge7.example/ek/ch/live/1080p/index.m3u8")
        self.assertNotIn("relative-uris-behind-redirect", defects)

    def test_a_redirect_inside_the_same_directory_is_harmless(self):
        body = b"#EXTM3U\n#EXTINF:2,\nseg1.ts\n"
        defects = probe.manifest_defects(body, "https://a.example/live/x.m3u8",
                                         "https://a.example/live/y.m3u8")
        self.assertNotIn("relative-uris-behind-redirect", defects)


class ManifestShape(unittest.TestCase):
    def test_a_sequence_past_a_32_bit_counter_is_a_hazard(self):
        shape = probe.manifest_shape(b"#EXTM3U\n#EXT-X-MEDIA-SEQUENCE:1786395804195022\n")
        self.assertEqual(shape["media_sequence"], 1786395804195022)
        self.assertIn("sequence-over-32bit", shape["hazards"])

    def test_an_ordinary_sequence_is_not(self):
        shape = probe.manifest_shape(b"#EXTM3U\n#EXT-X-MEDIA-SEQUENCE:1024\n")
        self.assertNotIn("hazards", shape)

    def test_a_heavy_manifest_is_a_hazard(self):
        shape = probe.manifest_shape(b"#EXTM3U\n" + b"#EXTINF:2,\nseg.ts\n" * 20000)
        self.assertIn("heavy-manifest", shape["hazards"])


class ClassifyFailure(unittest.TestCase):
    def test_a_legal_refusal_is_territorial_not_dead(self):
        self.assertEqual(probe.classify_failure("live.telewebion.ir", 451, b""), "iran_only")

    def test_a_known_domestic_cdn_is_never_called_dead(self):
        self.assertEqual(probe.classify_failure("cdn.irib.ir", 403, b"denied"), "iran_only")

    def test_an_expired_subscription_cdn_is_dead_even_though_it_403s(self):
        self.assertEqual(probe.classify_failure("x.pandatv.tn", 403, b""), "dead")

    def test_a_403_that_explains_itself_as_geographic(self):
        self.assertEqual(probe.classify_failure("a.com", 403, b"Not available in your country"),
                         "iran_only")

    def test_a_bare_403_is_dead(self):
        self.assertEqual(probe.classify_failure("a.com", 403, b"Forbidden"), "dead")

    def test_anything_else_is_dead(self):
        self.assertEqual(probe.classify_failure("a.com", 404, b""), "dead")


class ParseVariants(unittest.TestCase):
    def test_highest_bitrate_first(self):
        body = (b"#EXTM3U\n"
                b"#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360\nlow.m3u8\n"
                b"#EXT-X-STREAM-INF:BANDWIDTH=4000000,RESOLUTION=1920x1080\nhigh.m3u8\n")
        variants = probe.parse_variants(body, "https://a.com/live/master.m3u8")
        self.assertEqual([v[1] for v in variants], ["1920x1080", "640x360"])
        self.assertEqual(variants[0][2], "https://a.com/live/high.m3u8")

    def test_a_comma_inside_codecs_does_not_split_the_line(self):
        body = (b'#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=4000000,'
                b'CODECS="avc1.64001f,mp4a.40.2",RESOLUTION=1920x1080\nhigh.m3u8\n')
        variants = probe.parse_variants(body, "https://a.com/master.m3u8")
        self.assertEqual(variants, [(4000000, "1920x1080", "https://a.com/high.m3u8")])

    def test_average_bandwidth_is_not_mistaken_for_bandwidth(self):
        body = (b"#EXTM3U\n#EXT-X-STREAM-INF:AVERAGE-BANDWIDTH=111,BANDWIDTH=999,"
                b"RESOLUTION=1280x720\nv.m3u8\n")
        self.assertEqual(probe.parse_variants(body, "https://a.com/m.m3u8")[0][0], 999)

    def test_a_media_playlist_has_no_variants(self):
        self.assertEqual(probe.parse_variants(b"#EXTM3U\n#EXTINF:2,\nseg.ts\n", "https://a/m"), [])


class ParseSegments(unittest.TestCase):
    def test_relative_segments_are_resolved(self):
        body = b"#EXTM3U\n#EXTINF:2,\nseg1.ts\n#EXTINF:2,\nseg2.ts\n"
        self.assertEqual(probe.parse_segments(body, "https://a.com/live/index.m3u8"),
                         ["https://a.com/live/seg1.ts", "https://a.com/live/seg2.ts"])

    def test_an_initialisation_map_counts_as_a_segment(self):
        body = b'#EXTM3U\n#EXT-X-MAP:URI="init.mp4"\n#EXTINF:2,\nseg1.m4s\n'
        self.assertIn("https://a.com/live/init.mp4",
                      probe.parse_segments(body, "https://a.com/live/index.m3u8"))

    def test_a_truncated_read_drops_its_half_written_last_line(self):
        body = b"#EXTM3U\n#EXTINF:2,\nseg1.ts\n#EXTINF:2,\nseg2-cut"
        self.assertEqual(probe.parse_segments(body, "https://a.com/i.m3u8", truncated=True),
                         ["https://a.com/seg1.ts"])

    def test_a_complete_read_keeps_every_segment(self):
        body = b"#EXTM3U\n#EXTINF:2,\nseg1.ts\n#EXTINF:2,\nseg2.ts\n"
        self.assertEqual(len(probe.parse_segments(body, "https://a.com/i.m3u8")), 2)


class Retire(unittest.TestCase):
    NOW = "2026-08-11T12:00:00+00:00"

    def test_a_url_no_source_offers_is_marked_gone(self):
        streams = {"https://a": {"state": "ok", "last_ok": self.NOW},
                   "https://b": {"state": "ok", "last_ok": self.NOW}}
        probe.retire(streams, {"https://a"}, self.NOW)
        self.assertEqual(streams["https://b"]["state"], "gone")

    def test_a_retired_url_that_never_worked_is_dropped_at_once(self):
        streams = {"https://never": {"state": "ok", "fails": 3}}
        probe.retire(streams, set(), self.NOW)
        self.assertNotIn("https://never", streams)

    def test_a_recently_working_url_keeps_its_history(self):
        streams = {"https://recent": {"state": "ok", "last_ok": "2026-08-01T00:00:00+00:00"}}
        probe.retire(streams, set(), self.NOW)
        self.assertIn("https://recent", streams)
        self.assertEqual(streams["https://recent"]["state"], "gone")

    def test_a_long_retired_url_is_forgotten(self):
        streams = {"https://old": {"state": "ok", "last_ok": "2026-01-01T00:00:00+00:00"}}
        probe.retire(streams, set(), self.NOW)
        self.assertNotIn("https://old", streams)

    def test_a_probed_url_is_never_dropped(self):
        streams = {"https://live": {"state": "ok", "last_ok": "2020-01-01T00:00:00+00:00"}}
        probe.retire(streams, {"https://live"}, self.NOW)
        self.assertIn("https://live", streams)


class ReportTarget(unittest.TestCase):
    def test_a_full_run_publishes_and_may_retire(self):
        target, may_retire = probe.report_target(0)
        self.assertEqual(target, probe.DATA / "status.json")
        self.assertTrue(may_retire)

    def test_a_partial_run_cannot_touch_the_published_history(self):
        # Probing the first n urls is for local inspection. Retiring everything it did
        # not reach, or writing that over data/status.json, would empty the playlists.
        for limit in (1, 50, 1000):
            target, may_retire = probe.report_target(limit)
            self.assertNotEqual(target, probe.DATA / "status.json")
            self.assertEqual(target.parent.name, "build")
            self.assertFalse(may_retire)


if __name__ == "__main__":
    unittest.main()
