"""Category assignment and the resolution label, both of which are documented as a fixed
rule order, so the order is what is worth testing rather than any single channel."""
import json
import os
import unittest
from unittest import mock

from lib import DATA
import sources
import taxonomy


class SourceBlocklist(unittest.TestCase):
    def test_private_host_exclusions_are_loaded_from_the_environment(self):
        self.assertTrue(hasattr(sources, "blocked_hosts"))
        with mock.patch.dict(os.environ, {"PRIVATE_BLOCKED_HOSTS": "private.example,other.example"}):
            self.assertEqual(sources.blocked_hosts({"blocked_hosts": ["public.example"]}),
                             ("public.example", "private.example", "other.example"))


class QualityTag(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(taxonomy.quality_tag(2160), "4K")
        self.assertEqual(taxonomy.quality_tag(1080), "FHD")
        self.assertEqual(taxonomy.quality_tag(1079), "HD")
        self.assertEqual(taxonomy.quality_tag(720), "HD")
        self.assertEqual(taxonomy.quality_tag(719), "SD")
        self.assertEqual(taxonomy.quality_tag(576), "SD")

    def test_unknown_height_has_no_label(self):
        self.assertEqual(taxonomy.quality_tag(0), "")
        self.assertEqual(taxonomy.quality_tag(None), "")


class Classify(unittest.TestCase):
    def setUp(self):
        self.curated = {
            "category_overrides": {"Override.ir": "sat-music"},
            "sets": {
                "irib_provincial": ["Abadan.ir"],
                "irib_national": ["IRIB1.ir"],
                "religious_christian": ["Mohabat.ir"],
            },
        }

    def test_an_override_beats_everything(self):
        self.assertEqual(
            taxonomy.classify("Override.ir", ["news", "religious"], self.curated), "sat-music")

    def test_a_named_set_beats_the_database_genres(self):
        self.assertEqual(taxonomy.classify("Abadan.ir", ["news"], self.curated), "irib-provincial")

    def test_provincial_is_checked_before_national(self):
        # A channel in both lists is provincial, per the documented order.
        curated = {"sets": {"irib_provincial": ["Both.ir"], "irib_national": ["Both.ir"]}}
        self.assertEqual(taxonomy.classify("Both.ir", [], curated), "irib-provincial")

    def test_christian_is_checked_before_the_religious_genre(self):
        self.assertEqual(taxonomy.classify("Mohabat.ir", ["religious"], self.curated),
                         "religious-christian")

    def test_the_religious_genre_beats_any_other_genre(self):
        self.assertEqual(taxonomy.classify("X.ir", ["music", "religious"], {}), "religious-islamic")

    def test_the_first_mapped_genre_wins(self):
        self.assertEqual(taxonomy.classify("X.ir", ["unmapped", "movies", "news"], {}),
                         "sat-movies")

    def test_family_means_broad_programming_instead_of_children(self):
        self.assertEqual(taxonomy.classify("X.ir", ["family"], {}), "sat-general")

    def test_business_belongs_with_factual_programming(self):
        self.assertEqual(taxonomy.classify("X.ir", ["business"], {}), "sat-documentary")

    def test_general_and_unknown_channels_use_general(self):
        self.assertEqual(taxonomy.classify("X.ir", ["general"], {}), "sat-general")
        self.assertEqual(taxonomy.classify("X.ir", ["nothing-we-map"], {}), "sat-general")

    def test_content_categories_keep_visible_satellite_prefixes(self):
        expected = {
            "sat-general": ("Satellite · General & Variety", "ماهواره‌ای · عمومی و متنوع"),
            "sat-movies": ("Satellite · Film & Series", "ماهواره‌ای · فیلم و سریال"),
            "sat-news": ("Satellite · News & Current Affairs", "ماهواره‌ای · خبر و امور جاری"),
            "sat-music": ("Satellite · Music", "ماهواره‌ای · موسیقی"),
            "sat-kids": ("Satellite · Children", "ماهواره‌ای · کودک"),
            "sat-sports": ("Satellite · Sports", "ماهواره‌ای · ورزش"),
            "sat-documentary": ("Satellite · Factual, Culture & Lifestyle", "ماهواره‌ای · مستند، فرهنگ و سبک زندگی"),
        }
        self.assertEqual({cid: (taxonomy.LABELS[cid]["en"], taxonomy.LABELS[cid]["fa"])
                          for cid in expected}, expected)

    def test_every_category_a_rule_can_produce_is_declared(self):
        produced = ({c for _, c in taxonomy.SET_RULES} | set(taxonomy.GENRE_MAP.values())
                    | {"religious-islamic", taxonomy.FALLBACK})
        self.assertTrue(produced <= set(taxonomy.LABELS), produced - set(taxonomy.LABELS))

    def test_reviewed_satellite_channels_have_explicit_categories(self):
        curated = json.loads((DATA / "curated.json").read_text(encoding="utf-8"))
        channels = json.loads((DATA / "channels.json").read_text(encoding="utf-8"))
        reviewed = {channel["id"] for channel in channels if channel["category"].startswith("sat-")}
        self.assertTrue(reviewed <= set(curated["category_overrides"]))

    def test_researched_corrections_override_upstream_genres(self):
        curated = json.loads((DATA / "curated.json").read_text(encoding="utf-8"))
        expected = {
            "4UTV.tr": "sat-movies",
            "AraxTV.ir": "sat-movies",
            "AsilTV.ir": "religious-islamic",
            "AzadiTV.ir": "sat-news",
            "CafeTradeTV.ir": "sat-documentary",
            "DejTV.ir": "sat-news",
            "FX2.ir": "sat-kids",
            "GordAfaridTV.us": "sat-news",
            "HomePlus.ir": "sat-general",
            "IranIndependent.us": "sat-general",
            "IranTVIsrael.il": "sat-news",
            "MaahTV.my": "sat-movies",
            "NovinTV.ir": "sat-general",
            "ParsTV.us": "sat-news",
            "PayamJavanTV.us": "sat-documentary",
            "PersianaChina.fr": "sat-movies",
            "PersianaMedical.fr": "sat-movies",
            "PersianaPodcast.fr": "sat-documentary",
            "ProjectLeon.us": "sat-news",
            "RaviTV.us": "sat-general",
            "SetarehTV.uk": "sat-news",
            "Shabakeh7.us": "religious-christian",
            "SimayeAzadi.uk": "sat-news",
            "TMTV.us": "sat-documentary",
            "ZedTV.ir": "sat-news",
        }
        self.assertEqual({cid: curated["category_overrides"].get(cid) for cid in expected}, expected)

    def test_missing_directory_channels_are_curated(self):
        curated = json.loads((DATA / "curated.json").read_text(encoding="utf-8"))
        expected = {
            "ChannelOne.us": "sat-news",
            "GEMBollywood.tr": "sat-movies",
            "GEMClassic.tr": "sat-movies",
            "GEMDrama.tr": "sat-movies",
            "GEMFilm.tr": "sat-movies",
            "GEMFood.tr": "sat-documentary",
            "GEMJunior.tr": "sat-kids",
            "GEMKids.tr": "sat-kids",
            "GEMLife.tr": "sat-documentary",
            "GEMOnyx.tr": "sat-movies",
            "GEMRiver.tr": "sat-movies",
            "GEMRubix.tr": "sat-movies",
            "GEMSport.tr": "sat-sports",
            "GEMTV.tr": "sat-general",
            "KhabarbinTV.us": "sat-news",
            "KhaterehTV.us": "sat-general",
            "PersianaChina.fr": "sat-movies",
            "PersianaMusic.fr": "sat-music",
            "PersianaPodcast.fr": "sat-documentary",
            "PersianaRap.fr": "sat-music",
            "PersianaVoyage.fr": "sat-documentary",
        }
        stream_channels = {stream.get("channel") for stream in curated["streams"]}
        self.assertTrue(expected.keys() <= stream_channels)
        self.assertEqual({cid: curated["category_overrides"].get(cid) for cid in expected}, expected)

    def test_rebranded_persiana_streams_replace_stale_identities(self):
        curated = json.loads((DATA / "curated.json").read_text(encoding="utf-8"))
        self.assertEqual(curated["relabelled"].get(
            "https://musichls.persiana.live/hls/stream.m3u8"), "PersianaMusic.fr")
        self.assertEqual(curated["relabelled"].get(
            "https://raphls.persiana.live/hls/stream.m3u8"), "PersianaRap.fr")

    def test_woman_tv_stream_is_reassigned_to_azadi_tv(self):
        curated = json.loads((DATA / "curated.json").read_text(encoding="utf-8"))
        url = "https://wmtvhls.wns.live/hls/stream.m3u8"
        stream = next(stream for stream in curated["streams"] if stream["url"] == url)
        self.assertEqual(stream["channel"], "AzadiTV.ir")
        self.assertEqual(curated["relabelled"].get(url), "AzadiTV.ir")
        self.assertIn("AzadiTV.ir", curated["local_channels"])
        self.assertNotIn("WomanTV.us", curated["local_channels"])


class Tags(unittest.TestCase):
    def channel(self, **over):
        base = {"category": "irib-national", "reach": "global", "height": 1080,
                "languages": ["fas"], "streams": [{}]}
        return {**base, **over}

    def test_operator_distribution_and_quality(self):
        self.assertEqual(taxonomy.tags(self.channel()),
                         ["irib", "national", "worldwide", "fhd", "fas"])

    def test_reach_is_reported_faithfully(self):
        self.assertIn("iran-only", taxonomy.tags(self.channel(reach="iran-only")))
        self.assertIn("failing", taxonomy.tags(self.channel(reach="failing")))
        self.assertIn("worldwide", taxonomy.tags(self.channel(reach="global")))

    def test_a_backup_is_flagged_only_when_there_is_one(self):
        self.assertIn("has-backup", taxonomy.tags(self.channel(streams=[{}, {}])))
        self.assertNotIn("has-backup", taxonomy.tags(self.channel(streams=[{}])))

    def test_an_unknown_height_adds_no_quality_tag(self):
        self.assertNotIn("sd", taxonomy.tags(self.channel(height=0)))


if __name__ == "__main__":
    unittest.main()
