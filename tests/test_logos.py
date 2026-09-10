import pathlib
import sys
import tempfile
import unittest
from unittest import mock

import logos


class LogoRetention(unittest.TestCase):
    def test_mirror_keeps_a_logo_without_a_current_stream_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            asset = pathlib.Path(directory) / "PrivateChannel.png"
            asset.write_bytes(b"existing logo")
            with mock.patch.object(logos, "ASSETS", asset.parent), \
                    mock.patch.object(sys, "argv", ["logos.py", "--mirror"]), \
                    mock.patch.object(logos, "read_json", side_effect=([], {})), \
                    mock.patch.object(logos, "install_public_dns"), \
                    mock.patch.object(logos, "mirror") as mirror:
                logos.main()
            self.assertTrue(asset.exists())
            self.assertIn("PrivateChannel", mirror.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
