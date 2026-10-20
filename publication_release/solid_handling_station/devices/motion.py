import logging
import sys
from utilities.calc_crc import calc_crc
import serial
from crccheck.crc import Crc16Modbus
from time import sleep
from typing import Optional


from pathlib import Path
from app.runtime import load_yaml

reset_pge = calc_crc("14 06 01 00 00 01")
pge_speed_20 = calc_crc("14 06 01 04 00 14")
pge_force_20 = calc_crc("14 06 01 01 00 14")
pge_close = calc_crc("14 06 01 03 00 00")
pge_open = calc_crc("14 06 01 03 03 52")
pge_pos_85 = calc_crc("14 06 01 03 03 52")


class Motion:
    """Control the serial stepper drives and parallel gripper."""

    VALID_AXES = ["x", "y", "y1", "y2", "z1", "z2", "z", "r"]
    SAFE_POS_Z = 1000

    def __init__(self, logger: logging.Logger):
        self.serial_param = load_yaml(Path(__file__).with_name("config.yaml"))["dm2c556"]
        self.logger = logger or logging.getLogger(__name__)
        try:
            self.ser = serial.Serial(**self.serial_param)
        except serial.SerialException as e:
            self.logger.error(f"Failed to open serial port: {e}")
            raise

        self.reset_pge = calc_crc("14 06 01 00 00 01")
        self.reset_status = calc_crc("14 03 02 00 00 01")
        self.pge_speed_20 = calc_crc("14 06 01 04 00 14")
        self.pge_force_20 = calc_crc("14 06 01 01 00 14")
        self.hold_status = calc_crc("14 03 02 01 00 01")
        self.pge_pos = calc_crc("14 03 02 02 00 01")

        self.x = "0C"
        self.y = "0D"
        self.z1 = "0E"
        self.z2 = "0F"
        self.z = "10"
        self.r = "11"
        self.y1 = "12"
        self.y2 = "13"
        self.positive_direction = "00 00"
        self.negetive_direction = "00 01"

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

        self.running_status = "03 10 03 00 01"

        self.cmd_pos_h = "03 60 2A 00 01"

        self.cmd_pos_l = "03 60 2B 00 01"

        self.motor_pos_h = "03 60 2A 00 01"

        self.motor_pos_l = "03 60 2B 00 01"

        self.read_datum_mode = "03 60 0A 00 01"

    def send_msg(self, msg):
        """Send a hexadecimal command and return the serial response bytes."""
        msg_bytes = bytearray.fromhex(msg)
        try:
            if not self.ser.is_open:
                self.ser.open()
            self.ser.write(msg_bytes)
            return self.ser.readline()
        except Exception as e:
            self.logger.info(f"Failed to send message: {e}")

    def init_pge(self):
        self.send_msg(reset_pge)
        while True:
            sleep(0.5)
            res = self.send_msg(self.reset_status).hex()[9]
            if res == "1":
                break
        self.send_msg(pge_speed_20)
        self.send_msg(pge_force_20)
        self.send_msg(pge_pos_85)
        self.logger.info("Gripper initialization completed")

    def close_pge(self):
        self.send_msg(pge_close)
        sleep(0.5)
        while True:
            res = self.send_msg(self.hold_status).hex()[9]
            if res == "2":
                self.logger.info("Gripper closed")
                break
            elif res == "3":
                self.logger.info("Gripped object was dropped")
                sys.exit(1)

    def open_pge(self):

        self.send_msg(pge_open)
        sleep(0.5)
        while True:
            res = self.send_msg(self.pge_pos).hex()[6:10]
            try:
                pos = int(res, 16)
                if pos == 850:
                    self.logger.info("Gripper opened")
                    break
            except ValueError:
                continue

    def send_instr(self, axis: str, func: str, value: str = "") -> Optional[str]:
        """Send a CRC-protected command to a supported axis; return its hexadecimal reply."""

        if axis not in self.VALID_AXES:
            self.logger.error(f"Invalid axis: {axis}. Supported axes: {', '.join(self.VALID_AXES)}")
            raise ValueError(f"Invalid axis: {axis}")

        id = getattr(self, axis, None)
        if value == "":
            instr = bytes.fromhex(id + func)
        else:
            instr = bytes.fromhex(id + func + value)
        crc = Crc16Modbus.calc(instr).to_bytes(2, byteorder="little")
        instr = instr + crc

        try:
            self.ser.write(instr)
            for attempt in range(3):
                res = self.ser.read(8)
                if res:
                    break
                self.ser.write(instr)
            else:
                self.logger.error(
                    f"No response after three retries on serial port {self.serial_param.get('port')}, device address {id}, device ({axis.upper()} axis): no data received"
                )
                sys.exit(1)

        except serial.SerialException as e:
            self.logger.error(f"Device ({axis.upper()} axis): communication error: {e}")
            return None

        return res.hex() if res else None

    def datum_mode(self):
        for axis in self.VALID_AXES:
            res = self.send_instr(axis, self.read_datum_mode)
            self.logger.info(res)

    def set_command_pulses(self):
        pulse_25000 = "61 A8"
        pulse_14400 = "38 40"
        for axis in ["x"]:
            self.send_instr(axis, self.command_pulses, pulse_25000)
        for axis in ["y", "z1", "z2"]:
            self.send_instr(axis, self.command_pulses, pulse_14400)

    def set_peak_current(self):
        peak_3_0 = "00 20"
        peak_1_2 = "00 0C"
        peak_0_4 = "00 04"
        peak_0_6 = "00 06"

        for axis in ["x", "y", "z1", "z2"]:
            self.send_instr(axis, self.peak_current, peak_3_0)
        for axis in ["z"]:
            self.send_instr(axis, self.peak_current, peak_1_2)
        for axis in ["y1", "y2"]:
            self.send_instr(axis, self.peak_current, peak_0_6)
        for axis in ["r"]:
            self.send_instr(axis, self.peak_current, peak_0_4)
        return

    def set_motor_orientation(self):
        positive_list = ["x", "y", "z2", "z", "y1", "y2"]
        negetive_list = ["z1", "r"]
        for axis in positive_list:
            self.send_instr(axis, self.motor_orientation, self.positive_direction)
        for axis in negetive_list:
            self.send_instr(axis, self.motor_orientation, self.negetive_direction)

    def set_motor_speed(self):
        accel_value = "27 10"
        datum_high_speed = "00 10"
        datum_low_speed = "00 02"

        self.send_instr("z", self.zero_high_speed, datum_high_speed)
        self.send_instr("z", self.zero_low_speed, datum_low_speed)

        for axis in self.VALID_AXES:
            if axis == "z":
                z_speed = "00 64"
                self.send_instr(axis, self.speed, z_speed)
            elif axis == "z1" or axis == "z2":
                z_speed = "00 1E "
                self.send_instr(axis, self.speed, z_speed)
            elif axis == "y1" or axis == "y2":
                y1_speed = "02 58"
                self.send_instr(axis, self.speed, y1_speed)
            elif axis == "r":
                r_speed = "00 C8"
                self.send_instr(axis, self.speed, r_speed)
            else:
                speed = "00 1E"
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
        """Configure pulses, current, direction, positioning mode, and speed."""

        self.set_command_pulses()

        self.set_peak_current()

        self.set_motor_orientation()

        self.set_absolute_position()

        self.set_motor_speed()

        self.logger.info("Motor driver initial setup completed")

    def get_running_status(self, axis: str):
        """Return eight status bits, least significant first.

        Bits 0 through 6: fault, enabled, running, reserved, command complete,
        path complete, homing complete."""
        status = self.send_instr(axis, self.running_status)[6:10]
        status_dec = int(status, 16)
        status = bin(status_dec)[2:].zfill(8)[::-1]
        return status

    def get_axis_status(self):
        """Check every axis and stop execution if a drive reports a fault."""
        try:
            for axis in self.VALID_AXES:
                status = self.get_running_status(axis)
                if status[0] == "1":
                    self.logger.error(f"{axis} axis fault")
                    raise Exception(f"{axis} axis fault")

        except Exception as e:
            self.logger.error(e)
            sys.exit(1)

    def set_origin(self):
        for axis in self.VALID_AXES:
            self.send_instr(axis, self.set_zero_point)

    def get_position(self, axis: str):
        """Return the motor position as high and low hexadecimal words."""
        pos_h = self.send_instr(axis, self.motor_pos_h)[6:10]
        motor_pos_h = " ".join(pos_h[i : i + 2] for i in range(0, len(pos_h), 2))
        pos_l = self.send_instr(axis, self.motor_pos_l)[6:10]
        motor_pos_l = " ".join(pos_l[i : i + 2] for i in range(0, len(pos_l), 2))
        return motor_pos_h, motor_pos_l

    @staticmethod
    def _to_hex_8_bytes(num: int) -> list[str]:
        """Split a non-negative position into two 16-bit hexadecimal words."""
        if num < 0:
            raise ValueError("Number must be non-negative")

        hex_str = "{:08x}".format(int(num))

        high_4_bytes = " ".join(hex_str[i : i + 2] for i in range(0, 4, 2))
        low_4_bytes = " ".join(hex_str[i : i + 2] for i in range(4, 8, 2))

        return high_4_bytes, low_4_bytes

    def check_move_status(self, axis: str, pos_h, pos_l):
        """Wait until the drive no longer reports motion.

        This checks the running bit, not measured endpoint accuracy."""
        while True:
            status = self.get_running_status(axis)
            if status[2] == "1":
                continue
            elif status[2] == "0":
                break
        #     sys.exit(1)

    def single_move(self, axis: str, pos: int):
        """Move one axis to the requested absolute position in drive units."""
        if axis == "z":
            pass
        else:
            self.get_axis_status()
        pos_h, pos_l = self._to_hex_8_bytes(pos)
        self.send_instr(axis, self.pos_h, pos_h)
        self.send_instr(axis, self.pos_l, pos_l)
        self.send_instr(axis, self.trigger_to_run)
        self.check_move_status(axis, pos_h, pos_l)

    def single_move_zr(self, axis: str, pos: int):
        if axis not in ["z", "r"]:
            self.logger.error(f"Invalid axis: {axis}. Supported axes: z, r")
            raise ValueError(f"Invalid axis: {axis}")
        pos_h, pos_l = self._to_hex_8_bytes(pos)
        self.send_instr(axis, self.pos_h, pos_h)
        self.send_instr(axis, self.pos_l, pos_l)
        self.send_instr(axis, self.trigger_to_run)

    def move_xyz(self, pos_x: int, pos_y: int, pos_z1: int = -1, pos_z2: int = -1):
        """Move x and y, then the optional z axes. A z position of -1 leaves it unchanged."""
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
        self.init_pge()
        negetive_list = ["x", "y", "z1", "z2", "z"]

        for axis in negetive_list:
            self.send_instr(axis, self.origin_signal)
            self.send_instr(axis, self.zero_high_speed)
            self.send_instr(axis, self.zero_low_speed)
            self.send_instr(axis, self.zero_accel_speed)
            self.send_instr(axis, self.zero_decel_speed)
            self.send_instr(axis, self.set_datum_mode, "00 07")

        for axis in ["y1", "y2"]:
            zero_high_speed = "06 60 0F 00 3C"

            zero_low_speed = "06 60 10 00 06"
            self.send_instr(axis, self.origin_signal)
            self.send_instr(axis, zero_high_speed)
            self.send_instr(axis, zero_low_speed)
            self.send_instr(axis, self.zero_accel_speed)
            self.send_instr(axis, self.zero_decel_speed)
            self.send_instr(axis, self.set_datum_mode, "00 06")
        #             print(res)
        #     print(e)
        #     sys.exit(1)

        first_axis = ["y1", "y2", "z"]
        second_axis = ["z1", "z2"]
        third_axis = ["y"]
        fourth_axis = ["x"]

        for axis in first_axis:
            self.send_instr(axis, self.back_zero)

        status_message_printed = False
        while True:
            sleep(2)
            status_list = []
            for axis in first_axis:
                status = self.get_running_status(axis)
                status_list.append(status[4:7])
            if status_list != ["111", "111", "111"]:
                if not status_message_printed:
                    self.logger.info(
                        f"Axis {first_axis} homing in progress; axis {first_axis} is back to zeroing"
                    )
                    status_message_printed = True
                continue
            else:
                self.logger.info(
                    f"Axis {first_axis} homing completed; axis {first_axis} is back to zeroed"
                )
                break

        for axis in second_axis:
            self.send_instr(axis, self.back_zero)

        status_message_printed = False
        while True:
            sleep(2)
            status_list = []
            for axis in second_axis:
                status = self.get_running_status(axis)
                status_list.append(status[4:7])
            if status_list != ["111", "111"]:
                if not status_message_printed:
                    self.logger.info(
                        f"Axis {second_axis} homing in progress; axis {second_axis} is back to zeroing"
                    )
                    status_message_printed = True
                continue
            else:
                self.logger.info(
                    f"Axis {second_axis} homing completed; axis {second_axis} is back to zeroed"
                )
                break

        for axis in third_axis:
            self.send_instr(axis, self.back_zero)

        status_message_printed = False
        while True:
            sleep(2)
            status_list = []
            for axis in third_axis:
                status = self.get_running_status(axis)
                status_list.append(status[4:7])
            if status_list != ["111"]:
                if not status_message_printed:
                    self.logger.info(
                        f"Axis {third_axis} homing in progress; axis {third_axis} is back to zeroing"
                    )
                    status_message_printed = True
                continue
            else:
                self.logger.info(
                    f"Axis {third_axis} homing completed; axis {third_axis} is back to zeroed"
                )
                break

        for axis in fourth_axis:
            self.send_instr(axis, self.back_zero)

        status_message_printed = False
        while True:
            sleep(2)
            status_list = []
            for axis in fourth_axis:
                status = self.get_running_status(axis)
                status_list.append(status[4:7])
            if status_list != ["111"]:
                if not status_message_printed:
                    self.logger.info(
                        f"Axis {fourth_axis} homing in progress; axis {fourth_axis} is back to zeroing"
                    )
                    status_message_printed = True
                continue
            else:
                self.logger.info(
                    f"Axis {fourth_axis} homing completed; axis {fourth_axis} is back to zeroed"
                )
                break

    def safe_pos(self):
        pos_z1_h, pos_z1_l = self._to_hex_8_bytes(self.SAFE_POS_Z)
        pos_z2_h, pos_z2_l = self._to_hex_8_bytes(self.SAFE_POS_Z)
        self.send_instr("z1", self.pos_h, pos_z1_h)
        self.send_instr("z1", self.pos_l, pos_z1_l)
        self.send_instr("z2", self.pos_h, pos_z2_h)
        self.send_instr("z2", self.pos_l, pos_z2_l)
        self.send_instr("z1", self.trigger_to_run)
        self.send_instr("z2", self.trigger_to_run)
        self.check_move_status("z1", pos_z1_h, pos_z1_l)
        self.check_move_status("z2", pos_z2_h, pos_z2_l)

        self.logger.info("Z axes returned to the configured clearance height")

    def end_alignment(self, init_depth=7800, alignment_depth=8220):
        self.single_move("z", 0)
        self.single_move("z", init_depth)
        self.send_instr("r", self.set_zero_point)
        speed_z = "00 01"
        speed_r = "00 20"
        self.send_instr("z", self.speed, speed_z)
        self.send_instr("r", self.speed, speed_r)
        self.single_move_zr("r", 10000)
        self.single_move("z", (init_depth + alignment_depth) / 2)
        speed_z = "00 FA"
        speed_r = "00 FA"
        self.send_instr("z", self.speed, speed_z)
        self.send_instr("r", self.speed, speed_r)
        self.send_instr("r", self.set_zero_point)
        for i in range(3):
            self.single_move("r", 20000)
            self.single_move("r", 0)
        self.single_move("r", 100)
        self.send_instr("r", self.set_zero_point)
        self.single_move("z", 8040)
