"""Deduplication, which decides whether two entries are the same stream or channel.

Getting this wrong is quiet in both directions: too eager and a channel loses its backup,
too shy and the same stream is published three times.
"""
import unittest

import identity


class CanonicalUrl(unittest.TestCase):
    def test_cosmetic_differences_collapse(self):
        same = [
            "https://cdn.example.com/live/index.m3u8",
            "https://CDN.example.com/live/index.m3u8",
            "https://cdn.example.com:443/live/index.m3u8",
            "https://cdn.example.com/live/index.m3u8/",
            "https://www.cdn.example.com/live/index.m3u8",
            "https://cdn.example.com//live//index.m3u8",
            "  https://cdn.example.com/live/index.m3u8  ",
        ]
        self.assertEqual(len({identity.canonical_url(url) for url in same}), 1)

    def test_http_and_https_are_one_stream(self):
        self.assertEqual(identity.canonical_url("http://a.com/x.m3u8"),
                         identity.canonical_url("https://a.com/x.m3u8"))

    def test_session_parameters_are_ignored_but_real_ones_are_kept(self):
        self.assertEqual(identity.canonical_url("https://a.com/x.m3u8?token=abc&ts=12"),
                         identity.canonical_url("https://a.com/x.m3u8?token=zzz&ts=99"))
        self.assertNotEqual(identity.canonical_url("https://a.com/x.m3u8?channel=1"),
                            identity.canonical_url("https://a.com/x.m3u8?channel=2"))

    def test_query_order_does_not_matter(self):
        self.assertEqual(identity.canonical_url("https://a.com/x?b=2&a=1"),
                         identity.canonical_url("https://a.com/x?a=1&b=2"))

    def test_different_hosts_stay_apart(self):
        self.assertNotEqual(identity.canonical_url("https://edge1.example.com/x.m3u8"),
                            identity.canonical_url("https://edge2.example.com/x.m3u8"))


class NormaliseName(unittest.TestCase):
    def test_noise_words_are_dropped(self):
        self.assertEqual(identity.normalise_name("IRIB TV 1 HD"),
                         identity.normalise_name("IRIB 1"))

    def test_a_glued_token_is_left_alone(self):
        # "TV1" is one token, so the noise list cannot reach inside it. Names arrive from
        # the database and rarely differ this way, and splitting on digits would merge
        # channels that genuinely differ by number.
        self.assertEqual(identity.normalise_name("IRIB TV1 HD"), "irib tv1")

    def test_arabic_letter_forms_fold_to_the_persian_ones(self):
        self.assertEqual(identity.normalise_name("شبكة يك"), identity.normalise_name("شبکه یک"))

    def test_a_zero_width_non_joiner_reads_as_a_word_break(self):
        self.assertEqual(identity.normalise_name("آی\u200cفیلم"),
                         identity.normalise_name("ای فیلم"))

    def test_country_words_are_kept_apart(self):
        # "Iran Press" and "Press TV" are different channels, so Iran must not be noise.
        self.assertNotEqual(identity.normalise_name("Iran Press"),
                            identity.normalise_name("Press TV"))

    def test_empty_name(self):
        self.assertEqual(identity.normalise_name(""), "")
        self.assertEqual(identity.normalise_name(None), "")


class ChannelKey(unittest.TestCase):
    def test_the_database_id_wins(self):
        self.assertEqual(identity.channel_key("IRIB1.ir", "anything at all", "IR"), "id:IRIB1.ir")

    def test_without_an_id_the_name_groups_channels(self):
        self.assertEqual(identity.channel_key(None, "IRIB TV 1 HD", "IR"),
                         identity.channel_key(None, "IRIB 1", "IR"))

    def test_same_name_in_another_country_is_another_channel(self):
        self.assertNotEqual(identity.channel_key(None, "Kanal 1", "IR"),
                            identity.channel_key(None, "Kanal 1", "TR"))

    def test_a_nameless_entry_has_no_key(self):
        self.assertIsNone(identity.channel_key(None, "", "IR"))


class DedupeStreams(unittest.TestCase):
    def test_the_first_of_each_endpoint_is_kept(self):
        streams = [
            {"url": "https://a.com/x.m3u8", "score": 90},
            {"url": "http://a.com/x.m3u8/", "score": 50},
            {"url": "https://b.com/y.m3u8", "score": 10},
        ]
        kept = identity.dedupe_streams(streams)
        self.assertEqual([s["url"] for s in kept],
                         ["https://a.com/x.m3u8", "https://b.com/y.m3u8"])


if __name__ == "__main__":
    unittest.main()
