"""Publishing decisions: which streams survive, how they are ranked, and how an entry is
written. The scoring comments in build.py state an order of preference, so the tests assert
that order rather than any particular number, which is free to be retuned."""
import inspect
import io
import pathlib
import tempfile
import unittest
from unittest import mock

from PIL import Image

import build
import logos
import readme
import validate


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

    def test_a_tls_failure_is_excluded_immediately(self):
        for reason in ("tls", "variant:tls", "segment:tls"):
            entry = {"state": "dead", "reason": reason, "fails": 1,
                     "last_ok": "2026-08-01T00:00:00+00:00"}
            self.assertFalse(build.usable(entry))

    def test_a_recovered_stream_ignores_an_old_tls_reason(self):
        self.assertTrue(build.usable({"state": "ok", "reason": "tls"}))

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


class StreamVisibility(unittest.TestCase):
    def test_public_backup_playlist_excludes_unlisted_streams(self):
        public = stream(url="https://public.example/live.m3u8", unlisted_only=False)
        hidden = stream(url="https://proxy.example/live.m3u8", unlisted_only=True)
        item = channel(streams=[public, hidden])
        path = build.HERE / "build" / ".test-playlist.m3u"
        try:
            build.write_playlist(path, [item], "test", all_streams=True)
            text = path.read_text(encoding="utf-8")
            self.assertIn(public["url"], text)
            self.assertNotIn(hidden["url"], text)
        finally:
            path.unlink(missing_ok=True)

    def test_build_writes_no_private_playlist_outputs(self):
        direct = stream(url="https://provider.example/live.m3u8", hazards=[], defects=[],
                        sources=["curated"], unlisted_only=False)
        item = channel(streams=[direct], best=direct, compat=direct,
                       compat_public=direct, public=True)
        original = build.PLAYLISTS
        with tempfile.TemporaryDirectory(dir=build.HERE) as directory:
            folder = pathlib.Path(directory) / "playlists"
            try:
                build.PLAYLISTS = folder
                build.build_playlists([item])
                self.assertFalse((folder / "unlisted").exists())
                self.assertFalse((folder.parent / "worker" / "playlists").exists())
            finally:
                build.PLAYLISTS = original


class PublishedChannels(unittest.TestCase):
    def test_curated_categories_are_applied_when_rerendering(self):
        channels = {channel["id"]: channel for channel in build.published_channels()}
        self.assertEqual(channels["AraxTV.ir"]["category"], "sat-movies")
        self.assertNotIn("sat-entertainment",
                         {channel["category"] for channel in channels.values()})

    def test_an_officially_relaunched_channel_is_published(self):
        channels = {channel["id"]: channel for channel in build.published_channels()}
        self.assertIn("PersianaRap.fr", channels)

    def test_new_persiana_channels_have_persian_names(self):
        channels = {channel["id"]: channel for channel in build.published_channels()}
        expected = {
            "PersianaDocs.fr": "پرشیانا مستند",
            "PersianaFamily.fr": "پرشیانا خانواده",
            "PersianaFight.fr": "پرشیانا رزمی",
            "PersianaFolk.fr": "پرشیانا سنتی",
            "PersianaJunior.fr": "پرشیانا کودک",
            "PersianaMedical.fr": "پرشیانا پزشکی",
            "PersianaMusic.fr": "پرشیانا موسیقی",
            "PersianaRap.fr": "پرشیانا رپ",
            "PersianaTravel.fr": "پرشیانا سفر",
        }
        self.assertEqual({channel_id: channels[channel_id]["name_fa"]
                          for channel_id in expected}, expected)

    def test_rjtv_uses_its_radio_javan_brand_name(self):
        channels = {channel["id"]: channel for channel in build.published_channels()}
        self.assertEqual(channels["RJTV.us"]["name_en"], "Radio Javan")
        self.assertEqual(channels["RJTV.us"]["name_fa"], "رادیو جوان")

    def test_curated_names_are_reapplied_when_rerendering(self):
        channels = {channel["id"]: channel for channel in build.published_channels()}
        self.assertEqual(channels["MihanTV.ir"]["name_fa"], "میهن")
        self.assertEqual(channels["KhaterehTV.us"]["name_fa"], "خاطره")

    def test_local_curated_names_are_applied_during_collection(self):
        url = "https://example.com/nima.m3u8"
        candidate = {"url": url, "db": {"id": "NimaTV.us", "name": "Nima TV",
                                      "country": "US", "languages": ["fas"],
                                      "categories": ["general"], "local": True}}
        status = {"streams": {url: {"state": "ok", "final_url": url,
                                    "resolution": "1280x720", "checks": 2,
                                    "uptime": 1.0, "variants": 1, "ms": 10}}}
        curated = {"channels": {}, "local_channels": {
            "NimaTV.us": {"en": "Nima TV", "fa": "نیما"}}}

        def fake_read_json(path, default):
            if path == build.CANDIDATES:
                return [candidate]
            if path == build.DATA / "status.json":
                return status
            if path == build.DATA / "curated.json":
                return curated
            return default

        with mock.patch.object(build, "read_json", side_effect=fake_read_json), \
                mock.patch.object(build, "mirrored_logos", return_value={}):
            channels = build.collect()
        self.assertEqual(channels[0]["name_fa"], "نیما")

    def test_every_generated_channel_has_a_persian_name(self):
        missing = [channel["id"] for channel in build.published_channels()
                   if not channel["name_fa"]]
        self.assertEqual(missing, [])

    def test_persian_channel_names_drop_the_trailing_tv_word(self):
        branded = {"PressTV.ir", "PressTVFrench.ir", "HispanTV.ir", "ShoraiTV.us",
                   "IranTVIsrael.il", "PTV1.us", "IRTV.us"}
        curated = build.read_json(build.DATA / "curated.json", {})
        offenders = sorted({channel_id
                            for section in ("channels", "local_channels")
                            for channel_id, row in curated[section].items()
                            if channel_id not in branded
                            and ("تی‌وی" in row["fa"] or "تلویزیون" in row["fa"])})
        self.assertEqual(offenders, [])


