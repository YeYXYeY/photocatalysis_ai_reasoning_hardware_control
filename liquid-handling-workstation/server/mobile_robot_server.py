from pathlib import Path

from client.station_info import station_info
from server.station_server import StationServer
from utils.config import build_timestamped_log_path, config_logger, ensure_directory


class MobileRobotServer(StationServer):
    def __init__(self, ip, port, logger, file_path):
        super().__init__(ip, port, logger, file_path)


def build_server_runtime_paths(base_dir):
    base_path = Path(base_dir)
    log_dir = ensure_directory(base_path / "log")
    task_dir = ensure_directory(base_path / "task")
    return {
        "base_dir": base_path,
        "log_dir": log_dir,
        "task_dir": task_dir,
        "log_file": build_timestamped_log_path(log_dir),
    }


def main():
    runtime_paths = build_server_runtime_paths(Path(__file__).resolve().parent)
    logger = config_logger(
        runtime_paths["log_file"], logger_name="mobile_robot.server"
    )
    mobile_robot_server = MobileRobotServer(
        *station_info["mobile_robot"], logger, str(runtime_paths["task_dir"])
    )
    mobile_robot_server.start()


if __name__ == "__main__":
    main()
