# Automated Photocatalysis Hardware Control

Version **0.2.0** is the publication preparation release of the supplied laboratory control code. It includes the central control hub, liquid workstation, solid dispensing station, mobile robot integration, and photocatalytic reactor.

## Start here

Use **CPython 3.10, Windows x64** for the validated software environment. From this directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock-windows.txt
python main.py demo
python main.py test
python main.py check
```

The demo processes two explicitly synthetic tasks through the actual hub task-splitting and consumption functions. Expected output is supplied in `examples/expected_demo_output.json`. It sends no hardware commands. See [installation](SETUP.md), [reproduction](REPRODUCE.md), and [validation evidence](docs/VALIDATION_REPORT.md).

## Contents

| Directory | Responsibility | Primary entrypoint |
| --- | --- | --- |
| `automatic-control-system/` | Scheduling, task splitting, inventory, and PyQt dashboard | `main.py`, `python -m ui.main_ui` |
| `liquid-handling-workstation/` | Liquid transfer, capping, sampling, NMR integration | `main.py`, `liquid_station_server.py` |
| `solid_handling_station/` | Gravimetric solid dispensing and motion control | `main.py`, `solid_station_server.py` |
| `mobile_robot/` | CR10 arm, Trans200 AGV, named transfer workflow | `main.py` |
| `photocatalytic_reactor/` | Lighting, shaking, temperature and cooling control | `main.py`, `reactor_station_server.py` |

`examples/` contains synthetic demo inputs and six retained operational task examples. `tools/` provides offline demonstration, isolated tests, validation, and packaging. `docs/` documents schemas, hardware prerequisites, provenance, limitations, publication preparation, and changes.

## Reproduction scope

This release validates software logic with local data and mocked devices. It does **not** establish reproduction of chemical yields, manuscript figures, AI reasoning/model results, or an end-to-end hardware experiment. The manuscript, a figure-to-code mapping, robot-side programs, AGV maps, vendor runtime licensing, and a complete experimental dataset were not supplied for this preparation.

The station folders remain separate because their historical `devices`, `utils`, `client`, and `server` package names overlap. Run a station from its own directory. The root test runner isolates each suite in a separate process. This retains laboratory entrypoints while separating the new pure solid-task logic from device initialization.

Before attaching equipment, read [hardware requirements and interface gaps](docs/HARDWARE.md) and substitute validated site configuration. Documentation-range addresses are examples. Some legacy hub/mobile commands and solid rack-transfer actions lack matching station implementations in the supplied code.

## Release and citation

Run `python main.py package` to create a curated ZIP and SHA-256 file under `dist/`. The ZIP includes a per-file `MANIFEST.sha256`. Runtime outputs, local environments, caches, logs, historical prototypes, and vendor DLLs are excluded.

The supplied [LICENSE](LICENSE) is retained: it permits scholarly inspection and peer review and otherwise reserves rights. This release does not change ownership or grant an open-source license. See [third-party dependencies](THIRD_PARTY_NOTICES.md), [citation instructions](CITATION.md), [code availability](CODE_AVAILABILITY.md), and [remaining author metadata](docs/PUBLICATION_CHECKLIST.md).
