import logging
import os
import tempfile
import unittest

from server.station_server import StationServer


class StationServerTests(unittest.TestCase):
    def _make_server(self) -> StationServer:
        task_dir = tempfile.mkdtemp()
        logger = logging.getLogger(f"station-server-test-{id(self)}")
        logger.handlers.clear()
        return StationServer("127.0.0.1", 0, logger, task_dir)

    def test_invalid_command_is_rejected(self):
        server = self._make_server()
        self.addCleanup(server.server_socket.close)

        result = server.process_command("python script.py")

        self.assertIn("Invalid command format", result)

    def test_missing_task_file_is_rejected(self):
        server = self._make_server()
        self.addCleanup(server.server_socket.close)

        result = server.process_command(
            "python main.py --taskfile missing.xlsx --func replace_reactants"
        )

        self.assertEqual(result, "Task file does not exist: missing.xlsx")

    def test_invalid_function_name_is_rejected(self):
        server = self._make_server()
        self.addCleanup(server.server_socket.close)
        existing_file = os.path.join(tempfile.mkdtemp(), "task.xlsx")
        with open(existing_file, "w", encoding="utf-8") as file:
            file.write("placeholder")

        result = server.process_command(
            f'python main.py --taskfile "{existing_file}" --func bad-name'
        )

        self.assertEqual(result, "Invalid function name: bad-name")


if __name__ == "__main__":
    unittest.main()
