"""Station server entrypoint for the mobile robot."""

from __future__ import annotations

from server.server_entrypoint import run_station_server
from server.station_server import StationServer


class MobileRobotServer(StationServer):
    """Concrete station server for the mobile robot."""


if __name__ == "__main__":
    run_station_server("mobile_robot", MobileRobotServer, needs_task_dir=True)
