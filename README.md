# Photocatalysis AI Reasoning Hardware Control

This repository contains the control software and representative sample data for an automated photocatalysis platform composed of a central automation control hub, several published hardware-facing modules, and one documentation-only unpublished station placeholder.

The codebase is organized as a paper-oriented supplementary repository: it preserves the main control logic, representative task/state files, and station-level entrypoints needed to understand the system architecture, while still reflecting that the original platform depends on real hardware, lab networking, and machine-specific configuration.

## System Overview

The platform includes the following main published modules:

- `automatic-control-system/`: the central orchestration and monitoring hub. It manages task decomposition, station scheduling, inventory/status bookkeeping, and the UI/dashboard.
- `liquid-handling-workstation/`: the liquid handling station responsible for pipetting, capping, reagent preparation, and related liquid operations.
- `mobile_robot/`: the mobile transport module used to coordinate the CR10 robot arm and the Trans200 AGV.
- `photocatalytic_reactor/`: the photocatalytic reactor control module, including lighting, shaking, and cooling-related runtime logic.

The original platform also includes a solid handling station. Its implementation is referenced throughout the workflow and communication logic, but its source code is intentionally not included in this repository because of conflict-of-interest constraints. A documentation-only placeholder is provided in `solid-handling-station/`.

Some retained compatibility code paths also reference a peptide station, but no standalone peptide-station module is published in this repository snapshot.

In a typical run, the control hub reads a task workbook, splits the workflow into station-level actions, communicates with individual stations over socket-style station servers, and tracks status/inventory using YAML and spreadsheet-backed state files.

## Repository Layout

```text
.
├─ README.md
├─ SYSTEM_ARCHITECTURE.md
├─ SETUP.md
├─ REPRODUCE.md
├─ LICENSE
├─ requirements.txt
├─ pyproject.toml
├─ automatic-control-system/
├─ liquid-handling-workstation/
├─ mobile_robot/
├─ photocatalytic_reactor/
└─ solid-handling-station/
```

## Module Summary

### `automatic-control-system/`

Key responsibilities:

- workflow orchestration
- station status tracking
- inventory/replenishment bookkeeping
- UI/dashboard and station communication

Representative entrypoints:

- `main.py`
- `workflow/run_sample_workflow.py`
- `server/*.py`
- `ui/main_ui.py`

Representative retained data:

- `task/0923task.xlsx`
- `station_status/station_status.yaml`
- `station_status/initial_status.yaml`
- `station_status/*.xlsx`

### `liquid-handling-workstation/`

Key responsibilities:

- task-driven liquid handling execution
- motion control and RS485-connected peripheral control
- coordinate-table-driven hardware actions
- remote execution through a socket server

Representative entrypoints:

- `main.py`
- `liquid_station_server.py`

Representative retained data:

- `coordinates/*.xlsx`
- `task/*.xlsx`
- `devices/config.yaml`
- `utils/config.yaml`

### `mobile_robot/`

Key responsibilities:

- CR10 robot arm control
- Trans200 AGV control
- predefined robot + AGV workflows

Representative entrypoint:

- `main.py`

### `photocatalytic_reactor/`

Key responsibilities:

- reactor runtime and lighting control
- shaker / serial / power control drivers
- compatibility entrypoints for historical station-server workflows

Representative entrypoints:

- `main.py`
- `reactor_station_server.py`

Representative retained configuration:

- `config.yaml`

### `solid-handling-station/`

Key responsibility in the original platform:

- solid reagent handling and related station-level operations

Repository status:

- documentation only
- source code intentionally omitted because of conflict-of-interest constraints

## Recommended Reading Order

If you are new to the repository, start here:

1. Read this file for the high-level module map.
2. Read [`SYSTEM_ARCHITECTURE.md`](./SYSTEM_ARCHITECTURE.md) for the station interaction model.
3. Read [`SETUP.md`](./SETUP.md) for environment and startup expectations.
4. Read [`REPRODUCE.md`](./REPRODUCE.md) for a paper-style sample run path.
5. Then inspect each module-level `README.md` for station-specific details.

## Important Notes

- This repository is not a turnkey deployment package for a new lab. It is a cleaned control-code snapshot intended to document the architecture and workflow used in the project.
- Some paths, hosts, ports, serial devices, and spreadsheets are placeholders or lab-specific examples.
- Many `.xlsx`, `.yaml`, and log-like files in the station directories are operational artifacts or sample state, not source code modules.
- Runtime logs, editor metadata, nested repository metadata, Python cache directories, and internal cleanup/planning files have been removed from this release-oriented repository snapshot.
- Before using any module against real hardware, review the corresponding station code and configuration carefully.

## Module-Level Dependencies

For convenience, a root-level `requirements.txt` is provided for a consolidated software-only environment. Dependencies are also declared inside the station directories:

- `requirements.txt`
- `automatic-control-system/requirements.txt`
- `liquid-handling-workstation/requirements.txt`
- `mobile_robot/requirements.txt`
- `photocatalytic_reactor/requirements.txt`

See [`SETUP.md`](./SETUP.md) for a consolidated environment/setup recommendation.

## Release Notes

This release-oriented snapshot intentionally:

- keeps a minimal published module set plus a documentation-only placeholder for the solid handling station
- retains some compatibility references to non-published stations where they help explain the original workflow
- retains representative sample task/state/configuration files needed to understand the workflow
- omits the solid handling station implementation because of conflict-of-interest constraints
- replaces deployment-sensitive addresses with documentation-safe example values where possible
