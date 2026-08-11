"""Category assignment and the resolution label, both of which are documented as a fixed
rule order, so the order is what is worth testing rather than any single channel."""
import unittest

import taxonomy


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

    def test_an_unknown_channel_falls_back(self):
        self.assertEqual(taxonomy.classify("X.ir", ["nothing-we-map"], {}), taxonomy.FALLBACK)

    def test_every_category_a_rule_can_produce_is_declared(self):
        produced = ({c for _, c in taxonomy.SET_RULES} | set(taxonomy.GENRE_MAP.values())
                    | {"religious-islamic", taxonomy.FALLBACK})
        self.assertTrue(produced <= set(taxonomy.LABELS), produced - set(taxonomy.LABELS))


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
