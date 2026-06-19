import logging
import os
import time

import yaml


def config_logger(log_file_name):
    """
    Configure logging for both the console and a log file.

    Args:
        log_file_name: Destination log file name.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file_name, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    return logger


def load_config():
    """Load the YAML configuration next to this module."""
    current_time = time.strftime("%Y%m%d%H%M", time.localtime())
    logger = config_logger(f"{current_time}.log")
    current_path = os.path.abspath(os.path.dirname(__file__))
    config_file_path = os.path.join(current_path, "config.yaml")

    try:
        with open(config_file_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            logger.info(f"Loaded configuration file: {config_file_path}.")
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_file_path}.")
        raise
    except yaml.YAMLError as error:
        logger.error(f"Failed to parse configuration file {config_file_path}: {error}")
        raise

    return config


if __name__ == "__main__":
    config = load_config()
    print(config)