class ValidationMetadata(unittest.TestCase):
    def test_missing_persian_name_is_reported_without_blocking_the_channel(self):
        self.assertTrue(validate.check_metadata([{"id": "Missing.ir", "name_fa": ""}]))


class RefreshWorkflow(unittest.TestCase):
    def test_race_recovery_preserves_non_generated_files(self):
        workflow = (build.HERE / ".github" / "workflows" / "refresh.yml").read_text(
            encoding="utf-8")
        self.assertNotIn("git reset --soft FETCH_HEAD", workflow)
        self.assertIn('git restore --source="$refresh_commit"', workflow)
        self.assertIn("data/channels.json data/status.json", workflow)
        self.assertNotIn("playlists data assets", workflow)


class ReadmeMetadata(unittest.TestCase):
    def test_checked_badge_uses_the_probe_timestamp(self):
        item = channel(streams=[{"url": "https://a.com/x.m3u8"}],
                       compat_public={"url": "https://a.com/x.m3u8"},
                       resolution="1920x1080", height=1080, province_en="", province_fa="")
        try:
            text = readme.render([item], "2026-09-01T09:23:29+00:00")
        except TypeError as exc:
            self.fail(f"the renderer did not accept the probe timestamp: {exc}")
        self.assertIn("last%20checked-01%20September%202026", text)


class ConsumerGuidance(unittest.TestCase):
    def setUp(self):
        source = stream(url="https://a.com/x.m3u8")
        self.item = channel(
            streams=[source],
            best=source,
            compat=source,
            compat_public=source,
            resolution="1920x1080",
            height=1080,
            province_en="",
            province_fa="",
        )

    def test_landing_page_links_to_separate_channel_catalogues(self):
        text = readme.render([self.item], "2026-09-01T09:23:29+00:00")
        self.assertIn("CHANNELS.md", text)
        self.assertIn("CHANNELS.fa.md", text)
        self.assertNotIn("<summary><b>", text)

    def test_landing_uses_the_main_playlist_without_removed_variants(self):
        text = readme.render([self.item], "2026-09-01T09:23:29+00:00")
        self.assertIn("**Main playlist**", text)
        self.assertIn("/playlists/fa/iran.m3u", text)
        self.assertNotIn("iran-global.m3u", text)
        self.assertNotIn("iran-domestic.m3u", text)

    def test_backup_count_excludes_unlisted_streams(self):
        hidden = stream(url="https://proxy.example/live.m3u8", unlisted_only=True)
        text = readme.render([{**self.item, "streams": [self.item["best"], hidden]}],
                             "2026-09-01T09:23:29+00:00")
        self.assertIn("| 1 streams |", text)

    def test_only_three_main_playlists_are_generated(self):
        folder = build.HERE / "build"
        folder.mkdir(parents=True, exist_ok=True)
        original = build.PLAYLISTS
        with tempfile.TemporaryDirectory(dir=folder) as directory:
            try:
                build.PLAYLISTS = pathlib.Path(directory)
                build.build_playlists([self.item])
                names = {path.name for path in build.PLAYLISTS.glob("*.m3u")}
            finally:
                build.PLAYLISTS = original
        self.assertEqual(names, {"iran.m3u", "iran-all-streams.m3u", "iran-compat.m3u"})

    def test_epg_metadata_is_omitted_until_a_verified_feed_exists(self):
        path = build.HERE / "build" / ".test-playlist.m3u"
        try:
            build.write_playlist(path, [self.item], "test", all_streams=True)
            self.assertEqual(path.read_text(encoding="utf-8").splitlines()[0], "#EXTM3U")
        finally:
            path.unlink(missing_ok=True)

        text = readme.render([self.item], "2026-09-01T09:23:29+00:00")
        self.assertNotIn("EPGShare01", text)
        self.assertNotIn("x-tvg-url", text)

    def test_channel_catalogue_contains_channel_rows(self):
        text = readme.render_catalog([self.item], "en")
        self.assertIn("# Channel catalogue", text)
        self.assertIn("IRIB TV1", text)


