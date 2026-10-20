from pathlib import Path
import tempfile
import unittest

from tools.validate_release import audit, release_files


class ArchiveRuleTests(unittest.TestCase):
    def test_payload_excludes_local_state_and_keeps_example_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in [
                "source.py",
                "examples/operational_tasks/task.xlsx",
                "logs/run.log",
                ".venv/secret.py",
                "__pycache__/x.pyc",
            ]:
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("")
            names = {p.relative_to(root).as_posix() for p in release_files(root)}
            self.assertEqual(names, {"source.py", "examples/operational_tasks/task.xlsx"})

    def test_detects_embedded_credentials_and_invalid_python(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "credentials.py").write_text('api_key = "synthetic-test-value"')
            (root / "broken.py").write_text("def invalid(")
            issues = audit(root)["issues"]
            self.assertTrue(any("credential" in issue for issue in issues))
            self.assertTrue(any("syntax" in issue for issue in issues))
