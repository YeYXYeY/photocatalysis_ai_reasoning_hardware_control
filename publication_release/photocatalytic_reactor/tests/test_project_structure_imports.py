from pathlib import Path
import unittest

from core.config import PROJECT_PATH
from core.pid_controller import PIDController
from drivers.digital_io_rs485 import DigitalIO_RS485
from drivers.power_controller import PowerController
from drivers.serial_communicator import SerialCommunicator
from drivers.shaker_controller import ShakerController


class ProjectStructureImportTests(unittest.TestCase):
    def test_reorganized_packages_are_importable(self) -> None:
        self.assertTrue(Path(PROJECT_PATH, "config.yaml").is_file())
        self.assertIsNotNone(PIDController)
        self.assertIsNotNone(SerialCommunicator)
        self.assertIsNotNone(DigitalIO_RS485)
        self.assertIsNotNone(PowerController)
        self.assertIsNotNone(ShakerController)

    def test_root_directory_stays_free_of_legacy_driver_logs(self) -> None:
        self.assertFalse(Path(PROJECT_PATH, "shaker.log").exists())


if __name__ == "__main__":
    unittest.main()
