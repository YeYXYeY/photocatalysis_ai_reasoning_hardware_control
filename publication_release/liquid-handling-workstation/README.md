# Liquid handling workstation

The primary path is `main.py` -> `devices/liquid_station.py` -> motion/RS485/peripheral drivers. `devices/liquid_station_runtime.py` assembles configuration, logging, paths and coordinate tables. The supplied code also retains NMR XML protocols and legacy peptide/alternate helpers for inspection; they do not establish a complete integrated peptide station.

Install root dependencies and read `../SETUP.md`, then run commands from **this directory**:

```powershell
python main.py --help
python -m unittest discover -s tests -v
```

After hardware configuration, an operator can run a selected function, for example `python main.py --func prepare_solution --taskfile ../examples/operational_tasks/liquid_task.xlsx`. This performs physical actions. Supported functions include `open_cap`, `prepare_solution`, `pre_nmr_test`, `post_nmr_test`, `close_cap`, `tip_rack_out`, `tip_rack_back`, and `replace_reactants`. The replacement function expects Key/Value columns rather than an ordinary reaction table.

`python liquid_station_server.py` starts the station-local legacy TCP service. Configure station endpoints, device ports, coordinates, materials and interlocks first. Supplier ZMotion runtime DLLs are external dependencies: obtain them separately and set `ZMOTION_LIBRARY`. Importing the Python wrapper does not load a DLL; calling its hardware API does.

Coordinates are retained as installation-specific examples. Original input examples are in `../examples/operational_tasks/`. See `../docs/DATA_DICTIONARY.md` and `../docs/HARDWARE.md` for schemas, external dependencies and known integration gaps.
