"""Pure helper functions for reactor control flows.

These helpers keep the most error-prone numeric and state-transition rules
separate from hardware access so they can be tested without serial devices.
"""

from __future__ import annotations


def normalize_cooling_mode(mode: int) -> int:
    """Validate the supported cooling mode values.

    Modes:
    - 0: cooling disabled
    - 1: cooling always on
    - 2: PID + PWM cooling
    """
    if mode not in (0, 1, 2):
        raise ValueError("Cooling mode must be 0, 1, or 2.")
    return mode


def clamp_shaker_speed(speed: int, maximum: int = 120) -> int:
    """Clamp shaker speed to the supported device range."""
    return max(0, min(maximum, int(speed)))


def encode_shaker_speed(speed: int) -> str:
    """Encode the shaker speed as the two-byte hex string expected by the motor."""
    bounded_speed = clamp_shaker_speed(speed)
    speed_hex = hex(bounded_speed)[2:].zfill(4)
    return f"{speed_hex[:2]} {speed_hex[2:]}"


def clamp_cooling_output(pid_output: float, base_cooling_power: float) -> float:
    """Combine PID output with the baseline cooling offset and clamp to 0-100%."""
    return max(0.0, min(100.0, float(pid_output) + float(base_cooling_power)))


def should_enter_reaction_phase(
    current_temp: float, setpoint: float, tolerance: float = 0.5
) -> bool:
    """Return True when the measured temperature is inside the stable handoff band."""
    return abs(float(current_temp) - float(setpoint)) < float(tolerance)
