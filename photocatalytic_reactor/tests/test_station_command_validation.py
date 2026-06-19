import unittest

from server.station_server import validate_task_command


class StationCommandValidationTests(unittest.TestCase):
    def test_validate_task_command_accepts_supported_command(self) -> None:
        command_parts = validate_task_command("python main.py --func start_reactor")
        self.assertEqual(command_parts, ["python", "main.py", "--func", "start_reactor"])

    def test_validate_task_command_requires_main_entrypoint(self) -> None:
        with self.assertRaisesRegex(ValueError, "main.py"):
            validate_task_command("python other.py --func start_reactor")

    def test_validate_task_command_rejects_unknown_flag(self) -> None:
        with self.assertRaisesRegex(ValueError, "--badflag"):
            validate_task_command("python main.py --badflag value")

    def test_validate_task_command_rejects_invalid_function_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "function"):
            validate_task_command("python main.py --func start-reactor")


if __name__ == "__main__":
    unittest.main()
