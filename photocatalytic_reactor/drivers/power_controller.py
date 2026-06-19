"""RS485 power-supply controller for the reactor lighting system."""

from __future__ import annotations

import sys
import time
from time import sleep

from core.config import load_config_and_logger
from drivers.serial_communicator import SerialCommunicator


class PowerController:
    """Control the LED power supply over the shared serial bus."""

    def __init__(self, serial_comm: SerialCommunicator, address: int = 1):
        self.serial_comm = serial_comm
        self.address = address
        self.logger = serial_comm.logger

    def connect(self):
        """Send the power-supply connect command."""
        return self._send_command("09100000000")

    def disconnect(self):
        """Send the power-supply disconnect command and close the serial port."""
        response = self._send_command("09200000000")
        self.serial_comm.disconnect()
        return response

    def set_voltage(self, voltage):
        """Set the output voltage in volts."""
        voltage_int = int(voltage * 100)
        command = f"01{voltage_int:05d}0000"
        self._send_command(command)

    def set_current(self, current):
        """Set the output current in amps."""
        current_int = int(current * 1000)
        command = f"03{current_int:05d}0000"
        self._send_command(command)

    def read_voltage(self):
        """Read the current output voltage."""
        return self._send_command("02000000000")

    def read_current(self):
        """Read the current output current."""
        return self._send_command("04000000000")

    def enable_output(self):
        """Enable the power-supply output."""
        return self._send_command("07000000000")

    def disable_output(self):
        """Disable the power-supply output."""
        return self._send_command("08000000000")

    def _send_command(self, command):
        """Send an 11-character device command and return the raw response."""
        if len(command) != 11:
            raise ValueError("Power-supply commands must be exactly 11 characters long.")

        full_command = f"<{command}>".encode("ascii")
        self.serial_comm.write_with_lock(full_command)
        time.sleep(0.015)
        response = self.serial_comm.read_until_with_lock(b">")
        time.sleep(0.004)
        return response

    def __enter__(self):
        """Support context-managed use."""
        self.connect()
        return self

    def __exit__(self, *_exc_info):
        """Ensure the device is disconnected when leaving a context manager."""
        self.disconnect()

    def power_setting(
        self, flag: int = 0, voltage: float = 15.2, current: float = 18.9
    ):
        """Apply the high-level power preset used by the reactor workflows."""
        if flag == 1:
            self.connect()
            self.set_voltage(voltage)
            self.read_voltage()
            sleep(1)
            self.set_current(current)
            sleep(1)
            self.enable_output()
        elif flag == 0:
            self.connect()
            sleep(1)
            self.disable_output()
        else:
            print(f"Invalid flag value: {flag}")
            sys.exit(-1)
        sleep(1)


if __name__ == "__main__":
    config, logger = load_config_and_logger("logs/shaker.log")
    serial_comm = SerialCommunicator(config["shaker"], logger)
    power = PowerController(serial_comm, 1)
    power.power_setting(0)
