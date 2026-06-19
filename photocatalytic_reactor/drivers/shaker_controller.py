"""Serial protocol wrapper for the shaker motor controller."""

from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta
from time import sleep
from typing import Optional

from core.config import load_config_and_logger
from drivers.serial_communicator import SerialCommunicator


def _crc16_modbus(data: bytes) -> bytes:
    """Compute the standard Modbus CRC16 in little-endian order."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder="little")


class ShakerController:
    """Control the shaker motor driver over the shared serial bus."""

    def __init__(self, serial_comm: SerialCommunicator, address: int = 1):
        self.serial_comm = serial_comm
        self.address = address
        self.logger = serial_comm.logger
        self.motion = hex(self.address)[2:].zfill(2)

        self.positive_direction = "00 00"
        self.negative_direction = "00 01"

        self.sample_rack_offset = 720
        self.sample_rack_offset_1 = 725000
        self.sample_rack_offset_2 = 405000
        self.sample_rack_offset_3 = 85000
        self.dispensing_head_offset = 735

        self.mode = "06 62 00 00 01"
        self.speed_mode = "06 62 00 00 02"
        self.pos_h = "06 62 01"
        self.pos_l = "06 62 02"
        self.speed = "06 62 03"
        self.accel = "06 62 04"
        self.decel = "06 62 05"
        self.trigger_to_run = "06 60 02 00 10"
        self.trigger_to_stop = "06 60 02 00 40"
        self.emergency_stop = "06 60 02 00 40"
        self.back_zero = "06 60 02 00 20"
        self.set_zero_point = "06 60 02 00 21"
        self.peak_current = "06 01 91"
        self.origin_signal = "06 01 47 00 27"
        self.set_datum_mode = "06 60 0A"
        self.zero_high_speed = "06 60 0F"
        self.zero_low_speed = "06 60 10"
        self.zero_accel_time = "06 60 11"
        self.zero_decel_time = "06 60 12"
        self.motor_orientation = "06 00 07"
        self.command_pulses = "06 00 01"

        self.running_status = "03 10 03 00 01"
        self.cmd_pos_h = "03 60 2A 00 01"
        self.cmd_pos_l = "03 60 2B 00 01"
        self.motor_pos_h = "03 60 2A 00 01"
        self.motor_pos_l = "03 60 2B 00 01"
        self.read_datum_mode = "03 60 0A 00 01"

    def send_instr(self, axis: str, func: str, value: str = "") -> Optional[str]:
        """Build one controller instruction, send it, and return the raw hex response."""
        device_id = hex(self.address)[2:].zfill(2)
        payload = bytes.fromhex(device_id + func + value)
        frame = payload + _crc16_modbus(payload)

        try:
            self.serial_comm.write_with_lock(frame)
            for _attempt in range(3):
                response = self.serial_comm.read_bytes_with_lock(8)
                if response:
                    break
                self.serial_comm.write_with_lock(frame)
            else:
                self.logger.error(
                    "No response received from device address %s after 3 attempts.",
                    device_id,
                )
                sys.exit(1)
        except Exception as exc:
            self.logger.error(
                "Communication with device address %s failed: %s",
                device_id,
                exc,
            )
            return None

        return response.hex() if response else None

    def get_running_status(self, axis: str) -> str:
        """Read the motor running-status bitfield."""
        status = self.send_instr(axis, self.running_status)[6:10]
        status_dec = int(status, 16)
        return bin(status_dec)[2:].zfill(8)[::-1]

    def get_position(self, axis: str) -> tuple[str, str]:
        """Read the current motor position as high and low words."""
        pos_h = self.send_instr(axis, self.motor_pos_h)[6:10]
        motor_pos_h = " ".join(pos_h[index : index + 2] for index in range(0, len(pos_h), 2))
        pos_l = self.send_instr(axis, self.motor_pos_l)[6:10]
        motor_pos_l = " ".join(pos_l[index : index + 2] for index in range(0, len(pos_l), 2))
        return motor_pos_h, motor_pos_l

    @staticmethod
    def _to_hex_8_bytes(num: int) -> tuple[str, str]:
        """Convert a position integer to the controller high and low hex words."""
        if num < 0:
            raise ValueError("Position must be non-negative.")

        hex_str = f"{int(num):08x}"
        high_4_bytes = " ".join(hex_str[index : index + 2] for index in range(0, 4, 2))
        low_4_bytes = " ".join(hex_str[index : index + 2] for index in range(4, 8, 2))
        return high_4_bytes, low_4_bytes

    def check_move_status(self, axis: str, pos_h: str, pos_l: str) -> None:
        """Block until the target axis reports that motion has completed."""
        del pos_h, pos_l
        while True:
            status = self.get_running_status(axis)
            if status[2] == "1":
                continue
            if status[2] == "0":
                break

    def single_move(self, axis: str, pos: int) -> None:
        """Run one absolute move and wait for completion."""
        pos_h, pos_l = self._to_hex_8_bytes(pos)
        self.send_instr(axis, self.pos_h, pos_h)
        self.send_instr(axis, self.pos_l, pos_l)
        self.send_instr(axis, self.trigger_to_run)
        self.check_move_status(axis, pos_h, pos_l)

    def single_move_zr(self, axis: str, pos: int) -> None:
        """Queue one absolute move on one of the supported shaker axes."""
        if axis not in ["A_z", "A_r"]:
            self.logger.error("Invalid axis '%s'. Valid values are A_z and A_r.", axis)
            raise ValueError(f"Invalid axis: {axis}")
        pos_h, pos_l = self._to_hex_8_bytes(pos)
        self.send_instr(axis, self.pos_h, pos_h)
        self.send_instr(axis, self.pos_l, pos_l)
        self.send_instr(axis, self.trigger_to_run)

    def pause_with_countdown(self, duration: int) -> None:
        """Sleep while printing a one-second countdown."""
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=duration)

        while datetime.now() < end_time:
            remaining_time = end_time - datetime.now()
            print(
                f"Time remaining: {remaining_time.seconds}s, expected end: {end_time}",
                end="\r",
            )
            time.sleep(1)

        print("\nPause finished.")

    def shaker_setting(self, flag: int = 0, running_speed: str = "00 78") -> None:
        """Start or stop the shaker using the controller's speed mode."""
        if flag == 1:
            self.send_instr(self.motion, self.speed_mode)
            self.send_instr(self.motion, self.speed, running_speed)
            self.send_instr(self.motion, self.accel, "7F FE")
            self.send_instr(self.motion, self.decel, "7F FE")
            self.send_instr(self.motion, self.trigger_to_run)
        elif flag == 0:
            for decel_speed in ("00 32", "00 16", "00 08"):
                self.send_instr(self.motion, self.speed, decel_speed)
                self.send_instr(self.motion, self.trigger_to_run)
                sleep(2)
            self.send_instr(self.motion, self.trigger_to_stop)
        else:
            print(f"Invalid flag value: {flag}")
            sys.exit(-1)
        sleep(1)


if __name__ == "__main__":
    config, logger = load_config_and_logger("logs/shaker.log")
    serial_comm = SerialCommunicator(config["shaker_2"], logger)
    shaker = ShakerController(serial_comm, 2)
    print(shaker.get_running_status("02"))
