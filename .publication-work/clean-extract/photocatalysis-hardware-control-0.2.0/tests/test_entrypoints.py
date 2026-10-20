from pathlib import Path
import subprocess
import sys
import unittest


class EntrypointTests(unittest.TestCase):
    def test_all_station_help_commands_work_without_hardware(self):
        root = Path(__file__).resolve().parents[1]
        for name in [
            "automatic-control-system",
            "liquid-handling-workstation",
            "mobile_robot",
            "photocatalytic_reactor",
            "solid_handling_station",
        ]:
            with self.subTest(station=name):
                result = subprocess.run(
                    [sys.executable, "main.py", "--help"],
                    cwd=root / name,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("usage:", result.stdout.lower())
