"""Compatibility wrapper for the reactor station server entrypoint."""

from __future__ import annotations

from server.reactor_station_server import ReactorStationServer
from server.server_entrypoint import run_station_server

__all__ = ["ReactorStationServer", "run_station_server"]


if __name__ == "__main__":
    run_station_server("reactor_station", ReactorStationServer)
