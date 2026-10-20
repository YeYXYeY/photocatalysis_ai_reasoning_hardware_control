# Installation

## Validated system

- Windows x64; CPython 3.10.19. The supported project range is Python 3.10.x.
- CPU-only software validation; no GPU, laboratory device, vendor DLL, or email account is required for demo/tests.
- Exact direct dependencies are in `requirements.txt`; the complete validated Windows environment is in `requirements-lock-windows.txt`. `pyproject.toml` records matching direct dependencies and developer tools.
- Other operating systems and Python releases have not been validated. The ZMotion hardware binding explicitly requires Windows.

## Installation from an extracted archive

Open a terminal in the directory containing this file:

```powershell
python --version
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock-windows.txt
python main.py demo
```

If activation is unavailable, use `.venv\Scripts\python.exe` in place of `python`; activation is not required. A Python installation with `venv` and pip is required. An internet connection is needed to install packages unless compatible wheels are cached. No editable package installation is needed: this is a multi-process source repository.

For software use without development tooling, install `requirements.txt` instead. For development, `requirements-dev.txt` includes the runtime dependencies, pytest, and Ruff. Station-level requirements files delegate to the root version pins.

The measured preparation environment used uv to install 44 packages: resolution 3.32 s, download/preparation 8.26 s, installation 2.45 s. These are one-machine observations, exclude Python installation, and are not a guaranteed fresh-download duration. See `docs/VALIDATION_REPORT.md` for measured demo and test timings.

## Hardware setup

Install the correct supplier ZMotion SDK separately. Keep `zauxdll.dll` and its matching dependencies together and set an absolute path:

```powershell
$env:ZMOTION_LIBRARY = 'C:\VendorSDK\zauxdll.dll'
```

Alternatively place the licensed runtime files beside `liquid-handling-workstation/devices/zmotion/zauxdllPython.py`. They are excluded from release archives. The wrapper loads the DLL only when a hardware API is called. Match the SDK and Python bitness; the SDK version and firmware versions must be recorded by the deploying laboratory.

Configure station IPs in the corresponding `client/station_info.py`, device ports in YAML/Python configuration, validated coordinate workbooks, robot programs, and AGV maps before executing station commands. The hardware and integration limitations are enumerated in `docs/HARDWARE.md`.
