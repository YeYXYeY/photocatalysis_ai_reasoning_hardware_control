"""Compatibility API for the solid station configuration and logger."""

from pathlib import Path
from utils.config import config_logger, load_config


def load_config_and_logger(log_file_name):
    logger = config_logger(log_file_name)
    return load_config(Path(__file__).with_name("config.yaml"), logger=logger), logger
