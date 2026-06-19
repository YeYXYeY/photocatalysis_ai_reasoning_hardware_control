import os

import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NMR_PREPARE_FILE_PATH = os.path.join(
    PROJECT_ROOT, "station_status", "nmr_prepare.xlsx"
)

LIQUID_TASK_COLUMNS = [
    "NO",
    "A1",
    "A2",
    "B1",
    "C1",
    "C2",
    "C3",
    "C4",
    "C5",
    "C6",
    "C7",
    "C8",
    "D1",
    "E1",
    "E2",
    "E3",
    "E4",
    "G1",
    "G2",
    "G3",
    "G4",
    "H1",
    "H2",
    "H3",
    "H4",
    "J1",
    "J2",
    "J3",
    "J4",
    "J5",
    "J6",
    "J7",
    "J8",
]

SOLID_TASK_COLUMNS = ["NO", "F1", "F2", "F3", "I1", "I2", "I3"]

EMPTY_NMR_CONSUMPTION = {
    "A1": 0.0,
    "A2": 0.0,
    "B1": 0.0,
    "C1": 0.0,
    "C2": 0.0,
    "C3": 0.0,
    "C4": 0.0,
    "C5": 0.0,
    "C6": 0.0,
    "C7": 0.0,
    "C8": 0.0,
    "E1": 0.0,
    "E2": 0.0,
    "E3": 0.0,
    "E4": 0.0,
    "G1": 0.0,
    "G2": 0.0,
    "G3": 0.0,
    "G4": 0.0,
    "H1": 0.0,
    "H2": 0.0,
    "H3": 0.0,
    "H4": 0.0,
    "J1": 0.0,
    "J2": 0.0,
    "J3": 0.0,
    "J4": 0.0,
    "J5": 0.0,
    "J6": 0.0,
    "J7": 0.0,
    "J8": 0.0,
}


def split_task(file_path):
    """
    Split an Excel task sheet into liquid-station and solid-station task tables.

    Args:
        file_path: Path to the task Excel file.

    Returns:
        Tuple of `(solid_task_df, liquid_task_df)`.
    """
    dataframe = pd.read_excel(file_path)
    missing_liquid_columns = [
        column for column in LIQUID_TASK_COLUMNS if column not in dataframe.columns
    ]
    missing_solid_columns = [
        column for column in SOLID_TASK_COLUMNS if column not in dataframe.columns
    ]

    if missing_liquid_columns:
        raise ValueError(
            "The task file is missing liquid-station columns: "
            f"{missing_liquid_columns}"
        )
    if missing_solid_columns:
        raise ValueError(
            "The task file is missing solid-station columns: "
            f"{missing_solid_columns}"
        )

    solid_task_df = dataframe[SOLID_TASK_COLUMNS].dropna(
        subset=SOLID_TASK_COLUMNS[1:], how="all"
    )
    liquid_task_df = dataframe[LIQUID_TASK_COLUMNS].dropna(
        subset=LIQUID_TASK_COLUMNS[1:], how="all"
    )
    return solid_task_df, liquid_task_df


def calculate_liquid_consumption(liquid_task_df, mode=0):
    """
    Calculate liquid-station reagent consumption.

    Args:
        liquid_task_df: Task DataFrame for the liquid station.
        mode: `0` calculates solution-preparation consumption.
            `1` calculates the NMR-preparation consumption profile.
    """
    if mode == 0:
        liquid_consumption = liquid_task_df.drop(columns=["NO", "D1"]).sum(axis=0)
        liquid_consumption = liquid_consumption.to_dict()
        liquid_consumption.update({"G5": 0.0, "G6": 0.0})
        return liquid_consumption

    if mode == 1:
        task_count = len(liquid_task_df)
        nmr_prepare_df = pd.read_excel(NMR_PREPARE_FILE_PATH).head(task_count)
        nmr_consumption = nmr_prepare_df.drop(columns=["NO"]).sum(axis=0).to_dict()
        liquid_consumption = dict(EMPTY_NMR_CONSUMPTION)
        liquid_consumption.update(nmr_consumption)
        return liquid_consumption

    raise ValueError(f"Unsupported liquid consumption mode: {mode}")


def calculate_solid_consumption(solid_task_df):
    """
    Calculate solid-station reagent consumption.

    Args:
        solid_task_df: Task DataFrame for the solid station.
    """
    return solid_task_df.drop(columns=["NO"]).sum(axis=0).to_dict()
