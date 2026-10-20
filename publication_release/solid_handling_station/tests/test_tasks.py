import unittest

import pandas as pd

from app.tasks import build_chemical_tasks


class TaskValidationTests(unittest.TestCase):
    def test_skips_blank_and_zero_targets(self):
        tasks = build_chemical_tasks(pd.DataFrame({"NO": [1, 2, 3], "F1": [0.0, 2.5, None]}))
        self.assertEqual(tasks["F1"], {"TargetWeight": [2.5], "BottleNum": [2]})

    def test_rejects_negative_nonfinite_and_nonnumeric_targets(self):
        for value in [-1, float("inf"), "invalid"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_chemical_tasks(pd.DataFrame({"NO": [1], "F1": [value]}))

    def test_rejects_invalid_bottle_identifiers(self):
        for values in [[1, 1], [0, 2], [1.5, 2], [None, 2]]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                build_chemical_tasks(pd.DataFrame({"NO": values, "F1": [1, 1]}))

    def test_requires_positive_work_and_identifier_column(self):
        for frame in [pd.DataFrame({"F1": [1]}), pd.DataFrame({"NO": [1], "F1": [0]})]:
            with self.assertRaises(ValueError):
                build_chemical_tasks(frame)
