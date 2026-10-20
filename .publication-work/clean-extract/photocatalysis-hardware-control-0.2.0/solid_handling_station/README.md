# Solid dispensing station

This module contains the supplied active solid weighing implementation. It is included in this release; the earlier documentation-only station placeholder is obsolete.

## Structure

- `app/`: task validation, explicit runtime loading, and station-independent workflow execution.
- `devices/`: serial stepper/gripper and balance interfaces.
- `utilities/`: coarse/fine dispensing logic, CRC utilities, configuration compatibility API, and optional incremental regression calibration.
- `coordinates/`: balance, head, bottle/reaction, and dispensing reference tables.
- `tests/`: isolated regression tests using local tables and simulated hardware.

## Usage

Install the root dependency set and run from **this directory**:

```powershell
python main.py --help
python -m unittest discover -s tests -v
```

A configured physical run uses `python main.py --taskfile ../examples/operational_tasks/solid_task.xlsx --func weighing`. `start_weighing` is an alias. A task workbook requires unique positive integer `NO` values and reagent columns matching `coordinates/head.xlsx`; target masses are in mg. Blank and zero targets request no action, negative/nonfinite/nonnumeric targets are rejected.

The runtime validates the task before initialization, constructs the serial devices explicitly, and checkpoints measured masses in `task/<run-id>/actual_weight.xlsx` (or `--output-dir`). Active cells awaiting measurement are blank. The inherited instrument settling/polling logic still depends on laboratory behavior; offline tests do not establish its real-device timing.

`python solid_station_server.py` starts the TCP service using addresses in `client/station_info.py`. Only weighing functions are implemented by the CLI. Hub-advertised rack-transfer functions require separate validated implementation.

`devices/config.yaml` configures serial devices; `utilities/config.yaml` supplies dispensing and clearance settings. Both are retained examples. The optional `utilities/dynamic_linear_regression.py` helper is not used by the active weighing loop, includes no trained state, and can use an explicit seed for new calibration work. Read `../docs/HARDWARE.md` before attaching equipment.
