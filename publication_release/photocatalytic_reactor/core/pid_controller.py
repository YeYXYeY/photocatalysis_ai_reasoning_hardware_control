"""Simple PID controller used by the reactor cooling loop."""

from __future__ import annotations

import time


class PIDController:
    """Minimal PID controller that exposes term values for logging."""

    def __init__(self, Kp, Ki, Kd, setpoint, output_limits=(0, 100)):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.output_limits = output_limits

        self._integral = 0
        self._last_error = 0
        self._last_time = time.time()
        self._last_output = 0

        self.p_term = 0
        self.i_term = 0
        self.d_term = 0

    def update(self, process_variable):
        """Update the controller output from the latest process variable."""
        current_time = time.time()
        delta_time = current_time - self._last_time

        if delta_time <= 0.01:
            return self._last_output

        error = process_variable - self.setpoint

        self.p_term = self.Kp * error
        self._integral += error * delta_time

        i_min, i_max = self.output_limits
        if self.Ki != 0:
            self._integral = max(
                min(self._integral, (i_max / self.Ki)),
                (i_min / self.Ki),
            )
        self.i_term = self.Ki * self._integral

        delta_error = error - self._last_error
        self.d_term = self.Kd * (delta_error / delta_time)

        output = self.p_term + self.i_term + self.d_term
        output = max(min(output, self.output_limits[1]), self.output_limits[0])

        self._last_error = error
        self._last_time = current_time
        self._last_output = output
        return output

    def set_setpoint(self, new_setpoint):
        """Update the setpoint and reset the integral accumulator."""
        self.setpoint = new_setpoint
        self._integral = 0
