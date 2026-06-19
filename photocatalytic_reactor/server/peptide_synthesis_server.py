"""Station server entrypoint for the peptide synthesis station."""

from __future__ import annotations

from server.server_entrypoint import run_station_server
from server.station_server import StationServer


class PeptideSynthesisServer(StationServer):
    """Concrete station server for the peptide synthesis station."""


if __name__ == "__main__":
    run_station_server("peptide_station", PeptideSynthesisServer, needs_task_dir=True)
