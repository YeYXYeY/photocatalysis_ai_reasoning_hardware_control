# Central control hub

This module contains task splitting, consumption/inventory bookkeeping, YAML status tracking, the PyQt dashboard, and legacy TCP clients/services. Install dependencies from the release root as described in `../SETUP.md`.

## Entry points

Run these commands from **this directory**:

```powershell
python main.py --help
python -m unittest discover -s tests -v
```

`python main.py` executes the **hardware-attached** sample replenishment workflow; it loads `../examples/operational_tasks/hub_task.xlsx` and can send network/device commands. `python -m ui.main_ui` opens the control dashboard. For the safe offline demonstration, return to the release root and run `python main.py demo`.

`workflow/run_sample_workflow.py` holds the sample workflow. `utils/task_processing.py` provides pure task splitting and consumption calculations, `utils/inventory.py` handles inventory, `station_status/` holds state and sample workbooks, `ui/controllers/` holds UI-independent logic, and `server/` contains historical service helpers.

The hub's legacy transfer names do not fully match the supplied mobile CLI and solid rack operations. See `../docs/HARDWARE.md` before any integrated deployment. Network addresses are documentation examples. Runtime tasks/logs are local; representative original tasks are in `../examples/operational_tasks/`.
