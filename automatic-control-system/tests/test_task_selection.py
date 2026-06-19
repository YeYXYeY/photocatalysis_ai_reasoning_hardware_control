import unittest

from ui.controllers.task_selection import SelectionState, describe_selection


class TaskSelectionTests(unittest.TestCase):
    def test_requires_loaded_file_before_starting(self):
        selection = describe_selection(
            SelectionState(
                is_file_loaded=False,
                pre_selected=False,
                post_selected=False,
                steps={"c1": False},
            )
        )

        self.assertFalse(selection.is_valid)
        self.assertEqual(selection.message, "Please load a task file first")

    def test_accepts_predefined_pre_selection(self):
        selection = describe_selection(
            SelectionState(
                is_file_loaded=True,
                pre_selected=True,
                post_selected=False,
                steps={key: False for key in SelectionState.STEP_KEYS},
            )
        )

        self.assertTrue(selection.is_valid)
        self.assertEqual(selection.message, "Pre-reaction workflow selected")

    def test_requires_exactly_one_step_in_manual_mode(self):
        selection = describe_selection(
            SelectionState(
                is_file_loaded=True,
                pre_selected=False,
                post_selected=False,
                steps={key: False for key in SelectionState.STEP_KEYS},
            )
        )

        self.assertFalse(selection.is_valid)
        self.assertEqual(
            selection.message,
            "Single-step execution requires exactly one option",
        )

    def test_returns_selected_step_name_in_manual_mode(self):
        steps = {key: False for key in SelectionState.STEP_KEYS}
        steps["c8"] = True
        selection = describe_selection(
            SelectionState(
                is_file_loaded=True,
                pre_selected=False,
                post_selected=False,
                steps=steps,
            )
        )

        self.assertTrue(selection.is_valid)
        self.assertEqual(selection.message, "Selected step: pre nmr")


if __name__ == "__main__":
    unittest.main()
