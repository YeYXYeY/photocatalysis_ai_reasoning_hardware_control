import unittest

from drivers.digital_io_rs485 import DigitalIO_RS485


class DummySerialCommunicator:
    def __init__(self):
        self.writes = []

    def write_with_lock(self, data: bytes) -> bool:
        self.writes.append(data)
        return True

    def read_bytes_with_lock(self, size: int) -> bytes:
        return bytes(size)

    def disconnect(self) -> None:
        return None


class DigitalIoRs485Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.serial_comm = DummySerialCommunicator()
        self.device = DigitalIO_RS485(self.serial_comm, address=0x0A)

    def test_write_single_coil_builds_expected_modbus_frame(self) -> None:
        frame = self.device._send_command(
            self.device.FunctionCode.WRITE_SINGLE_COIL,
            start_address=0x0001,
            values=[1],
        )
        self.assertEqual(frame.hex(" "), "0a 05 00 01 ff 00 dc 81")
        self.assertEqual(self.serial_comm.writes[-1], frame)

    def test_write_multiple_coils_packs_bits_in_order(self) -> None:
        frame = self.device._send_command(
            self.device.FunctionCode.WRITE_MULTIPLE_COILS,
            start_address=0x0000,
            values=[1, 0, 1, 1],
        )
        self.assertEqual(frame.hex(" "), "0a 0f 00 00 00 04 01 0d be e0")

    def test_read_input_registers_builds_read_frame(self) -> None:
        frame = self.device._send_command(
            self.device.FunctionCode.READ_INPUT_REGISTERS,
            start_address=0x0000,
            num_registers=4,
        )
        self.assertEqual(frame.hex(" "), "0a 04 00 00 00 04 f0 b2")


if __name__ == "__main__":
    unittest.main()
