# Setup and Startup Notes

This document summarizes how to prepare an environment for reading, testing, or cautiously running the retained station code.

## Scope

This repository is best understood as a supplementary research-code package rather than a one-command installable product.

You should expect:

- module-specific dependencies
- real-hardware assumptions
- machine-specific serial/network configuration
- sample spreadsheets and state files that may require local adaptation

## Recommended Python Environment

The root `pyproject.toml` currently exists mainly as a lightweight project marker and is not yet a complete source of truth for dependencies.

Recommended approach:

1. Use Python 3.10 for the published repository snapshot.
2. Create an isolated virtual environment at the repository root.
3. Install the root requirements file, then install any additional module-specific requirements if you are working on one station in detail.

Example:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
pip install -r automatic-control-system/requirements.txt
pip install -r liquid-handling-workstation/requirements.txt
pip install -r photocatalytic_reactor/requirements.txt
```

## Module Dependencies

### Control hub

`automatic-control-system/requirements.txt` currently lists:

- `pandas`
- `openpyxl`
- `PyYAML`
- `PyQt5`

### Liquid handling workstation

`liquid-handling-workstation/requirements.txt` currently lists:

- `pandas`
- `PyYAML`
- `pyserial`
- `crccheck`
- `requests`
- `numpy`
- `scipy`
- `scikit-learn`
- `matplotlib`

### Photocatalytic reactor

`photocatalytic_reactor/requirements.txt` currently lists:

- `matplotlib`
- `pandas`
- `pyserial`
- `PyYAML`

### Mobile robot

`mobile_robot/requirements.txt` currently lists:

- `requests`

## Configuration Files To Review First

Before running any hardware-facing code, review:

- `automatic-control-system/utils/config.yaml`
- `liquid-handling-workstation/utils/config.yaml`
- `liquid-handling-workstation/devices/config.yaml`
- `photocatalytic_reactor/config.yaml`
- `mobile_robot/devices/config.py`

These files may include hostnames, ports, markers, mission names, serial ports, and hardware-specific mappings.

## Startup Model

The repository suggests a distributed startup model:

- the control hub runs separately
- station servers may run on different machines or processes
- each station uses its own local drivers/configuration

## Representative Startup Commands

### Control hub workflow

From `automatic-control-system/`:

```bash
python main.py
```

This delegates into the retained sample workflow runner.

### Control hub UI

From `automatic-control-system/`:

```bash
python -m ui.main_ui
```

### Liquid handling workstation CLI

From `liquid-handling-workstation/`:

```bash
python main.py --func open_cap --taskfile task/task.xlsx
```

### Liquid handling workstation server

From `liquid-handling-workstation/`:

```bash
python liquid_station_server.py
```

### Mobile robot CLI

From `mobile_robot/`:

```bash
python main.py robot enable
python main.py agv move weighing
python main.py workflow photocatalysis
```

### Photocatalytic reactor

From `photocatalytic_reactor/`:

```bash
python main.py --func lighting
python main.py --func start_reactor
python main.py --func stop_reactor
```

## Recommended Safe Usage Modes

Depending on your goal, use one of these modes:

### Documentation-only mode

Read the code and retained spreadsheets without executing hardware code.

Best for:

- paper review
- architecture understanding
- supplementary-material inspection

### Logic/test mode

Run tests or pure-Python logic where available, while avoiding real hardware connections.

Best for:

- code cleanup
- regression checks
- refactoring with mock-based tests

### Hardware-attached mode

Run station code only after validating:

- serial device mappings
- network endpoints
- workbook formats
- motion coordinates
- emergency stop procedures

Best for:

- controlled lab use by people familiar with the platform

## Known Environment-Specific Details

Examples observed in the retained configuration:

- placeholder/documentation-safe IPs are used in the published network configuration files
- localhost values appear in some sample configs
- the reactor config includes Windows-style COM ports such as `COM6` and `COM7`

These values should be treated as examples unless you know they match your actual lab environment.

## Suggested Future Improvements

Further deployment-oriented improvements could still include:

- per-module `requirements-lock.txt` or `environment.yml`
- `config.example.yaml` templates
- a small startup script for documentation/demo mode
- a hardware safety checklist for live operation
