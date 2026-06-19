# System Architecture

This document explains how the published modules and documentation-only placeholders in the repository fit together as an automated photocatalysis platform.

## Core Topology

The published repository is organized as one automation control hub, three published hardware-facing modules, and one documentation-only station placeholder:

- `automatic-control-system/`: central scheduler, status tracker, and UI layer
- `liquid-handling-workstation/`: liquid handling and reagent preparation station
- `mobile_robot/`: transport and manipulation layer for the CR10 arm and Trans200 AGV
- `photocatalytic_reactor/`: photocatalytic reaction execution layer
- `solid-handling-station/`: documentation-only placeholder for the unpublished solid handling module

At a conceptual level:

```text
task workbook / user input
          |
          v
automatic-control-system
    |        |        |        |
    v        v        v        v
liquid-handling   mobile_robot   photocatalytic_reactor   solid-handling-station
workstation                                              (documentation only)
```

## Role of the Control Hub

The `automatic-control-system/` module acts as the automation control center.

Its retained code indicates these main responsibilities:

- load and interpret task spreadsheets
- split workflows into station-level subtasks
- maintain station state and inventory state
- trigger replenishment logic when required
- expose UI components for monitoring and control
- host or coordinate station server communication

Relevant retained paths include:

- `workflow/run_sample_workflow.py`
- `utils/task_processing.py`
- `utils/inventory.py`
- `utils/confirm_status.py`
- `station_status/`
- `server/`
- `ui/`

## Role of the Liquid Handling Workstation

The `liquid-handling-workstation/` module is the main liquid-processing station.

Its code and retained sample data indicate a coordinate-table-driven hardware workflow:

- reads task workbooks
- dispatches operations such as cap opening, solution preparation, pre/post NMR handling, and reagent replacement
- uses controller and RS485 wrappers for pumps, grippers, motion, and auxiliary devices
- uses spreadsheet coordinate tables to map logical actions onto physical positions
- can be driven locally through a CLI or remotely through a station server

Representative runtime path:

- `main.py`
- `devices/liquid_station.py`
- `devices/controller.py`
- `devices/rs485.py`
- `liquid_station_server.py`

## Role of the Mobile Robot Module

The `mobile_robot/` module provides transport and mobile execution support.

Its retained code indicates:

- a single CLI entrypoint
- CR10 robot arm command dispatch
- Trans200 AGV command dispatch
- named workflows that combine robot and AGV actions

Representative runtime path:

- `main.py`
- `devices/cr10.py`
- `devices/trans200.py`
- `devices/config.py`
- `workflows/standard.py`

This module appears to serve as the movement/transfer layer between otherwise fixed stations.

## Role of the Photocatalytic Reactor Module

The `photocatalytic_reactor/` module contains the reactor-facing execution logic.

Its retained code indicates:

- manual and legacy-compatible reactor entrypoints
- runtime context creation for reactor jobs
- hardware drivers for shaker, serial, digital I/O, and power control
- compatibility wrappers for historical cooling-control modes
- station-server compatibility entrypoints

Representative runtime path:

- `main.py`
- `app/reactor_controller.py`
- `app/runtime.py`
- `drivers/`
- `server/`

## Role of the Solid Handling Station Placeholder

The repository includes a documentation-only placeholder at `solid-handling-station/`.

This placeholder exists because:

- the original automation platform includes a solid handling station
- the rest of the published code still references that station in task routing and communication logic
- the station implementation itself is intentionally not released because of conflict-of-interest constraints

As a result, readers can still understand where the solid handling module sits in the workflow even though its source code is not part of this repository snapshot.

## Notes on Other Compatibility References

Some retained modules also contain compatibility references to a peptide station in client/server glue code.

These references are kept because they are part of the historical orchestration surface of the original platform, but no standalone peptide-station implementation is published in this repository snapshot.

## Data and Control Flow

A typical task flow is:

1. A task workbook is prepared or selected.
2. The automation control hub loads the task and decomposes it into station-relevant operations.
3. The control hub checks current status/inventory state from YAML or workbook-backed state files.
4. The control hub communicates with the relevant station server or module entrypoint.
5. Published stations execute their local hardware logic using their own drivers/configuration, while the solid handling station remains represented only through workflow/documentation references.
6. Logs, status files, or inventory files are updated for later monitoring and replenishment decisions.

## Configuration Boundaries

The repository intentionally mixes several kinds of files:

- source code
- representative task/state spreadsheets
- runtime logs
- machine-specific configuration

In practice, these should be understood as different layers:

### Stable logic layer

Files such as `main.py`, `server/*.py`, `devices/*.py`, `workflow/*.py`, and `app/*.py` are the main retained logic.

### Semi-stable sample data layer

Files such as:

- `task/*.xlsx`
- `station_status/*.yaml`
- `station_status/*.xlsx`
- `coordinates/*.xlsx`

help explain task schema, state layout, and physical mapping, but often need local replacement in a new deployment.

### Lab-specific runtime layer

Files such as:

- host/port config files
- serial port config
- runtime logs
- cached outputs

are environment-specific and should not be assumed portable across labs or machines.

## Communication Model

The codebase suggests a station-server communication model rather than a single in-process monolith.

Observed patterns include:

- `client/` helpers in several modules
- `server/` entrypoints in multiple modules
- host/port definitions in YAML configuration

This implies the control hub can act as a scheduler/orchestrator while station modules expose server-style interfaces for remote command execution.

## How To Read the System

If your goal is to understand the whole automation pipeline:

1. Start from `automatic-control-system/workflow/run_sample_workflow.py`.
2. Inspect `automatic-control-system/utils/` to see how tasks and inventory are handled.
3. Follow station-specific commands into the liquid workstation, robot, or reactor modules.
4. Inspect sample spreadsheets and YAML files only after you understand the code path they support.

## Architecture Caveats

- The repository is a cleaned research-code package, not a productionized distributed system.
- Some station names and compatibility wrappers reflect historical project structure.
- Some historical compatibility references to non-published stations remain in the codebase for architectural completeness.
- Some modules retain more historical artifacts than others.
- Not every checked-in data file is required for understanding the core architecture.
