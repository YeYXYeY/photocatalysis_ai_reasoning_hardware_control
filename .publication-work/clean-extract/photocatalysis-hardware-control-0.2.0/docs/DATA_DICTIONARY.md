# Inputs, outputs, and provenance

## Synthetic offline demo

`examples/demo_task.json`: list of task rows. `NO` is the positive integer bottle identifier. Reagent columns contain positive quantities; omitted columns are filled with zero for the demonstration. A/B example liquid quantities are uL; F/I example solid masses are mg. Zero means no action. `examples/expected_demo_output.json` contains the exact deterministic aggregate summary. These are newly constructed illustrative values, not manuscript results.

## Retained operational workbooks

`examples/operational_tasks/` preserves six original task inputs under descriptive names. They are retained for inspection and local deployment adaptation. Their dates, experimental success, chemical identities, concentration conversions, and manuscript association have not been independently established.

| Release file | Original local source |
| --- | --- |
| `hub_task.xlsx` | `automatic-control-system/task/0923task.xlsx` |
| `hub_task_alternative.xlsx` | `automatic-control-system/task/task.xlsx` |
| `liquid_task.xlsx` | `liquid-handling-workstation/task/250916task.xlsx` |
| `liquid_task_alternative.xlsx` | `liquid-handling-workstation/task/task.xlsx` |
| `solid_task.xlsx` | `solid_handling_station/task/task.xlsx` |
| `solid_task_alternative.xlsx` | `solid_handling_station/task/0621task.xlsx` |

The hub expects the column lists in `automatic-control-system/utils/task_processing.py`, including `NO`, liquid reagent columns A/B/C/D/E/G/H/J, and solid columns F1-F3/I1-I3. The solid runner expects `NO` and one or more reagent columns that match the head coordinate table. It validates unique positive integer bottle IDs, finite non-negative target masses in mg, and at least one positive action. Historical liquid helper column sets differ; use each station's own input schema rather than assuming all workbooks are interchangeable.

## Calibration and state assets

Station-local `coordinates/*.xlsx` files contain drive positions, rack/bottle/head numbers and chemical labels; exact column lists and units are inventoried in `WORKBOOK_INVENTORY.json`. Numeric motion units and frame origins must be confirmed at the device driver and installation level. Coordinate values were not recalibrated during preparation.

`automatic-control-system/station_status/` contains representative inventory, reagent/NMR preparation and YAML station state. These files are mutable initial/example state, not a complete experimental dataset. Numerical cells, formulas, sheets, and non-metadata XML in retained workbooks were preserved; only Office document properties and Chinese font/style names were normalized. Source checksums and cell-level comparisons are recorded in the inventory/validation materials.

## Generated outputs

Solid runs save `actual_weight.xlsx` in a run-specific task/output directory; active unmeasured cells are blank, and completed measurements are checkpointed after each bottle. Logs, reactor plots, and fitted calibration pickles remain local. The optional incremental calibration helper is separate from the active weighing loop and supplies no trained model or AI reasoning pipeline.

Historical task snapshots, measured-weight histories and logs were excluded from the code upload and preserved in the original local material. Their relevance to manuscript evidence requires author review; they have not been declared scientifically unnecessary.
