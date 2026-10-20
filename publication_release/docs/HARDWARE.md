# Hardware prerequisites and supplied-code limitations

## Physical components

| Module | Required external resources |
| --- | --- |
| Liquid workstation | Motion controller and compatible ZMotion SDK; RS485 pumps/grippers/relays; calibrated coordinate tables; optional Spinsolve NMR and XML protocols |
| Solid station | DM2C-series serial stepper drives, gripper/ZR actuator, serial balance, validated geometry and chemical-to-head mappings |
| Mobile robot | CR10 controller with named robot programs; Trans200 AGV with the expected maps, markers, missions and network API |
| Reactor | Serial/RS485 digital I/O, power/light control, shaker, temperature sensor and cooling hardware configured in YAML |
| Hub | Station services, reachable validated network addresses, initialized status/inventory workbooks, optional PyQt dashboard |

Manufacturer/model details in the original code are implementation references, not a verified bill of materials. Exact serial numbers, firmware, controller programs, SDK version, wiring, and interlock behavior were not supplied for verification.

## Known interface gaps

- The hub sends legacy commands such as `python main.py --func mobile_1_to_liquid`. The supplied mobile CLI instead accepts `robot`, `agv`, and `workflow` subcommands, and implements only the named `photocatalysis` transport workflow. The complete legacy rack-transfer program/adapter set is absent. No physical adapter was invented in this preparation.
- The hub advertises solid `push_rack_out` and `pull_rack_back`. The active solid implementation supports dispensing (`weighing` / `start_weighing`) but does not supply validated rack-transfer actions. Unsupported CLI functions are rejected.
- Peptide-station names remain in compatibility clients/server launchers. No independently complete peptide station is claimed.
- The hub's server launchers are historical deployment helpers. They do not automatically choose the correct station working directory/interpreter for every remote deployment. Use the station-local service and validate its command routing.

The offline demo exercises only real task splitting and accounting. It cannot validate these missing integrations. Do not interpret a passing test suite as proof of hardware coordination or chemical performance.

## Configuration files

Station endpoints live in station-local `client/station_info.py`; hub/liquid/solid network examples also appear in `utils/config.yaml`. Device parameters live in liquid `devices/config.yaml`, solid `devices/config.yaml` and `utilities/config.yaml`, mobile `devices/config.py`, and reactor `config.yaml`. The two solid YAML files serve different consumers; retain both and validate any shared values together.

Network examples use loopback and reserved documentation addresses. They are intentionally not a deployable laboratory network. COM ports and coordinates are retained examples and require site validation. No run against connected hardware was performed during this preparation.
