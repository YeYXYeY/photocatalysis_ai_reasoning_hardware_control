"""Demonstrate the actual hub task splitter and accounting logic, without I/O to devices."""

import argparse
import importlib.util
import json
from pathlib import Path
import tempfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def build_summary():
    module_path = ROOT / "automatic-control-system" / "utils" / "task_processing.py"
    spec = importlib.util.spec_from_file_location("demo_task_processing", module_path)
    processing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(processing)
    fixture = json.loads((ROOT / "examples" / "demo_task.json").read_text(encoding="utf-8"))
    columns = list(dict.fromkeys(processing.LIQUID_TASK_COLUMNS + processing.SOLID_TASK_COLUMNS))
    dataframe = pd.DataFrame(fixture).reindex(columns=columns, fill_value=0.0)
    with tempfile.TemporaryDirectory(prefix="photocatalysis-demo-") as directory:
        workbook = Path(directory) / "task.xlsx"
        dataframe.to_excel(workbook, index=False)
        solid, liquid = processing.split_task(workbook)
    # Match the station rule: all-zero reagent rows request no action.
    solid = solid.loc[solid.drop(columns="NO").fillna(0).ne(0).any(axis=1)]
    liquid = liquid.loc[liquid.drop(columns="NO").fillna(0).ne(0).any(axis=1)]
    liquid_totals = processing.calculate_liquid_consumption(liquid)
    solid_totals = processing.calculate_solid_consumption(solid)
    return {
        "mode": "software-only",
        "input_kind": "synthetic illustration; not manuscript experimental data",
        "bottle_ids": dataframe["NO"].astype(int).tolist(),
        "liquid_task_rows": len(liquid),
        "solid_task_rows": len(solid),
        "liquid_consumption_uL": {k: float(v) for k, v in sorted(liquid_totals.items()) if v},
        "solid_consumption_mg": {k: float(v) for k, v in sorted(solid_totals.items()) if v},
        "hardware_commands_sent": 0,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optionally save the JSON report.")
    args = parser.parse_args(argv)
    summary = build_summary()
    expected = json.loads(
        (ROOT / "examples" / "expected_demo_output.json").read_text(encoding="utf-8")
    )
    if summary != expected:
        raise RuntimeError("Demo output does not match the supplied reference output.")
    report = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
