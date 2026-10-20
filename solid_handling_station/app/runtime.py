"""Explicit loading of station files and logging at runtime."""

from dataclasses import dataclass
from pathlib import Path
import time

import pandas as pd
import yaml

from utils.config import config_logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path):
    with Path(path).open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict):
        raise ValueError(f"Expected a configuration mapping in {path}.")
    return config


@dataclass
class StationRuntime:
    config: dict
    logger: object
    coordinates_dir: Path
    chemical_data_dir: Path
    tables: dict


def load_station_runtime(root=PROJECT_ROOT):
    root = Path(root)
    config = load_yaml(root / "utilities" / "config.yaml")
    settings = config.get("solid_weighing", {})
    required = {
        "z1_safe_pos",
        "z2_safe_pos",
        "y_safe_pos",
        "init_pos",
        "align_pos",
        "action_pos",
        "r_pos",
        "zero_pos",
    }
    if required - settings.keys():
        raise ValueError(f"Missing solid_weighing settings: {sorted(required - settings.keys())}")
    coordinates = root / "coordinates"
    tables = {
        name: pd.read_excel(coordinates / filename, sheet_name="Sheet1")
        for name, filename in {
            "database_df": "database.xlsx",
            "balance_coordinates_df": "balance.xlsx",
            "head_coordinates_df": "head.xlsx",
            "reaction_coordinates_df": "reaction.xlsx",
        }.items()
    }
    log_path = root / "logs" / (time.strftime("%Y%m%dT%H%M%S") + ".log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return StationRuntime(
        config, config_logger(log_path), coordinates, root / "chemical_data", tables
    )
