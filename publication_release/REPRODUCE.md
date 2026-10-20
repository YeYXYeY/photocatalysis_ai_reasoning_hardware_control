# Reproduction and validation

## 1. Run the software-only demonstration

From the release root:

```powershell
python main.py demo
python main.py demo --output outputs/demo.json
```

The supplied `examples/demo_task.json` is a synthetic two-bottle illustration, not experimental evidence. The demo writes a temporary Excel input, runs the hub's real `split_task`, `calculate_liquid_consumption`, and `calculate_solid_consumption` functions, and compares its complete summary with `examples/expected_demo_output.json`.

Expected totals: A1 = 250 uL, B1 = 75 uL, F1 = 2.5 mg, I1 = 5 mg; two liquid and two solid task rows; zero hardware commands. Missing reagent columns are filled with zero for this illustration, and all-zero station rows are excluded. The example's volume convention is uL; historical operational workbook units require author confirmation.

## 2. Run isolated regression tests

```powershell
python main.py test
```

Each station and the root tests run in a fresh Python process because station-local package names overlap. Tests cover existing task/inventory/status logic, communications and control frame construction, reactor logic, mobile workflow ordering, solid input validation and mock dispensing, calibration persistence, vendor lazy loading, CLI help, and release rules. They do not communicate with physical devices.

For one station, enter that station directory and run `python -m unittest discover -s tests -v`. Do not use a single recursive discovery command across all station folders: it can mix unrelated local packages. The `solid_handling_station/test/` exploratory scripts from the original were not included; the maintained suite is `solid_handling_station/tests/`.

## 3. Audit and package

```powershell
python main.py check
python -m ruff check .
python main.py package
```

The audit checks Python syntax, release filenames, Chinese text in sources and XLSX XML, personal absolute paths, potential literal credentials, and disallowed binary/runtime artifacts. It is an automated pattern check, not proof that every possible secret or dependency defect has been found.

The ZIP excludes local/generated files and contains file hashes. Verify `MANIFEST.sha256` against the extracted files and compare the outer ZIP hash with the accompanying `.zip.sha256` file. Validation details and measured timings are in `docs/VALIDATION_REPORT.md`.

## 4. Hardware reproduction boundary

Only execute hardware commands after site setup and integration validation. Station entrypoints operate real equipment. Use each station's `--help` first; those help paths are tested without hardware.

No manuscript or supporting figure dataset was supplied. This package cannot certify reproduction of published results. A fully integrated physical run additionally requires the items and command adapters listed in `docs/HARDWARE.md`, calibrated coordinates and interlocks, material identities and quantities, robot/AGV assets, firmware versions, and an author-maintained experimental protocol.
