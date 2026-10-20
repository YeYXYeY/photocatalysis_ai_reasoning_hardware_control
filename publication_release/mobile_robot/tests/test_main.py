import unittest

import main


class MainCliTests(unittest.TestCase):
    def test_parser_accepts_robot_run_script_command(self) -> None:
        parser = main.build_parser()

        args = parser.parse_args(["robot", "run-script", "pipetting"])

        self.assertEqual(args.resource, "robot")
        self.assertEqual(args.robot_action, "run-script")
        self.assertEqual(args.script_name, "pipetting")

    def test_parser_accepts_workflow_command(self) -> None:
        parser = main.build_parser()

        args = parser.parse_args(["workflow", "photocatalysis"])

        self.assertEqual(args.resource, "workflow")
        self.assertEqual(args.workflow_name, "photocatalysis")

    def test_parser_accepts_agv_move_command(self) -> None:
        parser = main.build_parser()

        args = parser.parse_args(["agv", "move", "weighing"])

        self.assertEqual(args.resource, "agv")
        self.assertEqual(args.agv_action, "move")
        self.assertEqual(args.marker_name, "weighing")


if __name__ == "__main__":
    unittest.main()
