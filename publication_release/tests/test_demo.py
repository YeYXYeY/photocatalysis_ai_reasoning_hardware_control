import json
from pathlib import Path
import unittest

from tools.run_demo import build_summary


class DemoTests(unittest.TestCase):
    def test_real_splitter_matches_published_fixture(self):
        root = Path(__file__).resolve().parents[1]
        expected = json.loads((root / "examples/expected_demo_output.json").read_text())
        self.assertEqual(build_summary(), expected)
