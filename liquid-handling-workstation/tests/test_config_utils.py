import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path


def build_fake_yaml_module():
    fake_yaml = types.ModuleType("yaml")

    class FakeYAMLError(Exception):
        pass

    def safe_load(stream):
        text = stream.read().strip()
        if text == "trigger-yaml-error":
            raise FakeYAMLError("Invalid YAML content.")

        data = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
        return data

    fake_yaml.safe_load = safe_load
    fake_yaml.YAMLError = FakeYAMLError
    return fake_yaml


class ConfigUtilsTests(unittest.TestCase):
    def load_module(self):
        sys.modules["yaml"] = build_fake_yaml_module()
        sys.modules.pop("utils.config", None)
        return importlib.import_module("utils.config")

    def test_build_timestamped_log_path_uses_directory_and_timestamp(self):
        config_module = self.load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = config_module.build_timestamped_log_path(
                Path(temp_dir) / "logs",
                timestamp="202606182130",
            )

        self.assertTrue(str(log_path).endswith("logs\\202606182130.log"))

    def test_config_logger_replaces_existing_handlers(self):
        config_module = self.load_module()
        logger_name = "tests.runtime"

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "runtime.log"
            logger = config_module.config_logger(log_file, logger_name=logger_name)
            original_handlers = tuple(logger.handlers)

            logger = config_module.config_logger(log_file, logger_name=logger_name)
            self.assertEqual(len(logger.handlers), 2)
            self.assertEqual(logger.handlers[0].__class__.__name__, "StreamHandler")
            self.assertEqual(logger.handlers[1].__class__.__name__, "FileHandler")
            self.assertNotEqual(tuple(logger.handlers), original_handlers)

            for handler in list(logger.handlers):
                handler.close()
                logger.removeHandler(handler)
            logger.propagate = True

    def test_load_config_reads_yaml_from_requested_path(self):
        config_module = self.load_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text('port: "COM7"\nmode: active\n', encoding="utf-8")

            config = config_module.load_config(config_path)

        self.assertEqual(config["port"], "COM7")
        self.assertEqual(config["mode"], "active")


if __name__ == "__main__":
    unittest.main()
