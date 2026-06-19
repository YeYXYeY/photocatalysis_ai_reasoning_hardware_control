# Liquid Handling Workstation

This repository contains the control code, a reduced sample task set, coordinate workbooks, and service entrypoints used by a liquid handling workstation and its related automation stations.

## Maintained Runtime Path

The current runtime path is centered around these files:

- `main.py`: command-line entrypoint for liquid station tasks
- `devices/liquid_station.py`: main liquid workstation orchestration logic
- `devices/controller.py`: Ethernet motion controller wrapper
- `devices/rs485.py`: RS485 serial wrapper for pumps and grippers
- `devices/motion.py`: lower-level motion driver helper
- `liquid_station_server.py`: socket server entrypoint for remote task execution

## Repository Layout

- `devices/`: hardware wrappers and workstation orchestration
- `server/`: socket-based station servers
- `client/`: station metadata and client helpers
- `coordinates/`: workbook-based coordinate tables used by the hardware flows
- `task/`: curated sample task workbooks retained for documentation and supplementary review
- `utils/`: shared helpers such as logging, config loading, and task utilities
- `main/`, `main_*.py`, `test/`, `test1203/`: historical scripts and experiments

## Configuration

Primary device configuration lives in:

- `devices/config.yaml`
- `utils/config.yaml`

Runtime logs are generated locally during execution but are not retained in this publication-oriented snapshot.

## Running the CLI

Run a liquid station function with one of the retained sample task workbooks:

```bash
python main.py --func open_cap --taskfile task/task.xlsx
```

Supported CLI functions are defined in `main.py` and currently include:

- `open_cap`
- `prepare_solution`
- `pre_nmr_test`
- `post_nmr_test`
- `close_cap`
- `tip_rack_out`
- `tip_rack_back`
- `replace_reactants`

## Running the Server

Start the liquid station socket server with:

```bash
python liquid_station_server.py
```

The server creates `log/` and `task/` directories next to the entry script when needed.

## Notes

- This project drives real hardware. Avoid broad refactors without reviewing the device flow carefully.
- Many spreadsheet files in the repository are operational data, not source code.
- The publication-oriented snapshot intentionally removes runtime clutter and keeps the maintained runtime path as the main focus for readers.
