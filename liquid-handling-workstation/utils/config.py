import logging
import time
from pathlib import Path

import yaml


def ensure_directory(path):
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def build_timestamped_log_path(log_dir, timestamp=None):
    current_time = timestamp or time.strftime("%Y%m%d%H%M", time.localtime())
    return ensure_directory(log_dir) / f"{current_time}.log"


def config_logger(log_file_name, logger_name=None):
    """Create a file-backed logger without duplicating handlers."""
    log_path = Path(log_file_name)
    ensure_directory(log_path.parent)

    logger = logging.getLogger(logger_name or f"liquid_workstation.{log_path.stem}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def load_config(config_file_path=None, *, logger=None):
    config_path = (
        Path(config_file_path)
        if config_file_path
        else Path(__file__).with_name("config.yaml")
    )
    active_logger = logger or logging.getLogger("liquid_workstation.config")
    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            active_logger.info("Loaded configuration from '%s'.", config_path)
    except FileNotFoundError:
        active_logger.error("Configuration file '%s' was not found.", config_path)
        raise
    except yaml.YAMLError as e:
        active_logger.error("Failed to parse configuration '%s': %s", config_path, e)
        raise

    return config or {}


if __name__ == "__main__":
    config = load_config()
    print(config)
