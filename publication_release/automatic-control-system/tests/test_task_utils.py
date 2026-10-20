import os
import tempfile
import unittest

import pandas as pd

from utils.task_utils import (
    calc_liquid_comsumption,
    calc_solid_comsumption,
    split_task,
)


class TaskUtilsTests(unittest.TestCase):
    def _build_task_file(self) -> str:
        liquid_columns = [
            "NO",
            "A1",
            "A2",
            "B1",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
            "C6",
            "C7",
            "C8",
            "D1",
            "E1",
            "E2",
            "E3",
            "E4",
            "G1",
            "G2",
            "G3",
            "G4",
            "H1",
            "H2",
            "H3",
            "H4",
            "J1",
            "J2",
            "J3",
            "J4",
            "J5",
            "J6",
            "J7",
            "J8",
        ]
        solid_columns = ["F1", "F2", "F3", "I1", "I2", "I3"]

        rows = [
            {
                "NO": 1,
                "A1": 10,
                "A2": 0,
                "B1": 2,
                "C1": 0,
                "C2": 0,
                "C3": 0,
                "C4": 0,
                "C5": 0,
                "C6": 0,
                "C7": 0,
                "C8": 0,
                "D1": 100,
                "E1": 1,
                "E2": 0,
                "E3": 0,
                "E4": 0,
                "G1": 0,
                "G2": 0,
                "G3": 0,
                "G4": 0,
                "H1": 0,
                "H2": 0,
                "H3": 0,
                "H4": 0,
                "J1": 0,
                "J2": 0,
                "J3": 0,
                "J4": 0,
                "J5": 0,
                "J6": 0,
                "J7": 0,
                "J8": 0,
                "F1": 0,
                "F2": 5,
                "F3": 0,
                "I1": 0,
                "I2": 0,
                "I3": 1,
            },
            {
                "NO": 2,
                "A1": 5,
                "A2": 1,
                "B1": 0,
                "C1": 0,
                "C2": 0,
                "C3": 0,
                "C4": 0,
                "C5": 0,
                "C6": 0,
                "C7": 0,
                "C8": 0,
                "D1": 50,
                "E1": 2,
                "E2": 0,
                "E3": 0,
                "E4": 0,
                "G1": 0,
                "G2": 0,
                "G3": 0,
                "G4": 0,
                "H1": 0,
                "H2": 0,
                "H3": 0,
                "H4": 0,
                "J1": 0,
                "J2": 0,
                "J3": 0,
                "J4": 0,
                "J5": 0,
                "J6": 0,
                "J7": 0,
                "J8": 0,
                "F1": 0,
                "F2": 0,
                "F3": 3,
                "I1": 0,
                "I2": 7,
                "I3": 0,
            },
        ]

        ordered_columns = liquid_columns + solid_columns
        dataframe = pd.DataFrame(rows, columns=ordered_columns)
        temp_dir = tempfile.mkdtemp()
        task_path = os.path.join(temp_dir, "task.xlsx")
        dataframe.to_excel(task_path, index=False)
        return task_path

    def test_split_task_returns_station_specific_frames(self):
        task_path = self._build_task_file()

        solid_df, liquid_df = split_task(task_path)

        self.assertEqual(list(solid_df.columns), ["NO", "F1", "F2", "F3", "I1", "I2", "I3"])
        self.assertEqual(
            list(liquid_df.columns),
            [
                "NO",
                "A1",
                "A2",
                "B1",
                "C1",
                "C2",
                "C3",
                "C4",
                "C5",
                "C6",
                "C7",
                "C8",
                "D1",
                "E1",
                "E2",
                "E3",
                "E4",
                "G1",
                "G2",
                "G3",
                "G4",
                "H1",
                "H2",
                "H3",
                "H4",
                "J1",
                "J2",
                "J3",
                "J4",
                "J5",
                "J6",
                "J7",
                "J8",
            ],
        )
        self.assertEqual(len(solid_df), 2)
        self.assertEqual(len(liquid_df), 2)

    def test_calc_liquid_consumption_sums_columns_and_adds_nmr_keys(self):
        task_path = self._build_task_file()
        _, liquid_df = split_task(task_path)

        consumption = calc_liquid_comsumption(liquid_df)

        self.assertEqual(consumption["A1"], 15)
        self.assertEqual(consumption["A2"], 1)
        self.assertEqual(consumption["B1"], 2)
        self.assertEqual(consumption["E1"], 3)
        self.assertEqual(consumption["G5"], 0.0)
        self.assertEqual(consumption["G6"], 0.0)
        self.assertNotIn("D1", consumption)

    def test_calc_solid_consumption_sums_non_identifier_columns(self):
        task_path = self._build_task_file()
        solid_df, _ = split_task(task_path)

        consumption = calc_solid_comsumption(solid_df)

        self.assertEqual(consumption["F2"], 5)
        self.assertEqual(consumption["F3"], 3)
        self.assertEqual(consumption["I2"], 7)


if __name__ == "__main__":
    unittest.main()
