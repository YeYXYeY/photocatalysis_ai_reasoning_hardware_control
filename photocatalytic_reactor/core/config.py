"""Project configuration and logging helpers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    yaml = None


PROJECT_PATH = Path(__file__).resolve().parent.parent
Project_Path = str(PROJECT_PATH)


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load the project YAML configuration file."""
    if yaml is None:
        raise ModuleNotFoundError("PyYAML is required to load the project configuration.")
    resolved_path = Path(config_path) if config_path else PROJECT_PATH / "config.yaml"
    try:
        with resolved_path.open("r", encoding="utf-8") as stream:
            return yaml.safe_load(stream) or {}
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Configuration file not found: {resolved_path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Failed to parse configuration file: {resolved_path}") from exc


def config_logger(
    log_file_name: str | Path,
    logger_name: str = "photocatalytic_reactor",
) -> logging.Logger:
    """Create a project logger with console and file handlers.

    Repeated calls replace existing handlers so long-running sessions do not
    duplicate log lines.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    log_path = Path(log_file_name)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def load_config_and_logger(
    log_file_name: str | Path,
    config_path: str | Path | None = None,
    logger_name: str = "photocatalytic_reactor",
) -> tuple[dict[str, Any], logging.Logger]:
    """Load the YAML configuration and create a matching logger."""
    logger = config_logger(log_file_name, logger_name=logger_name)
    config = load_config(config_path)
    logger.info("Loaded configuration from %s", config_path or PROJECT_PATH / "config.yaml")
    return config, logger


if __name__ == "__main__":
    config, logger = load_config_and_logger(PROJECT_PATH / "logs" / "config_test.log")
    logger.info("Configuration loaded successfully: %s", config)
    print(config)
