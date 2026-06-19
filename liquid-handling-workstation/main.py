import argparse
from pathlib import Path

import pandas as pd

from devices.liquid_station import LiquidStation


COMMAND_CHOICES = (
    "open_cap",
    "prepare_solution",
    "pre_nmr_test",
    "post_nmr_test",
    "close_cap",
    "tip_rack_out",
    "tip_rack_back",
    "replace_reactants",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Execute a liquid station function against the provided task workbook."
        )
    )
    parser.add_argument(
        "--func",
        type=str,
        choices=COMMAND_CHOICES,
        required=True,
        help="Function to execute.",
    )
    parser.add_argument(
        "--taskfile",
        type=str,
        required=True,
        help="Path to the task workbook.",
    )
    return parser.parse_args()


def load_task_dataframe(task_file):
    return pd.read_excel(Path(task_file))


def build_reactant_dict(task_df):
    return pd.Series(task_df.Value.values, index=task_df.Key.values).to_dict()


def execute_station_command(liquid_station, func, task_df):
    command_handlers = {
        "open_cap": lambda: liquid_station.open_cap(),
        "prepare_solution": lambda: liquid_station.prepare_solution(),
        "pre_nmr_test": lambda: liquid_station.pre_nmr_test(),
        "post_nmr_test": lambda: liquid_station.post_nmr_test(),
        "close_cap": lambda: liquid_station.close_cap(),
        "tip_rack_out": lambda: liquid_station.handle_tip_rack(1),
        "tip_rack_back": lambda: liquid_station.handle_tip_rack(2),
        "replace_reactants": lambda: liquid_station.replace_reactants(
            build_reactant_dict(task_df)
        ),
    }

    if func not in command_handlers:
        raise ValueError(f"Unknown function: {func}")

    liquid_station.logger.info("Running function '%s'.", func)
    command_handlers[func]()


def main():
    args = parse_args()
    task_file = Path(args.taskfile)
    task_df = load_task_dataframe(task_file)

    liquid_station = LiquidStation(task_df=task_df)
    liquid_station.logger.info("Liquid station initialized.")
    liquid_station.logger.info(
        "Received function '%s' for task file '%s'.", args.func, task_file
    )

    execute_station_command(liquid_station, args.func, task_df)


if __name__ == "__main__":
    main()
