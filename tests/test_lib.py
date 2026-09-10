"""Reading other people's playlists, which is how candidate streams arrive, and the
round trip through the ones this project writes."""
import unittest

import lib


class ParseM3u(unittest.TestCase):
    def test_attributes_title_and_url(self):
        text = ('#EXTM3U\n'
                '#EXTINF:-1 tvg-id="IRIB1.ir" tvg-quality="FHD",IRIB TV1\n'
                'https://a.com/x.m3u8\n')
        (attrs, title, url), = lib.parse_m3u(text)
        self.assertEqual(attrs["tvg-id"], "IRIB1.ir")
        self.assertEqual(attrs["tvg-quality"], "FHD")
        self.assertEqual(title, "IRIB TV1")
        self.assertEqual(url, "https://a.com/x.m3u8")

    def test_player_options_between_the_entry_and_its_url_are_skipped(self):
        text = ('#EXTINF:-1 tvg-id="a",A\n'
                '#EXTVLCOPT:http-user-agent=UA/1\n'
                '#EXTVLCOPT:http-referrer=https://ref\n'
                'https://a.com/x.m3u8\n')
        (_, _, url), = lib.parse_m3u(text)
        self.assertEqual(url, "https://a.com/x.m3u8")

    def test_blank_lines_are_tolerated(self):
        text = '#EXTINF:-1 tvg-id="a",A\n\n\nhttps://a.com/x.m3u8\n'
        self.assertEqual(len(list(lib.parse_m3u(text))), 1)

    def test_a_title_containing_a_comma_survives(self):
        text = '#EXTINF:-1 tvg-id="a",Channel, the second\nhttps://a.com/x.m3u8\n'
        (_, title, _), = lib.parse_m3u(text)
        self.assertEqual(title, "Channel, the second")

    def test_a_trailing_entry_with_no_url_is_not_yielded(self):
        text = '#EXTINF:-1 tvg-id="a",A\nhttps://a.com/x.m3u8\n#EXTINF:-1 tvg-id="b",B\n'
        self.assertEqual([t for _, t, _ in lib.parse_m3u(text)], ["A"])

    def test_several_entries(self):
        text = ('#EXTM3U\n'
                '#EXTINF:-1 tvg-id="a",A\nhttps://a.com/1.m3u8\n'
                '#EXTINF:-1 tvg-id="b",B\nhttps://a.com/2.m3u8\n')
        self.assertEqual([t for _, t, _ in lib.parse_m3u(text)], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