class LogoOptimisation(unittest.TestCase):
    def test_logo_is_resized_to_a_television_safe_png(self):
        source = io.BytesIO()
        Image.new("RGBA", (1200, 600), (20, 80, 160, 255)).save(source, "PNG")

        optimiser = getattr(logos, "optimise_image", None)
        self.assertIsNotNone(optimiser)
        body = optimiser(source.getvalue())

        with Image.open(io.BytesIO(body)) as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (512, 256))
        self.assertLess(len(body), len(source.getvalue()))

    def test_logo_is_upscaled_for_crisp_4k_interfaces(self):
        source = io.BytesIO()
        Image.new("RGBA", (120, 60), (20, 80, 160, 255)).save(source, "PNG")

        body = logos.optimise_image(source.getvalue())

        with Image.open(io.BytesIO(body)) as image:
            self.assertEqual(image.size, (512, 256))

    def test_transparent_padding_is_removed_before_resizing(self):
        source = Image.new("RGBA", (1200, 1200), (0, 0, 0, 0))
        source.paste((20, 80, 160, 255), (100, 350, 1100, 850))
        encoded = io.BytesIO()
        source.save(encoded, "PNG")

        body = logos.optimise_image(encoded.getvalue())

        with Image.open(io.BytesIO(body)) as image:
            self.assertEqual(image.size, (512, 256))

    def test_mirror_optimises_a_downloaded_logo(self):
        source = io.BytesIO()
        Image.new("RGB", (1200, 600), (20, 80, 160)).save(source, "JPEG")

        with tempfile.TemporaryDirectory() as temporary, \
                mock.patch.object(logos, "ASSETS", pathlib.Path(temporary)), \
                mock.patch.object(logos, "evaluate", return_value=(source.getvalue(), "jpg", "ok")):
            logos.mirror({"ExampleTV.ir": ["https://example.com/logo.jpg"]})
            output = pathlib.Path(temporary) / "ExampleTV.ir.png"

            self.assertTrue(output.exists())
            with Image.open(output) as image:
                self.assertEqual(image.size, (512, 256))

    def test_mirror_preserves_selected_existing_logo_bytes(self):
        source = io.BytesIO()
        Image.new("RGB", (1200, 600), (20, 80, 160)).save(source, "JPEG")
        self.assertIn("preserve", inspect.signature(logos.mirror).parameters)

        with tempfile.TemporaryDirectory() as temporary, \
                mock.patch.object(logos, "ASSETS", pathlib.Path(temporary)), \
                mock.patch.object(logos, "evaluate", return_value=(source.getvalue(), "jpg", "ok")):
            output = pathlib.Path(temporary) / "ExampleTV.ir.png"
            output.write_bytes(b"audited logo")
            logos.mirror({"ExampleTV.ir": ["https://example.com/logo.jpg"]},
                         preserve={"ExampleTV.ir"})

            self.assertTrue(output.exists())
            self.assertEqual(output.read_bytes(), b"audited logo")
            self.assertFalse((output.parent / "ExampleTV.ir.jpg").exists())


if __name__ == "__main__":
    unittest.main()
