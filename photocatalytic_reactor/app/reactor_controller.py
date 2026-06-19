"""Photocatalytic reactor orchestration logic."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Sequence

import matplotlib.pyplot as plt

from app.reactor_logic import (
    clamp_cooling_output,
    clamp_shaker_speed,
    encode_shaker_speed,
    normalize_cooling_mode,
    should_enter_reaction_phase,
)
from app.runtime import RuntimeContext
from core.pid_controller import PIDController


@dataclass
class ReactorSettings:
    """User-facing settings for a reactor run."""

    setpoint: float
    duration_seconds: int
    shaker_speed: int
    cooling_mode: int = 2
    pid_params: tuple[float, float, float] = (20.0, 0.1, 0.2)
    pwm_cycle_seconds: int = 60
    base_cooling_power: float = 30.0

    def __post_init__(self) -> None:
        self.cooling_mode = normalize_cooling_mode(self.cooling_mode)
        self.shaker_speed = clamp_shaker_speed(self.shaker_speed)


class PhotocatalyticReaction:
    """Coordinate temperature control, lighting, stirring, and shutdown."""

    def __init__(self, runtime: RuntimeContext, settings: ReactorSettings):
        self.runtime = runtime
        self.settings = settings
        self.logger = runtime.logger
        self.hardware = runtime.hardware

        self.is_running = False
        self.reaction_start_time: float | None = None
        self.overall_start_time: float | None = None

        self.pump_state = 0
        self.last_pwm_update_time = 0.0
        self.pump_on_duration_in_cycle = 0.0

        self.time_points: list[float] = []
        self.temp_points: list[float] = []
        self.cooling_output_points: list[float] = []

        if self.settings.cooling_mode == 2:
            kp, ki, kd = self.settings.pid_params
            self.pid = PIDController(
                Kp=kp,
                Ki=ki,
                Kd=kd,
                setpoint=self.settings.setpoint,
                output_limits=(-100, 100),
            )
        else:
            self.pid = None

    def get_average_temperature(self) -> float:
        """Read all temperature channels and return the rounded mean value."""
        temperatures = self.hardware.temp_sensor.read_temperature_sensors()
        return round(sum(temperatures) / len(temperatures), 1)

    def set_led_state(self, panel_id: int = 4, state: int = 0) -> None:
        """Set one LED panel or all panels at once."""
        if not 0 <= panel_id <= 4:
            raise ValueError("LED panel id must be between 0 and 4.")

        if panel_id == 4:
            self.hardware.led_relay.set_multiple_relay_states(0, [state] * 4)
            return
        self.hardware.led_relay.set_relay_state(panel_id, state)

    def set_power_state(
        self, enabled: int = 0, voltage: float = 15.2, current: float = 18.9
    ) -> None:
        """Switch the LED power supply on or off."""
        self.hardware.power_controller.power_setting(enabled, voltage, current)

    def set_pump_state(self, enabled: int = 0) -> None:
        """Switch the cooling pump relay pair on or off."""
        if enabled not in (0, 1):
            raise ValueError("Pump state must be 0 or 1.")
        self.hardware.pump_relay.set_multiple_relay_states(0, [enabled, enabled])

    def set_shaker_state(self, enabled: int = 0, speed: int | None = None) -> None:
        """Start or stop the shaker with bounded speed."""
        if enabled not in (0, 1):
            raise ValueError("Shaker state must be 0 or 1.")
        if enabled == 1:
            target_speed = encode_shaker_speed(
                self.settings.shaker_speed if speed is None else speed
            )
            self.hardware.shaker_controller.shaker_setting(1, target_speed)
            return
        self.hardware.shaker_controller.shaker_setting(0)

    def _temperature_control_pid_pwm(self, current_temp: float) -> None:
        """Update the PWM cooling duty cycle from the PID controller."""
        current_time = time.time()
        assert self.pid is not None

        if current_time - self.last_pwm_update_time >= self.settings.pwm_cycle_seconds:
            pid_raw_output = self.pid.update(current_temp)
            output = clamp_cooling_output(
                pid_raw_output, self.settings.base_cooling_power
            )
            self.pump_on_duration_in_cycle = (
                output / 100.0
            ) * self.settings.pwm_cycle_seconds
            self.last_pwm_update_time = current_time
            self.logger.info(
                "PID update: temp=%.1fC, raw_output=%.2f%%, base_cooling=%.1f%%, final_output=%.2f%%, pump_on_duration=%.1fs",
                current_temp,
                pid_raw_output,
                self.settings.base_cooling_power,
                output,
                self.pump_on_duration_in_cycle,
            )

        current_output = clamp_cooling_output(
            self.pid._last_output, self.settings.base_cooling_power
        )
        self.cooling_output_points.append(current_output)

        elapsed_in_cycle = current_time - self.last_pwm_update_time
        if elapsed_in_cycle < self.pump_on_duration_in_cycle:
            if self.pump_state == 0:
                self.set_pump_state(1)
                self.pump_state = 1
                self.logger.debug(
                    "PWM control turned the cooling pump on for %.1f seconds.",
                    self.pump_on_duration_in_cycle,
                )
        elif self.pump_state == 1:
            self.set_pump_state(0)
            self.pump_state = 0
            self.logger.debug("PWM control turned the cooling pump off.")

    def _record_non_pid_cooling_output(self) -> None:
        """Record the fixed cooling output for non-PID modes."""
        if self.settings.cooling_mode == 1:
            self.cooling_output_points.append(100.0)
            return
        self.cooling_output_points.append(0.0)

    def _plot_temperature_curve(self) -> None:
        """Persist a temperature and cooling output summary plot for the run."""
        if not self.time_points or not self.temp_points:
            self.logger.warning("No temperature data was recorded, skipping plot generation.")
            return

        figure, axis_temperature = plt.subplots(figsize=(12, 7))
        axis_temperature.set_xlabel("Time (Minutes)")
        axis_temperature.set_ylabel("Temperature (°C)", color="tab:blue")
        axis_temperature.plot(
            self.time_points,
            self.temp_points,
            marker=".",
            linestyle="-",
            label="Measured temperature",
            color="tab:blue",
        )
        axis_temperature.tick_params(axis="y", labelcolor="tab:blue")
        axis_temperature.grid(True)

        axis_cooling = axis_temperature.twinx()
        axis_cooling.set_ylabel("Cooling Output (%)", color="tab:green")
        axis_cooling.plot(
            self.time_points,
            self.cooling_output_points,
            linestyle=":",
            label="Cooling output",
            color="tab:green",
            alpha=0.7,
        )
        axis_cooling.tick_params(axis="y", labelcolor="tab:green")
        axis_cooling.set_ylim(-5, 105)

        if self.settings.cooling_mode == 2:
            axis_temperature.axhline(
                y=self.settings.setpoint,
                color="r",
                linestyle="--",
                label=f"Setpoint ({self.settings.setpoint}°C)",
            )
            plt.title("Temperature and PID Cooling Output During Reaction")
        elif self.settings.cooling_mode == 1:
            plt.title("Temperature During Reaction (Cooling Always On)")
        else:
            plt.title("Temperature During Reaction (Cooling Off)")

        lines, labels = axis_temperature.get_legend_handles_labels()
        lines2, labels2 = axis_cooling.get_legend_handles_labels()
        axis_cooling.legend(lines + lines2, labels + labels2, loc="upper right")

        figure.tight_layout()
        plot_filename = (
            self.runtime.project_dir
            / "logs"
            / f"{self.runtime.log_file_path.stem}_temperature_curve.png"
        )
        plt.savefig(plot_filename)
        self.logger.info("Saved the temperature summary plot to %s", plot_filename)
        plt.close()

    def _start_reaction_outputs(self) -> None:
        """Enable shaker, LEDs, and optional cooling pump at reaction start."""
        self.reaction_start_time = time.time()
        self.set_shaker_state(1, self.settings.shaker_speed)
        self.logger.info("Shaker started at %s rpm.", self.settings.shaker_speed)
        self.set_led_state(panel_id=4, state=1)
        self.set_power_state(enabled=1)
        self.logger.info("LED lighting enabled.")
        if self.settings.cooling_mode == 1:
            self.set_pump_state(1)
            self.pump_state = 1
            self.logger.info("Cooling pump enabled in continuous mode.")
        self.logger.info(
            "Reaction phase started and will run for %s seconds.",
            self.settings.duration_seconds,
        )

    def start(self) -> None:
        """Run the full photocatalytic process until completion or stop()."""
        if self.is_running:
            self.logger.warning("A reaction is already running.")
            return

        self.logger.info("Photocatalytic reaction workflow started.")
        self.is_running = True
        state = "PREPARING"
        self.overall_start_time = time.time()
        if self.settings.cooling_mode == 2:
            self.last_pwm_update_time = self.overall_start_time
            self.logger.info(
                "Stage 1: stabilize temperature at %.1fC with PID + PWM cooling.",
                self.settings.setpoint,
            )
        else:
            self.logger.info("Stage 1: skip temperature stabilization and move directly to reaction.")

        while self.is_running:
            current_temp = self.get_average_temperature()
            elapsed_minutes = (time.time() - self.overall_start_time) / 60.0
            self.time_points.append(elapsed_minutes)
            self.temp_points.append(current_temp)

            if self.settings.cooling_mode == 2:
                self._temperature_control_pid_pwm(current_temp)
            else:
                self._record_non_pid_cooling_output()

            if state == "PREPARING":
                if self.settings.cooling_mode == 2:
                    if should_enter_reaction_phase(
                        current_temp, self.settings.setpoint, tolerance=0.5
                    ):
                        self.logger.info(
                            "Target temperature reached at %.1fC; entering reaction phase.",
                            current_temp,
                        )
                        state = "RUNNING"
                        self._start_reaction_outputs()
                    else:
                        self.logger.info(
                            "Stabilizing temperature: current=%.1fC, target=%.1fC.",
                            current_temp,
                            self.settings.setpoint,
                        )
                else:
                    state = "RUNNING"
                    self._start_reaction_outputs()
            elif state == "RUNNING":
                assert self.reaction_start_time is not None
                reaction_elapsed = time.time() - self.reaction_start_time
                if reaction_elapsed >= self.settings.duration_seconds:
                    self.logger.info("Reaction duration reached; preparing shutdown.")
                    self.is_running = False
                else:
                    self.logger.info(
                        "Reaction running: %ss / %ss elapsed, current temperature %.1fC.",
                        int(reaction_elapsed),
                        self.settings.duration_seconds,
                        current_temp,
                    )

            time.sleep(5)

        self.stop()

    def stop(self) -> None:
        """Stop the process safely and persist the recorded plot."""
        self.logger.info("Stopping the photocatalytic reaction safely.")
        self.set_led_state(panel_id=4, state=0)
        self.set_power_state(enabled=0)
        self.logger.info("LED lighting disabled.")
        self.set_shaker_state(0)
        self.logger.info("Shaker stopped.")
        self.set_pump_state(0)
        self.pump_state = 0
        self.logger.info("Cooling pump disabled.")
        self._plot_temperature_curve()
        self.is_running = False
        self.logger.info("Photocatalytic reaction stopped safely.")

    def lighting(self, timing_hours: float) -> None:
        """Run the lighting system alone for the specified duration."""
        self.logger.info("Starting the standalone lighting routine.")
        self.set_led_state(panel_id=4, state=1)
        self.set_power_state(enabled=1)
        self.logger.info("LED lighting enabled.")
        time.sleep(timing_hours * 3600)
        self.logger.info("Lighting routine complete; disabling LEDs.")
        self.set_led_state(panel_id=4, state=0)
        self.set_power_state(enabled=0)
        self.logger.info("LED lighting disabled.")


def build_default_reactor(
    runtime: RuntimeContext,
    *,
    setpoint: float = 20.0,
    duration_seconds: int = 3600,
    shaker_speed: int = 100,
    cooling_mode: int = 2,
    pid_params: Sequence[float] = (15.0, 0.1, 1.0),
    pwm_cycle_seconds: int = 60,
    base_cooling_power: float = 45.0,
) -> PhotocatalyticReaction:
    """Create a default reactor controller with project-standard settings."""
    settings = ReactorSettings(
        setpoint=setpoint,
        duration_seconds=duration_seconds,
        shaker_speed=shaker_speed,
        cooling_mode=cooling_mode,
        pid_params=(float(pid_params[0]), float(pid_params[1]), float(pid_params[2])),
        pwm_cycle_seconds=pwm_cycle_seconds,
        base_cooling_power=base_cooling_power,
    )
    return PhotocatalyticReaction(runtime, settings)
