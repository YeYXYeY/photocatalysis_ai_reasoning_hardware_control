# Reproduce a Representative Sample Run

This document describes a conservative, paper-oriented way to inspect or replay the retained workflow structure without assuming a full lab deployment.

## Goal

The objective is to help a reader understand how the control hub, liquid workstation, mobile robot, and reactor modules fit together in practice.

This is not a guarantee that the full physical workflow can be reproduced on a new machine without local lab configuration and hardware access.

## Reproduction Levels

Choose one of the following levels depending on your access:

### Level 1: Static inspection

Use this if you only want to understand the pipeline for paper review.

Steps:

1. Read [`README.md`](./README.md).
2. Read [`SYSTEM_ARCHITECTURE.md`](./SYSTEM_ARCHITECTURE.md).
3. Inspect `automatic-control-system/workflow/run_sample_workflow.py`.
4. Inspect sample task/status files under:
   - `automatic-control-system/task/`
   - `automatic-control-system/station_status/`
   - `liquid-handling-workstation/task/`
   - `liquid-handling-workstation/coordinates/`

Outcome:

- you understand the intended workflow decomposition and station responsibilities

### Level 2: Software-only validation

Use this if you want to validate retained Python logic without attaching real hardware.

Suggested steps:

1. Create a virtual environment and install the relevant module dependencies.
2. Run available tests in each module that has test coverage.
3. Review failing tests carefully to determine whether they require hardware or environment-specific setup.

Example commands:

```bash
python -m pytest automatic-control-system/tests
python -m pytest liquid-handling-workstation/tests
python -m pytest mobile_robot/tests
python -m pytest photocatalytic_reactor/tests
```

Outcome:

- you can verify which parts of the retained code remain executable in a software-only environment

### Level 3: Lab-attached demonstration

Use this only if you have the real hardware, correct wiring, and validated local configuration.

Suggested order:

1. Validate all host/port and serial configuration files.
2. Start the individual station servers or module runtimes.
3. Start the control hub.
4. Load a representative task workbook.
5. Observe status transitions, inventory checks, and inter-station command flow.

Outcome:

- you can demonstrate the intended multi-station workflow on a configured platform

## Representative Files for Understanding the Workflow

The following retained files are especially useful as anchors:

- `automatic-control-system/workflow/run_sample_workflow.py`
- `automatic-control-system/task/0923task.xlsx`
- `automatic-control-system/station_status/station_status.yaml`
- `automatic-control-system/station_status/initial_status.yaml`
- `liquid-handling-workstation/main.py`
- `mobile_robot/main.py`
- `photocatalytic_reactor/main.py`

## What a Reader Should Expect

In the retained workflow structure:

1. A task spreadsheet is chosen as the input.
2. The control hub interprets and splits that task.
3. Station-specific execution paths are selected.
4. Status/inventory checks gate further actions.
5. Hardware-facing stations perform local execution using their own drivers and configuration.

## Reproducibility Caveats

- The published snapshot keeps only a reduced subset of task examples and removes runtime/editor/cache directories from the release-oriented repository layout.
- Some retained configuration values are placeholders, some are local examples, and some may be stale relative to the original live system.
- Real reproducibility depends on hardware, calibration, coordinates, network topology, and lab SOPs that are outside the scope of this code snapshot.

## Recommended Companion Materials

If this repository is released with a paper, the following additions would further improve reproducibility:

- a task workbook schema explanation
- an inventory/status file schema explanation
- a hardware BOM and communication map
- an operation order / startup checklist
- a note separating sample data from live operational data
