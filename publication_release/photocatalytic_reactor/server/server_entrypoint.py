"""Shared helpers for station server entrypoints."""

from __future__ import annotations

from pathlib import Path

from client.station_info import station_info
from core.config import PROJECT_PATH, config_logger


def run_station_server(
    station_name: str,
    server_cls,
    *,
    needs_task_dir: bool = False,
) -> None:
    """Create the server logger, optional task directory, and start the server."""
    logs_dir = PROJECT_PATH / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file_name = logs_dir / f"{station_name}.log"
    logger = config_logger(log_file_name, logger_name=f"server.{station_name}")

    if needs_task_dir:
        task_dir = PROJECT_PATH / "task"
        task_dir.mkdir(parents=True, exist_ok=True)
        server = server_cls(*station_info[station_name], logger, str(task_dir))
    else:
        server = server_cls(*station_info[station_name], logger)
    server.start()
