import unittest

from workflows.standard import run_photocatalysis_workflow


class FakeRobot:
    def __init__(self) -> None:
        self.actions: list[tuple[str, str] | str] = []

    def enable_robot(self) -> None:
        self.actions.append("enable_robot")

    def run_script(self, script_name: str) -> None:
        self.actions.append(("run_script", script_name))


class FakeAgv:
    def __init__(self) -> None:
        self.actions: list[tuple[str, str]] = []

    def switch_mode(self, mode: str) -> None:
        self.actions.append(("switch_mode", mode))

    def move_to_marker(self, marker_name: str) -> None:
        self.actions.append(("move_to_marker", marker_name))

    def run_mission(self, mission_name: str) -> None:
        self.actions.append(("run_mission", mission_name))


class WorkflowTests(unittest.TestCase):
    def test_photocatalysis_workflow_runs_expected_sequence(self) -> None:
        robot = FakeRobot()
        agv = FakeAgv()

        run_photocatalysis_workflow(robot, agv, sleep_fn=lambda _: None)

        self.assertEqual(
            robot.actions,
            [
                "enable_robot",
                ("run_script", "pipetting"),
                ("run_script", "photocatalytic"),
            ],
        )
        self.assertEqual(
            agv.actions,
            [
                ("switch_mode", "manual"),
                ("move_to_marker", "photocatalytic"),
                ("switch_mode", "auto"),
                ("run_mission", "rotate_0"),
                ("switch_mode", "manual"),
                ("move_to_marker", "weighing"),
                ("switch_mode", "auto"),
                ("run_mission", "rotate_0"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
