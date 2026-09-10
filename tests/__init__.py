"""Put scripts/ on the import path so the tests can be discovered from the repository root.

The scripts import each other by bare name (`import taxonomy`) because they are run as
`python scripts/build.py`, which puts scripts/ on the path automatically. Discovery from
the root does not, so it is arranged here rather than in every test module.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
