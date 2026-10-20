"""Station server entrypoint for the photocatalytic reactor."""

from __future__ import annotations

from server.server_entrypoint import run_station_server
from server.station_server import StationServer


class ReactorStationServer(StationServer):
    """Concrete station server for the photocatalytic reactor."""


if __name__ == "__main__":
    run_station_server("reactor_station", ReactorStationServer)
