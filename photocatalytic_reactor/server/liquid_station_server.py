"""Station server entrypoint for the liquid station."""

from __future__ import annotations

from server.server_entrypoint import run_station_server
from server.station_server import StationServer


class LiquidStationServer(StationServer):
    """Concrete station server for the liquid station."""


if __name__ == "__main__":
    run_station_server("liquid_station", LiquidStationServer, needs_task_dir=True)
