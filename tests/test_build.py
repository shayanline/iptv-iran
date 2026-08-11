"""Publishing decisions: which streams survive, how they are ranked, and how an entry is
written. The scoring comments in build.py state an order of preference, so the tests assert
that order rather than any particular number, which is free to be retuned."""
import unittest

import build


def stream(**over):
    base = {"state": "ok", "checks": 8, "uptime": 1.0, "variants": 1, "ms": 300,
            "resolution": "1920x1080"}
    return {**base, **over}


def channel(**over):
    base = {
        "id": "IRIB1.ir", "name_en": "IRIB TV1", "name_fa": "شبکه یک",
        "logo": "https://example.com/logo.png", "languages": ["fas"],
        "category": "irib-national", "quality": "FHD", "reach": "global",
    }
    return {**base, **over}


class Usable(unittest.TestCase):
    def test_a_working_stream_is_published(self):
        self.assertTrue(build.usable({"state": "ok"}))

    def test_iran_only_is_published_rather_than_deleted(self):
        # It is refusing this checker's location, not reporting that it has stopped.
        self.assertTrue(build.usable({"state": "iran_only", "fails": 99}))

    def test_a_recent_failure_is_kept_through_the_grace_period(self):
        entry = {"state": "dead", "fails": build.GRACE_FAILS, "last_ok": "2026-08-01T00:00:00+00:00"}
        self.assertTrue(build.usable(entry))

    def test_it_is_dropped_once_the_grace_period_runs_out(self):
        entry = {"state": "dead", "fails": build.GRACE_FAILS + 1,
                 "last_ok": "2026-08-01T00:00:00+00:00"}
        self.assertFalse(build.usable(entry))

    def test_a_stream_that_never_worked_is_never_published(self):
        self.assertFalse(build.usable({"state": "dead", "fails": 1}))

    def test_a_retired_url_is_dropped_immediately(self):
        self.assertFalse(build.usable({"state": "gone", "fails": 0, "last_ok": "2026-08-01"}))


class HeightOf(unittest.TestCase):
    def test_a_measured_resolution_is_preferred(self):
        self.assertEqual(build.height_of({"resolution": "1920x1080", "format": "480p"}), 1080)

    def test_the_providers_hint_is_next(self):
        self.assertEqual(build.height_of({"known_height": 720, "format": "480p"}), 720)

    def test_the_database_format_string_is_the_fallback(self):
        self.assertEqual(build.height_of({"format": "576i"}), 576)

    def test_nothing_known(self):
        self.assertEqual(build.height_of({}), 0)


class Score(unittest.TestCase):
    def test_reachable_beats_sharper_but_unreachable(self):
        reachable = build.score(stream(state="ok", resolution="640x480"))
        restricted = build.score(stream(state="iran_only", resolution="3840x2160"))
        self.assertGreater(reachable, restricted)

    def test_a_plain_stream_beats_one_needing_custom_headers(self):
        self.assertGreater(build.score(stream()),
                           build.score(stream(referrer="https://example.com")))
        self.assertGreater(build.score(stream()), build.score(stream(user_agent="Custom/1.0")))

    def test_a_malformed_manifest_loses_to_a_clean_equivalent(self):
        self.assertGreater(build.score(stream()), build.score(stream(defects=["tag-missing-hash"])))

    def test_higher_resolution_wins_all_else_equal(self):
        self.assertGreater(build.score(stream(resolution="1920x1080")),
                           build.score(stream(resolution="1280x720")))

    def test_adaptive_bitrate_is_worth_something(self):
        self.assertGreater(build.score(stream(variants=3)), build.score(stream(variants=1)))

    def test_a_single_check_is_treated_as_neutral_not_perfect(self):
        self.assertGreater(build.score(stream(checks=8, uptime=1.0)),
                           build.score(stream(checks=1, uptime=1.0)))

    def test_latency_only_breaks_ties(self):
        # A faster but lower resolution stream must not overtake a sharper one.
        self.assertGreater(build.score(stream(resolution="1920x1080", ms=3000)),
                           build.score(stream(resolution="1280x720", ms=1)))


class DisplayName(unittest.TestCase):
    def test_the_resolution_is_not_repeated_in_the_name(self):
        # It is published as tvg-quality, which is where a player looks for it.
        for quality in ("SD", "HD", "FHD", "4K"):
            for lang in ("en", "fa", "both"):
                name = build.display_name(channel(quality=quality), lang)
                self.assertNotIn(quality, name, f"{quality} leaked into the {lang} name")

    def test_each_naming_style(self):
        self.assertEqual(build.display_name(channel(), "en"), "IRIB TV1")
        self.assertEqual(build.display_name(channel(), "fa"), "شبکه یک")
        self.assertEqual(build.display_name(channel(), "both"), "IRIB TV1 | شبکه یک")

    def test_english_stands_in_when_there_is_no_persian_name(self):
        self.assertEqual(build.display_name(channel(name_fa=""), "fa"), "IRIB TV1")
        self.assertEqual(build.display_name(channel(name_fa=""), "both"), "IRIB TV1")

    def test_only_a_geographic_restriction_earns_a_marker(self):
        self.assertTrue(build.display_name(channel(reach="iran-only"), "en").endswith(" [IR]"))
        self.assertNotIn("[IR]", build.display_name(channel(reach="failing"), "en"))
        self.assertNotIn("[IR]", build.display_name(channel(reach="global"), "en"))


class Extinf(unittest.TestCase):
    def line(self, chan=None, strm=None, lang="both"):
        return build.extinf(chan or channel(), strm or {"url": "https://a.com/x.m3u8"}, lang)

    def test_the_quality_is_carried_as_an_attribute(self):
        self.assertIn('tvg-quality="FHD"', self.line())

    def test_an_unknown_quality_is_left_out_entirely(self):
        self.assertNotIn("tvg-quality", self.line(channel(quality="")))

    def test_the_group_follows_the_language_of_the_titles(self):
        self.assertIn('group-title="IRIB National Networks"', self.line(lang="en"))
        self.assertIn('group-title="شبکه‌های سراسری سیما"', self.line(lang="fa"))
        self.assertIn('group-title="IRIB National Networks | شبکه‌های سراسری سیما"',
                      self.line(lang="both"))

    def test_custom_headers_are_emitted_for_players_that_read_them(self):
        text = self.line(strm={"url": "https://a.com/x.m3u8", "user_agent": "UA/1",
                               "referrer": "https://ref"})
        self.assertIn("#EXTVLCOPT:http-user-agent=UA/1", text)
        self.assertIn("#EXTVLCOPT:http-referrer=https://ref", text)
        self.assertTrue(text.endswith("https://a.com/x.m3u8"))

    def test_the_url_is_always_the_last_line(self):
        self.assertTrue(self.line().endswith("\nhttps://a.com/x.m3u8"))


if __name__ == "__main__":
    unittest.main()
