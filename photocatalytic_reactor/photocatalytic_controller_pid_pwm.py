"""Compatibility wrapper for the historical PID + PWM controller module."""

from __future__ import annotations

from app.reactor_controller import (
    PhotocatalyticReaction as SharedPhotocatalyticReaction,
    ReactorSettings,
    build_default_reactor,
)
from app.runtime import RuntimeContext, build_runtime_context

__all__ = [
    "PhotocatalyticReaction",
    "ReactorSettings",
    "RuntimeContext",
    "build_default_reactor",
    "build_runtime_context",
]


class PhotocatalyticReaction:
    """Preserve the legacy constructor while delegating to shared logic."""

    def __init__(
        self,
        setpoint: float,
        duration_seconds: int,
        shaker_speed: int,
        pid_params: tuple[float, float, float] = (20.0, 0.1, 0.2),
        pwm_cycle_seconds: int = 60,
        base_cooling_power: float = 30.0,
    ):
        self.runtime = build_runtime_context()
        self.controller = SharedPhotocatalyticReaction(
            self.runtime,
            ReactorSettings(
                setpoint=setpoint,
                duration_seconds=duration_seconds,
                shaker_speed=shaker_speed,
                cooling_mode=2,
                pid_params=pid_params,
                pwm_cycle_seconds=pwm_cycle_seconds,
                base_cooling_power=base_cooling_power,
            ),
        )

    def start(self) -> None:
        self.controller.start()

    def stop(self) -> None:
        self.controller.stop()


def main() -> int:
    """Retain the historical script entrypoint while delegating to shared logic."""
    runtime = build_runtime_context()
    reactor = build_default_reactor(runtime)
    try:
        reactor.start()
        return 0
    except KeyboardInterrupt:
        runtime.logger.warning("Interrupted by user, stopping the reactor.")
        reactor.stop()
        return 130
    except Exception:
        runtime.logger.exception("Unhandled error while running PID + PWM control.")
        reactor.stop()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
