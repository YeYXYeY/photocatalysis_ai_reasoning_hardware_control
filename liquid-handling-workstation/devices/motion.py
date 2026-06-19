import logging
import os
import sys
from utils.calc import calculate_crc
from devices.weighing import Weighing
import serial
import yaml
from crccheck.crc import Crc16Modbus
from time import sleep
from typing import Optional


class Motion:
    """Low-level motion driver wrapper for the linear stage."""

    # Supported axes for this driver wrapper.
    VALID_AXES = ["h"]

    def __init__(self, ser: serial.Serial, logger: logging.Logger):
        self.ser = ser
        self.logger = logger

        # Driver address map.
        self.h = "1F"
        self.positive_direction = "00 00"
        self.negetive_direction = "00 01"

        # Write commands.
        self.mode = "06 62 00 00 01"
        self.pos_h = "06 62 01"
        self.pos_l = "06 62 02"
        self.speed = "06 62 03"
        self.accel = "06 62 04"
        self.decel = "06 62 05"
        self.trigger_to_run = "06 60 02 00 10"
        self.emergency_stop = "06 60 02 00 40"
        self.back_zero = "06 60 02 00 20"
        self.set_zero_point = "06 60 02 00 21"
        self.peak_current = "06 01 91"
        self.origin_signal = "06 01 47 00 27"
        self.set_datum_mode = "06 60 0A"
        self.zero_high_speed = "06 60 0F"
        self.zero_low_speed = "06 60 10"
        self.zero_accel_speed = "06 60 11 00 64"
        self.zero_decel_speed = "06 60 12 27 10"
        self.motor_orientation = "06 00 07"
        self.command_pulses = "06 00 01"

        # Read commands.
        self.running_status = "03 10 03 00 01"
        self.cmd_pos_h = "03 60 2A 00 01"
        self.cmd_pos_l = "03 60 2B 00 01"
        self.motor_pos_h = "03 60 2A 00 01"
        self.motor_pos_l = "03 60 2B 00 01"
        self.read_datum_mode = "03 60 0A 00 01"
        self.read_input_status = "03 01 79 00 01"

    def send_msg(self, msg):
        """Send a raw hex command to the serial line and return the reply."""
        msg_bytes = bytearray.fromhex(msg)
        try:
            if not self.ser.is_open:
                self.ser.open()
            self.ser.write(msg_bytes)
            return self.ser.readline()
        except Exception as e:
            self.logger.error("Failed to send a motion message: %s", e)

    def send_instr(self, axis: str, func: str, value: str = "") -> Optional[str]:
        """Send a command to the requested axis.

        Args:
            axis (str): Axis name.
            func (str): Function code.
            value (str, optional): Command payload. Defaults to "".

        Raises:
            ValueError: Raised when the axis is not supported.

        Returns:
            Optional[str]: Serial response payload.
        """

        if axis not in self.VALID_AXES:
            self.logger.error(
                "Invalid axis '%s'. Supported values: %s.",
                axis,
                ", ".join(self.VALID_AXES),
            )
            raise ValueError(f"Invalid axis: {axis}")

        id = getattr(self, axis, None)
        if value == "":
            instr = bytes.fromhex(id + func)
        else:
            instr = bytes.fromhex(id + func + value)
        crc = Crc16Modbus.calc(instr).to_bytes(2, byteorder="little")
        instr = instr + crc

        try:
            if not self.ser.is_open:
                self.ser.open()
            self.ser.write(instr)
            for attempt in range(3):
                res = self.ser.read(8)
                if res:
                    break
                self.ser.write(instr)
            else:
                self.logger.error(
                    "No response received from axis %s after 3 attempts.",
                    axis.upper(),
                )
                sys.exit(1)

        except serial.SerialException as e:
            self.logger.error(
                "Serial communication with axis %s failed: %s", axis.upper(), e
            )
            return None

        return res.hex() if res else None

    def datum_mode(self):
        for axis in self.VALID_AXES:
            res = self.send_instr(axis, self.read_datum_mode)
            # self.logger.info(res)

    def set_command_pulses(self):
        pulse_25000 = "61 A8"
        pulse_14400 = "38 40"
        for axis in ["x"]:
            self.send_instr(axis, self.command_pulses, pulse_25000)
        for axis in ["y", "z1", "z2"]:
            self.send_instr(axis, self.command_pulses, pulse_14400)

    def set_peak_current(self):
        # peak_3_0 = "00 20"
        # peak_1_2 = "00 0C"
        # peak_0_4 = "00 04"
        peak_0_6 = "00 06"

        # for axis in ["x", "y", "z1", "z2"]:
        #     self.send_instr(axis, self.peak_current, peak_3_0)
        # for axis in ["z"]:
        #     self.send_instr(axis, self.peak_current, peak_1_2)
        # for axis in ["y1", "y2"]:
        #     self.send_instr(axis, self.peak_current, peak_0_6)
        for axis in ["h"]:
            self.send_instr(axis, self.peak_current, peak_0_6)
        return

    def set_motor_orientation(self):
        positive_list = ["h"]
        negetive_list = []
        for axis in positive_list:
            self.send_instr(axis, self.motor_orientation, self.positive_direction)
        for axis in negetive_list:
            self.send_instr(axis, self.motor_orientation, self.negetive_direction)

    def set_motor_speed(self):
        accel_value = "27 10"
        # datum_high_speed = "00 10"
        # datum_low_speed = "00 02"

        # self.send_instr("z", self.zero_high_speed, datum_high_speed)
        # self.send_instr("z", self.zero_low_speed, datum_low_speed)

        for axis in self.VALID_AXES:
            if axis == "z":
                z_speed = "00 64"
                self.send_instr(axis, self.speed, z_speed)
            elif axis == "z1" or axis == "z2":
                z_speed = "00 3C "
                self.send_instr(axis, self.speed, z_speed)
            elif axis == "y1" or axis == "y2":
                y1_speed = "02 58"
                self.send_instr(axis, self.speed, y1_speed)
            elif axis == "r":
                r_speed = "00 C8"
                self.send_instr(axis, self.speed, r_speed)
            else:
                speed = "02 58"
                self.send_instr(axis, self.speed, speed)

            if axis == "z" or axis == "r":
                accel_value_z = "01 28"
                self.send_instr(axis, self.accel, accel_value_z)
                self.send_instr(axis, self.decel, accel_value_z)
            else:
                self.send_instr(axis, self.accel, accel_value)
                self.send_instr(axis, self.decel, accel_value)

    def set_absolute_position(self):
        for axis in self.VALID_AXES:
            self.send_instr(axis, self.mode)

    def initial_setup(self):
        """Apply the default driver configuration."""
        self.set_peak_current()
        self.set_motor_orientation()
        self.set_absolute_position()
        self.set_motor_speed()

        self.logger.info("Motor driver initial setup completed.")

    def get_running_status(self, axis: str):
        """Return the current running status bits for the given axis.

        Args:
            axis (str): Axis name.

        Returns:
            str: Reversed 8-bit status string.
        """
        status = self.send_instr(axis, self.running_status)[6:10]
        status_dec = int(status, 16)
        status = bin(status_dec)[2:].zfill(8)[::-1]
        return status

    def get_input_status(self):
        res = self.send_instr("h", self.read_input_status)[6:10]
        input_status_dec = int(res, 16)
        input_status = bin(input_status_dec)[2:].zfill(16)[-4]
        return int(input_status)

    def get_axis_status(self):
        """Validate that all configured axes are in a healthy state."""
        try:
            for axis in self.VALID_AXES:
                status = self.get_running_status(axis)
                if status[0] == "1":
                    self.logger.error("Axis %s is in a fault state.", axis)
                    raise Exception(f"Axis {axis} is in a fault state.")
        except Exception as e:
            self.logger.error(e)
            sys.exit(1)

    def set_origin(self):
        for axis in self.VALID_AXES:
            self.send_instr(axis, self.set_zero_point)

    def get_position(self, axis: str):
        """Return the current motor position registers.

        Args:
            axis (str): Axis name.

        Returns:
            str: High and low position words.
        """
        pos_h = self.send_instr(axis, self.motor_pos_h)[6:10]
        motor_pos_h = " ".join(pos_h[i : i + 2] for i in range(0, len(pos_h), 2))
        pos_l = self.send_instr(axis, self.motor_pos_l)[6:10]
        motor_pos_l = " ".join(pos_l[i : i + 2] for i in range(0, len(pos_l), 2))
        return motor_pos_h, motor_pos_l

    @staticmethod
    def _to_hex_8_bytes(num: int) -> list[str]:
        """Convert an integer position into high and low hex words.

        Args:
            num (int): Decimal position value.

        Raises:
            ValueError: Raised when the position is negative.

        Returns:
            list[str]: High and low position words.
        """
        if num < 0:
            raise ValueError("Number must be non-negative")

        hex_str = "{:08x}".format(int(num))

        high_4_bytes = " ".join(hex_str[i : i + 2] for i in range(0, 4, 2))
        low_4_bytes = " ".join(hex_str[i : i + 2] for i in range(4, 8, 2))

        return high_4_bytes, low_4_bytes

    def check_move_status(self, axis: str, pos_h, pos_l):
        """Block until motion completes for the requested axis.

        Args:
            axis (str): Axis name.
            pos_h (str): High position word.
            pos_l (str): Low position word.
        """
        while True:
            status = self.get_running_status(axis)
            if status[2] == "1":
                continue
            elif status[2] == "0":
                break

    def single_move(self, axis: str, pos):
        """Move a single axis to the requested absolute position.

        Args:
            axis (str): Axis name.
            pos (int): Decimal target position.
        """
        if axis == "z":
            pass
        else:
            self.get_axis_status()
        pos = int(pos)
        pos_h, pos_l = self._to_hex_8_bytes(pos)
        self.send_instr(axis, self.pos_h, pos_h)
        self.send_instr(axis, self.pos_l, pos_l)
        self.send_instr(axis, self.trigger_to_run)

        self.check_move_status(axis, pos_h, pos_l)

    def single_move_zr(self, axis: str, pos: int):
        if axis not in ["z", "r"]:
            self.logger.error("Invalid axis '%s'. Supported values: z, r.", axis)
            raise ValueError(f"Invalid axis: {axis}")
        pos_h, pos_l = self._to_hex_8_bytes(pos)
        self.send_instr(axis, self.pos_h, pos_h)
        self.send_instr(axis, self.pos_l, pos_l)
        self.send_instr(axis, self.trigger_to_run)

    def move_xyz(self, pos_x: int, pos_y: int, pos_z1: int = -1, pos_z2: int = -1):
        """Move X and Y together, then move the requested Z axes.

        Args:
            pos_x (int): X-axis target position.
            pos_y (int): Y-axis target position.
            pos_z1 (int, optional): Z1 target position. `-1` skips the move.
            pos_z2 (int, optional): Z2 target position. `-1` skips the move.
        """
        self.get_axis_status()
        pos_x_h, pos_x_l = self._to_hex_8_bytes(pos_x)
        pos_y_h, pos_y_l = self._to_hex_8_bytes(pos_y)
        self.send_instr("x", self.pos_h, pos_x_h)
        self.send_instr("x", self.pos_l, pos_x_l)
        self.send_instr("y", self.pos_h, pos_y_h)
        self.send_instr("y", self.pos_l, pos_y_l)
        self.send_instr("x", self.trigger_to_run)
        self.send_instr("y", self.trigger_to_run)
        self.check_move_status("x", pos_x_h, pos_x_l)
        self.check_move_status("y", pos_y_h, pos_y_l)

        if pos_z1 != -1 and pos_z2 != -1:
            pos_z1_h, pos_z1_l = self._to_hex_8_bytes(pos_z1)
            pos_z2_h, pos_z2_l = self._to_hex_8_bytes(pos_z2)
            self.send_instr("z1", self.pos_h, pos_z1_h)
            self.send_instr("z1", self.pos_l, pos_z1_l)
            self.send_instr("z2", self.pos_h, pos_z2_h)
            self.send_instr("z2", self.pos_l, pos_z2_l)
            self.send_instr("z1", self.trigger_to_run)
            self.send_instr("z2", self.trigger_to_run)
            self.check_move_status("z1", pos_z1_h, pos_z1_l)
            self.check_move_status("z2", pos_z2_h, pos_z2_l)
        elif pos_z1 != -1 and pos_z2 == -1:
            pos_z1_h, pos_z1_l = self._to_hex_8_bytes(pos_z1)
            self.send_instr("z1", self.pos_h, pos_z1_h)
            self.send_instr("z1", self.pos_l, pos_z1_l)
            self.send_instr("z1", self.trigger_to_run)
            self.check_move_status("z1", pos_z1_h, pos_z1_l)
        elif pos_z1 == -1 and pos_z2 != -1:
            pos_z2_h, pos_z2_l = self._to_hex_8_bytes(pos_z2)
            self.send_instr("z2", self.pos_h, pos_z2_h)
            self.send_instr("z2", self.pos_l, pos_z2_l)
            self.send_instr("z2", self.trigger_to_run)
            self.check_move_status("z2", pos_z2_h, pos_z2_l)
        else:
            pass
        return

    def datum(self):
        self.get_axis_status()
        negetive_list = ["h"]
        positive_list = []
        for axis in negetive_list:
            zero_high_speed = "06 60 0F 00 3C"
            zero_low_speed = "06 60 10 00 06"
            self.send_instr(axis, self.origin_signal)
            self.send_instr(axis, zero_high_speed)
            self.send_instr(axis, zero_low_speed)
            self.send_instr(axis, self.zero_accel_speed)
            self.send_instr(axis, self.zero_decel_speed)
            self.send_instr(axis, self.set_datum_mode, "00 07")

        for axis in positive_list:
            zero_high_speed = "06 60 0F 00 3C"
            zero_low_speed = "06 60 10 00 06"
            self.send_instr(axis, self.origin_signal)
            self.send_instr(axis, zero_high_speed)
            self.send_instr(axis, zero_low_speed)
            self.send_instr(axis, self.zero_accel_speed)
            self.send_instr(axis, self.zero_decel_speed)
            self.send_instr(axis, self.set_datum_mode, "00 06")

        first_axis = ["h"]

        for axis in first_axis:
            self.send_instr(axis, self.back_zero)
        status_message_printed = False
        while True:
            sleep(2)
            status_list = []
            for axis in first_axis:
                status = self.get_running_status(axis)
                status_list.append(status[4:7])
            if status_list != ["111"]:
                if not status_message_printed:
                    self.logger.info(
                        "Axis %s is still returning to the home position.",
                        first_axis,
                    )
                    status_message_printed = True
                continue
            else:
                self.logger.info("Axis %s returned to home successfully.", first_axis)
                break
