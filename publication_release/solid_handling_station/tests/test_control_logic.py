import importlib
import logging
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd

from utilities.calc_crc import calc_crc
from utilities.solid_weigh import SolidWeigh


class ControlLogicTests(unittest.TestCase):
    def test_import_does_not_open_serial_or_read_workbooks(self):
        with patch("serial.Serial") as serial, patch("pandas.read_excel") as read:
            importlib.reload(importlib.import_module("utilities.solid_weigh"))
        serial.assert_not_called()
        read.assert_not_called()

    def test_modbus_crc_uses_little_endian_wire_order(self):
        self.assertEqual(
            calc_crc(bytes.fromhex("01 03 00 00 00 0A")), bytes.fromhex("01 03 00 00 00 0A C5 CD")
        )

    def test_all_calibration_calls_receive_alignment_position(self):
        station = SolidWeigh.__new__(SolidWeigh)
        station.logger = logging.getLogger("test.solid")
        station.motion = Mock()
        station.weighing = Mock()
        station.weighing.stable_weight.return_value = 2.6
        station.balance_coordinates_df = pd.DataFrame(
            {"usage": ["weigh"], "X": [1], "Y": [2], "Z1": [3]}
        )
        station.stop_event = Event()
        station.z1_safe_pos = 1000
        station.weighing_action = Mock()
        station.coarse_weighing = Mock()
        station.monitor_weight = Mock()
        alignments = []
        station.calibrate_actuator = lambda align: alignments.append(align)
        with patch("utilities.solid_weigh.sleep"):
            result = station.start_weighing(8120, 8300, 2.5)
        self.assertEqual(result, 2.6)
        self.assertEqual(alignments, [8120, 8120, 8120])

    def test_nonpositive_target_is_rejected_before_motion(self):
        station = SolidWeigh.__new__(SolidWeigh)
        station.motion = Mock()
        for target in [0, -1, float("inf"), float("nan")]:
            with self.assertRaises(ValueError):
                station.start_weighing(1, 2, target)
        self.assertEqual(station.motion.mock_calls, [])

    def test_calibration_persistence_and_inverse_prediction(self):
        from utilities.dynamic_linear_regression import DynamicLinearRegression

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pd.DataFrame({"Chemical": ["F1"]}).to_excel(root / "head.xlsx", index=False)
            model = DynamicLinearRegression(
                "F1", model_dir=root / "models", coordinates_dir=root, random_state=0
            )
            model.update(1, 2)
            predicted = model.predict(2)
            restored = DynamicLinearRegression(
                "F1", model_dir=root / "models", coordinates_dir=root
            )
            np.testing.assert_array_equal(restored.X, [[1]])
            np.testing.assert_allclose(restored.predict(2), predicted)
