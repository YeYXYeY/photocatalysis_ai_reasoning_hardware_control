from pathlib import Path

from client.station_info import station_info
from server.station_server import StationServer
from utils.config import build_timestamped_log_path, config_logger, ensure_directory


class ReactorStationServer(StationServer):
    def __init__(self, ip, port, logger):
        super().__init__(ip, port, logger)


def build_server_runtime_paths(base_dir):
    base_path = Path(base_dir)
    log_dir = ensure_directory(base_path / "log")
    return {
        "base_dir": base_path,
        "log_dir": log_dir,
        "log_file": build_timestamped_log_path(log_dir),
    }


def main():
    runtime_paths = build_server_runtime_paths(Path(__file__).resolve().parent)
    logger = config_logger(
        runtime_paths["log_file"], logger_name="reactor_workstation.server"
    )
    reactor_station_server = ReactorStationServer(
        *station_info["reactor_station"], logger
    )
    reactor_station_server.start()


if __name__ == "__main__":
    main()
