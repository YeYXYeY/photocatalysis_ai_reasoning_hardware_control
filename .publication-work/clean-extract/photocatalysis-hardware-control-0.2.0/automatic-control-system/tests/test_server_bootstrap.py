import os
import tempfile
import unittest

from server.bootstrap import prepare_server_runtime


class ServerBootstrapTests(unittest.TestCase):
    def test_prepare_server_runtime_creates_log_and_task_directories(self):
        base_dir = tempfile.mkdtemp()

        runtime = prepare_server_runtime(base_dir, needs_task_directory=True)

        self.assertTrue(os.path.isdir(runtime.log_dir))
        self.assertTrue(os.path.isdir(runtime.task_dir))
        self.assertTrue(runtime.log_file.endswith(".log"))

    def test_prepare_server_runtime_can_skip_task_directory(self):
        base_dir = tempfile.mkdtemp()

        runtime = prepare_server_runtime(base_dir, needs_task_directory=False)

        self.assertTrue(os.path.isdir(runtime.log_dir))
        self.assertIsNone(runtime.task_dir)


if __name__ == "__main__":
    unittest.main()
