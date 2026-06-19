import os
import time
from dataclasses import dataclass

from client.station_info import station_info
from server.station_server import StationServer
from utils.config import config_logger


@dataclass(frozen=True)
class ServerRuntime:
    log_dir: str
    log_file: str
    task_dir: str | None


def prepare_server_runtime(
    base_dir: str, needs_task_directory: bool
) -> ServerRuntime:
    """Create the runtime directories and log file path for a station server."""
    timestamp = time.strftime("%Y%m%d%H%M", time.localtime())
    log_dir = os.path.join(base_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{timestamp}.log")

    task_dir = None
    if needs_task_directory:
        task_dir = os.path.join(base_dir, "task")
        os.makedirs(task_dir, exist_ok=True)

    return ServerRuntime(log_dir=log_dir, log_file=log_file, task_dir=task_dir)


def build_station_server(
    station_key: str,
    base_dir: str,
    *,
    needs_task_directory: bool,
) -> StationServer:
    """Create a configured station server for the given station key."""
    runtime = prepare_server_runtime(base_dir, needs_task_directory)
    logger = config_logger(runtime.log_file)
    file_path = runtime.task_dir or base_dir
    return StationServer(*station_info[station_key], logger, file_path)
