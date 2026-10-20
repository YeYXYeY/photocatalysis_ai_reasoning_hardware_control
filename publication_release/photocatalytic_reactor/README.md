# Photocatalytic reactor control

The reactor module coordinates lighting, shaking, temperature monitoring, and cooling. `app/reactor_controller.py` contains orchestration; `app/reactor_logic.py` contains pure control helpers; `app/runtime.py` constructs runtime devices. `core/` contains configuration and PID logic, and `drivers/` contains serial/RS485/power/shaker interfaces.

Install root dependencies and run from **this directory**:

```powershell
python main.py --help
python -m unittest discover -s tests -v
```

The manual CLI supports lighting, starting and stopping the reactor, duration parameters and cooling mode selection. Run `--help` for exact arguments. Commands without `--help` operate hardware after building the runtime. `reactor_station_server.py` is the station-service entrypoint; historical bang-bang and PID/PWM wrappers are retained.

Configure serial endpoints, temperatures, timing and connected devices in `config.yaml` before physical use. Generated logs/plots remain local and are excluded from the upload archive. Offline tests verify logic and command construction with controlled inputs, not temperature regulation on a real reactor. See `../docs/HARDWARE.md` for external requirements.
