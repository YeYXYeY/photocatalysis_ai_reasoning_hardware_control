# Automatic Control System

This repository is the cleaned supplementary code package for a paper on an automated multi-station chemical workflow. It preserves the original control logic and sample data needed to understand the workflow while removing generated files, duplicate UI artifacts, legacy experiments, and machine-specific clutter.

## Repository Layout

- `main.py`: Thin workflow entry script that delegates to the extracted sample workflow runner.
- `client/`: Client-side station communication helpers and command definitions.
- `server/`: Socket-based station server implementation, shared bootstrap helpers, and per-station launchers.
- `station_status/`: YAML status model plus representative sample inventory/status spreadsheets.
- `task/`: Curated sample task spreadsheets retained for demonstration and supplementary review.
- `tests/`: `unittest` regression coverage for the retained core logic.
- `ui/`: PyQt-based dashboard sources, generated UI files, and non-generated controller helpers.
- `utils/`: Shared helpers for task splitting, inventory accounting, status display, and configuration loading.
- `workflow/`: Extracted sample workflow orchestration for the retained replenishment flow.

## Retained Sample Data

The cleaned repository keeps a minimal set of sample input/state files:

- `task/0923task.xlsx`: Default sample task file referenced by `main.py`.
- `task/task.xlsx`: Generic sample task spreadsheet.
- `station_status/station_status.yaml`: Current sample station state.
- `station_status/initial_status.yaml`: Baseline sample station state.
- `station_status/nmr_prepare.xlsx` and `station_status/reactant_info_*.xlsx`: Sample reagent/NMR preparation data.
- `station_status/liquid_chemical_remaining.xlsx` and `station_status/solid_chemical_remaining.xlsx`: Sample inventory spreadsheets.

Historical task snapshots and disposable runtime artifacts were removed to keep the supplementary package focused.

## Requirements

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

The retained code imports the following packages:

- `pandas`
- `openpyxl`
- `PyYAML`
- `PyQt5`

## Usage

Run commands from the repository root so the package-style imports resolve correctly.

### Main workflow

`main.py` delegates to `workflow/run_sample_workflow.py`. The retained sample workflow loads the curated sample task file `task/0923task.xlsx`, splits the task into liquid and solid station worklists, checks liquid inventory requirements, and triggers reagent replenishment actions when needed.

Example:

```bash
python main.py
```

### UI dashboard

The retained PyQt dashboard implementation is in `ui/main_ui.py`.

Example:

```bash
python -m ui.main_ui
```

### Station servers

Each server launcher under `server/` exposes a standalone entry script for the corresponding station and now shares common bootstrap behavior, for example:

```bash
python -m server.liquid_station_server
```

## Configuration Notes

- IP addresses in `client/station_info.py` and `utils/config.yaml` were replaced with documentation-safe placeholder values for publication.
- The configuration structure was preserved so local deployments can substitute lab-specific values if needed.
- The repository is intended as supplementary material, not as a turn-key deployment package for a specific hardware environment.

## Notes for Reviewers

- The codebase was cleaned without intentionally changing retained function signatures or the main workflow structure.
- Some scripts still assume access to external station services or hardware-specific environments; these are kept to document the control flow used in the project.
- Generated caches, duplicate UI files, temporary test scripts, unused helpers, and most historical task dumps were removed to make the repository easier to inspect.
- The refactor keeps compatibility wrappers for several legacy helper names so the retained modules stay easier to compare against the original project structure.
