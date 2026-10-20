from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

import pandas as pd

from app.workflow import run_weighing


class WorkflowTests(unittest.TestCase):
    def station(self):
        station = Mock()
        station.head_coordinates_df = pd.DataFrame({"Chemical": ["F1"]})
        station.reaction_coordinates_df = pd.DataFrame({"NO": [1]})
        station.handle_weighing_head.return_value = {"init_pos": 1, "align_pos": 2, "action_pos": 3}
        station.start_weighing.return_value = 2.45
        return station

    def test_rejects_unknown_reagent_before_initialization(self):
        station = self.station()
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            run_weighing(pd.DataFrame({"NO": [1], "X1": [1]}), station, directory)
        station.init_device.assert_not_called()

    def test_records_actual_mass_using_simulated_station(self):
        station = self.station()
        with tempfile.TemporaryDirectory() as directory:
            path = run_weighing(pd.DataFrame({"NO": [1], "F1": [2.5]}), station, directory)
            self.assertEqual(Path(path).name, "actual_weight.xlsx")
            self.assertAlmostEqual(pd.read_excel(path).loc[0, "F1"], 2.45)
        station.start_weighing.assert_called_once_with(2, 3, 2.5)
