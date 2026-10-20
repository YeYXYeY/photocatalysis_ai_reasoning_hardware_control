from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from utils.config import build_timestamped_log_path, config_logger, load_config


COORDINATE_WORKBOOK_NAMES = {
    "reagent_df": "reagent.xlsx",
    "gripper_df": "gripper.xlsx",
    "reaction_for_pump_df": "reaction_for_pump.xlsx",
    "reaction_for_pump2_df": "reaction_for_pump2.xlsx",
    "slot_for_pump_df": "slot_for_pump.xlsx",
    "dosing_head_df": "dosing_head.xlsx",
    "tip_for_gripper_df": "tip_for_gripper.xlsx",
    "reaction_for_dosing_df": "reaction_for_dosing.xlsx",
    "slot_for_gripper_df": "slot_for_gripper.xlsx",
    "clean_for_gripper_df": "clean_for_gripper.xlsx",
    "nmr_prepare_df": "nmr_prepare.xlsx",
    "reaction_for_gripper_df": "reaction_for_gripper.xlsx",
    "tip_for_pump_df": "tip_for_pump.xlsx",
}


@dataclass(frozen=True)
class LiquidStationPaths:
    devices_dir: Path
    project_root: Path
    log_dir: Path
    coordinates_dir: Path
    config_path: Path
    tip_for_pump_path: Path
    tip_for_gripper_path: Path


def build_liquid_station_paths(devices_dir=None):
    devices_path = Path(devices_dir or Path(__file__).resolve().parent)
    project_root = devices_path.parent
    coordinates_dir = project_root / "coordinates"
    return LiquidStationPaths(
        devices_dir=devices_path,
        project_root=project_root,
        log_dir=project_root / "log",
        coordinates_dir=coordinates_dir,
        config_path=devices_path / "config.yaml",
        tip_for_pump_path=coordinates_dir / "tip_for_pump.xlsx",
        tip_for_gripper_path=coordinates_dir / "tip_for_gripper.xlsx",
    )


def build_coordinate_workbook_paths(paths: LiquidStationPaths):
    return {
        table_name: paths.coordinates_dir / workbook_name
        for table_name, workbook_name in COORDINATE_WORKBOOK_NAMES.items()
    }


def load_coordinate_tables(paths: LiquidStationPaths):
    workbook_paths = build_coordinate_workbook_paths(paths)
    return {
        table_name: pd.read_excel(workbook_path)
        for table_name, workbook_path in workbook_paths.items()
    }


def build_runtime_logger(paths: LiquidStationPaths, *, timestamp=None):
    log_file = build_timestamped_log_path(paths.log_dir, timestamp=timestamp)
    return config_logger(log_file, logger_name="liquid_workstation.runtime")


def load_runtime_config(paths: LiquidStationPaths, *, logger=None):
    return load_config(paths.config_path, logger=logger)
