# System architecture

## Data and control flow

1. The control hub loads a workbook, splits liquid/solid tasks, and computes inventory needs.
2. The hub sends station task tables as split-orient JSON and commands over TCP. Station services save received tables as Excel files.
3. Liquid and solid stations execute local task workflows through motion/serial drivers and coordinate tables. The reactor runs lighting, shaking and temperature/cooling logic.
4. The mobile module invokes robot-side programs and AGV missions for transport. YAML and Excel files store station state, coordinates, and inventory.

The host software does not supply all robot-side scripts, AGV maps, firmware, or a complete matching command adapter for every historical hub command. See `docs/HARDWARE.md` for the precise boundary.

## Process structure

The five station/hub directories are intentionally separate process roots. Their `devices`, `utils`, `server`, and `client` names must not be combined on one global import path. Root tools load only the pure task-processing module by file path, or run isolated station subprocesses.

Within the solid station, `app/tasks.py` handles hardware-free validation, `app/runtime.py` loads configuration/workbooks explicitly, `app/workflow.py` executes validated tasks through a supplied station instance, and `utilities/solid_weigh.py` preserves dispensing/control logic. Constructing a station opens devices; importing its workflow module does not.

## Persistent assets

- Coordinate workbooks: machine-specific motion positions and head/reagent mappings.
- Station-status workbooks and YAML: representative mutable inventory and rack states; copy before a physical run.
- Operational task examples: retained inputs of unknown manuscript relevance, separate from synthetic demo data.
- Generated outputs: logs, measured solid masses, fitted calibration pickle files, and reactor plots remain local and are excluded from upload packages.

These controller-side socket protocols are legacy laboratory protocols. Configure them only in the intended controlled laboratory network. The offline demo bypasses socket services entirely.
