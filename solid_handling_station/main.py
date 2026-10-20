"""Command-line entrypoint. Device imports occur only after task validation."""

import argparse
from pathlib import Path

import pandas as pd

from app.tasks import build_chemical_tasks


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Execute a solid dispensing task (target masses in mg)."
    )
    parser.add_argument(
        "--taskfile", type=Path, required=True, help="Task workbook with NO and reagent columns."
    )
    parser.add_argument("--func", choices=("weighing", "start_weighing"), default="weighing")
    parser.add_argument("--output-dir", type=Path, help="Directory for measured mass output.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    dataframe = pd.read_excel(args.taskfile)
    build_chemical_tasks(dataframe)
    from app.workflow import default_output_dir, run_weighing
    from utilities.solid_weigh import SolidWeigh

    output = args.output_dir or default_output_dir(Path(__file__).parent)
    station = SolidWeigh()
    try:
        print(run_weighing(dataframe, station, output))
    finally:
        station.weighing.close()
        if station.motion.ser.is_open:
            station.motion.ser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
