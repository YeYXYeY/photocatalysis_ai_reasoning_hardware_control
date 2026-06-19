# Photocatalytic Reactor

## Directory Layout

- `app/`: reactor workflow orchestration and pure business logic.
- `client/`: station client helpers and station metadata.
- `core/`: shared configuration, logging, and control algorithms.
- `drivers/`: hardware communication drivers for serial, RS485, power, and shaker devices.
- `server/`: socket server entrypoints and station server runtime.
- `tests/`: unit tests for logic, drivers, and command validation.
- `logs/`: generated runtime logs and plots during local execution; these outputs are excluded from the publication-oriented snapshot.

## Root Files

- `main.py`: legacy-compatible reactor entrypoint.
- `photocatalytic_controller_bang_bang.py`: compatibility wrapper for the historical cooling-off controller mode.
- `photocatalytic_controller_pid_pwm.py`: compatibility wrapper for the historical PID + PWM mode.
- `reactor_station_server.py`: compatibility wrapper for the reactor server entrypoint.
- `config.yaml`: runtime configuration.
- `requirements.txt`: Python dependencies.
