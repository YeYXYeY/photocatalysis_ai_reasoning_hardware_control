"""Modbus RTU helpers for the RS485 digital I/O modules."""

from __future__ import annotations

import time
from enum import IntEnum
from typing import Sequence

from drivers.serial_communicator import SerialCommunicator


class DigitalIO_RS485:
    """Communicate with the RS485 digital I/O, relay, and temperature modules."""

    class FunctionCode(IntEnum):
        READ_COILS = 0x01
        READ_DISCRETE_INPUTS = 0x02
        READ_HOLDING_REGISTERS = 0x03
        READ_INPUT_REGISTERS = 0x04
        WRITE_SINGLE_COIL = 0x05
        WRITE_SINGLE_REGISTER = 0x06
        WRITE_MULTIPLE_COILS = 0x0F
        WRITE_MULTIPLE_REGISTERS = 0x10

    class OperatingMode(IntEnum):
        """Supported relay operating modes from the device manual."""

        NORMAL = 0
        LINKED = 1
        TOGGLE = 2
        CYCLE = 3
        TIMED_ON = 4

    def __init__(self, serial_comm: SerialCommunicator, address: int = 1):
        """Create a device wrapper bound to one Modbus address."""
        self.serial_comm = serial_comm
        self.address = address
        self.max_channels = 48
        self.crc_table = self._generate_crc_table()

    def _generate_crc_table(self) -> list[int]:
        """Precompute the Modbus CRC16 lookup table."""
        table: list[int] = []
        for value in range(256):
            crc = value
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
            table.append(crc)
        return table

    def _calculate_crc(self, data: bytearray) -> bytes:
        """Calculate the little-endian Modbus CRC16 for a request frame."""
        crc = 0xFFFF
        for byte in data:
            crc = (crc >> 8) ^ self.crc_table[(crc ^ byte) & 0xFF]
        return crc.to_bytes(2, "little")

    def _send_command(
        self,
        function_code: int,
        start_address: int,
        values: Sequence[int] | None = None,
        num_registers: int = 1,
    ) -> bytearray:
        """Build and send one Modbus RTU frame."""
        frame = bytearray()
        frame.append(self.address)
        frame.append(function_code)
        frame.extend(start_address.to_bytes(2, "big"))

        if function_code in (
            self.FunctionCode.READ_COILS,
            self.FunctionCode.READ_DISCRETE_INPUTS,
            self.FunctionCode.READ_INPUT_REGISTERS,
            self.FunctionCode.READ_HOLDING_REGISTERS,
        ):
            frame.extend(num_registers.to_bytes(2, "big"))
        elif function_code == self.FunctionCode.WRITE_SINGLE_COIL:
            coil_value = 0xFF00 if values and values[0] else 0x0000
            frame.extend(coil_value.to_bytes(2, "big"))
        elif function_code == self.FunctionCode.WRITE_SINGLE_REGISTER:
            assert values is not None
            frame.extend(values[0].to_bytes(2, "big"))
        elif function_code == self.FunctionCode.WRITE_MULTIPLE_COILS:
            assert values is not None
            byte_count = (len(values) + 7) // 8
            frame.extend(len(values).to_bytes(2, "big"))
            frame.append(byte_count)

            packed_data = 0
            for index, state in enumerate(values):
                if state:
                    packed_data |= 1 << index
            frame.extend(packed_data.to_bytes(byte_count, "big"))
        elif function_code == self.FunctionCode.WRITE_MULTIPLE_REGISTERS:
            assert values is not None
            frame.extend(len(values).to_bytes(2, "big"))
            frame.append(len(values) * 2)
            for value in values:
                frame.extend(value.to_bytes(2, "big"))

        frame.extend(self._calculate_crc(frame))
        self.serial_comm.write_with_lock(frame)
        return frame

    def _receive_response(self, expected_length: int) -> bytes:
        """Wait briefly for the device response and read the expected payload size."""
        time.sleep(0.2)
        response = self.serial_comm.read_bytes_with_lock(expected_length)
        return response

    def read_coil_status(self, address: int, num_coils: int) -> bytes:
        """Read one or more coil bits."""
        self._send_command(
            self.FunctionCode.READ_COILS,
            start_address=address,
            num_registers=num_coils,
        )
        return self._receive_response(5 + (num_coils + 7) // 8)

    def read_discrete_inputs(self, address: int, num_inputs: int) -> bytes:
        """Read one or more discrete input bits."""
        self._send_command(
            self.FunctionCode.READ_DISCRETE_INPUTS,
            start_address=address,
            num_registers=num_inputs,
        )
        return self._receive_response(5 + (num_inputs + 7) // 8)

    def read_holding_registers(self, address: int, num_registers: int) -> bytes:
        """Read one or more holding registers."""
        self._send_command(
            self.FunctionCode.READ_HOLDING_REGISTERS,
            start_address=address,
            num_registers=num_registers,
        )
        return self._receive_response(5 + num_registers * 2)

    def read_input_registers(self, address: int, num_registers: int) -> bytes:
        """Read one or more input registers."""
        self._send_command(
            self.FunctionCode.READ_INPUT_REGISTERS,
            start_address=address,
            num_registers=num_registers,
        )
        return self._receive_response(5 + num_registers * 2)

    def write_single_coil(self, address: int, value: int) -> bytes:
        """Write one coil state."""
        self._send_command(
            self.FunctionCode.WRITE_SINGLE_COIL,
            start_address=address,
            values=[value],
        )
        return self._receive_response(8)

    def write_multiple_coils(self, address: int, values: Sequence[int]) -> bytes:
        """Write multiple coil states in one request."""
        self._send_command(
            self.FunctionCode.WRITE_MULTIPLE_COILS,
            start_address=address,
            values=values,
        )
        return self._receive_response(8)

    def write_single_register(self, address: int, value: int) -> bytes:
        """Write one holding register."""
        self._send_command(
            self.FunctionCode.WRITE_SINGLE_REGISTER,
            start_address=address,
            values=[value],
        )
        return self._receive_response(8)

    def write_multiple_registers(self, address: int, values: Sequence[int]) -> bytes:
        """Write multiple holding registers."""
        self._send_command(
            self.FunctionCode.WRITE_MULTIPLE_REGISTERS,
            start_address=address,
            values=values,
        )
        return self._receive_response(8)

    def read_temperature_humidity(self) -> tuple[float, float]:
        """Read the combined temperature and humidity sensor values."""
        response = self.read_holding_registers(0, 2)
        temperature = ((response[3] << 8) | response[4]) / 10.0
        humidity = ((response[5] << 8) | response[6]) / 10.0
        return temperature, humidity

    def read_temperature(self, addr: int) -> float:
        """Read one temperature probe value."""
        response = self.read_input_registers(addr, 1)
        return ((response[3] << 8) | response[4]) / 10.0

    def read_temperature_sensors(self) -> list[float]:
        """Read the four-channel temperature block used by the reactor."""
        response = self.read_input_registers(0, 4)
        return [
            ((response[3] << 8) | response[4]) / 10.0,
            ((response[5] << 8) | response[6]) / 10.0,
            ((response[7] << 8) | response[8]) / 10.0,
            ((response[9] << 8) | response[10]) / 10.0,
        ]

    def set_relay_state(self, address: int, state: int) -> None:
        """Write one relay state and warn if the device returns no response."""
        response = self.write_single_coil(address, state)
        if not response:
            print(f"Failed to set relay state at address {address} to {state}.")

    def set_multiple_relay_states(self, address: int, states: Sequence[int]) -> None:
        """Write multiple relay states and warn if the device returns no response."""
        response = self.write_multiple_coils(address, states)
        if not response:
            print(f"Failed to set relay states at address {address} to {states}.")

    def close(self) -> None:
        """Close the shared serial connection."""
        self.serial_comm.disconnect()
