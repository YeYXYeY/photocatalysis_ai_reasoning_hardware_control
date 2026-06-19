# Mobile Robot

This repository now uses a single executable entry point: [`main.py`](./main.py). All device communication and workflow logic live in internal modules so the top level stays small and easier to maintain.

## Structure

- `main.py`: the only CLI entry point for robot, AGV, and workflow commands
- `devices/`: reusable clients and shared configuration for the CR10 robot arm and Trans200 AGV
- `workflows/`: predefined multi-device workflows
- `tests/`: `unittest` coverage for the CLI parser and workflow ordering

## Requirements

- Python 3.10 or newer
- `requests`

## Usage

Enable the robot:

```bash
python main.py robot enable
```

Run a robot-side script:

```bash
python main.py robot run-script pipetting
```

Move the AGV to a named marker:

```bash
python main.py agv move weighing
```

Run the default photocatalysis workflow:

```bash
python main.py workflow photocatalysis
```

## Notes

- The CLI opens device connections only when a command is executed.
- Marker IDs and mission payloads are centralized in [`devices/config.py`](./devices/config.py).
- The repository intentionally keeps only one runtime entry point to reduce duplication and accidental divergence.
