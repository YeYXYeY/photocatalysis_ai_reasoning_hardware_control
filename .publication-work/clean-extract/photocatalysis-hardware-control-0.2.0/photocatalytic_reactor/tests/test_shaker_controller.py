import logging
import unittest

from drivers.shaker_controller import ShakerController


class DummySerialCommunicator:
    def __init__(self):
        self.logger = logging.getLogger("test.shaker")
        self.writes = []
        self.reads = [bytes.fromhex("02 03 02 00 01 3d 84")]

    def write_with_lock(self, data: bytes) -> bool:
        self.writes.append(data)
        return True

    def read_bytes_with_lock(self, _size: int) -> bytes:
        if self.reads:
            return self.reads.pop(0)
        return b""


class ShakerControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.serial_comm = DummySerialCommunicator()
        self.controller = ShakerController(self.serial_comm, address=0x02)

    def test_to_hex_8_bytes_splits_position_into_high_and_low_words(self) -> None:
        self.assertEqual(
            self.controller._to_hex_8_bytes(305419896),
            ("12 34", "56 78"),
        )

    def test_send_instr_builds_crc_appended_frame(self) -> None:
        response = self.controller.send_instr("02", self.controller.trigger_to_run)
        self.assertEqual(self.serial_comm.writes[-1].hex(" "), "02 06 60 02 00 10 37 f5")
        self.assertEqual(response, "02030200013d84")


if __name__ == "__main__":
    unittest.main()
