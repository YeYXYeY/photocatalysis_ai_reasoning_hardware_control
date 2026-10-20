# Third-party components

Python dependencies are installed separately through pip/uv. Their own licenses apply; the repository LICENSE does not replace those terms. Exact versions used for validation are recorded in `requirements-lock-windows.txt`.

The `liquid-handling-workstation/devices/zmotion/zauxdllPython.py` file contains retained ZMotion API wrapper code with a new lazy runtime loader. Its original distribution notice and redistribution terms were not supplied. The authors must establish the wrapper's provenance and any required notices before public redistribution. This document does not grant rights to vendor components.

The vendor binaries `zauxdll.dll` and `zmotion.dll` are not included in the release because no redistribution terms were supplied. Obtain a compatible SDK/runtime from the controller supplier and record its version and license for the physical installation. See `SETUP.md`.

PyQt5/Qt, scientific Python libraries, communications libraries, and any hardware SDK retain their separate licenses. Existing UI icons are retained from the supplied repository; their origin and publication rights should be confirmed by the authors. No new rights or ownership assertions have been inferred for those assets.
