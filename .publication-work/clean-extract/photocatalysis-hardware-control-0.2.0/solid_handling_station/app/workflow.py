"""Execute a validated dispensing plan using a supplied station instance."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from app.tasks import build_chemical_tasks


def run_weighing(dataframe, station, output_dir):
    tasks = build_chemical_tasks(dataframe)
    heads = set(station.head_coordinates_df["Chemical"])
    bottles = set(station.reaction_coordinates_df["NO"])
    if set(tasks) - heads:
        raise ValueError(f"Reagents missing from head coordinates: {sorted(set(tasks) - heads)}")
    requested = {number for task in tasks.values() for number in task["BottleNum"]}
    if requested - bottles:
        raise ValueError(
            f"Bottles missing from reaction coordinates: {sorted(requested - bottles)}"
        )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    actual = dataframe.copy()
    for chemical in tasks:
        actual[chemical] = pd.to_numeric(actual[chemical]).astype(float)
        actual.loc[actual[chemical] > 0, chemical] = float("nan")
    station.init_device()
    for chemical, task in tasks.items():
        positions = station.handle_weighing_head(chemical, 1)
        station.align_weighing_head(positions["init_pos"], positions["align_pos"])
        for bottle, target in zip(task["BottleNum"], task["TargetWeight"]):
            station.logger.info(
                "Weighing %s into bottle %s; target=%s mg", chemical, bottle, target
            )
            station.handle_sample_bottle(bottle, 1)
            mass = station.start_weighing(positions["align_pos"], positions["action_pos"], target)
            actual.loc[actual["NO"] == bottle, chemical] = mass
            actual.to_excel(output_dir / "actual_weight.xlsx", index=False)
            station.handle_sample_bottle(bottle, 2)
        station.handle_weighing_head(chemical, 2)
    station.motion.single_move("y", 1000)
    station.motion.single_move("x", 1000)
    return output_dir / "actual_weight.xlsx"


def default_output_dir(root):
    return Path(root) / "task" / datetime.now().strftime("%Y%m%dT%H%M%S%f")
