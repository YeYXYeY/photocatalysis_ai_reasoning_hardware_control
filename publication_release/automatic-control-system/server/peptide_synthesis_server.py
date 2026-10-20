import os

from server.bootstrap import build_station_server


def main():
    """Start the peptide station server."""
    current_path = os.path.abspath(os.path.dirname(__file__))
    peptide_station_server = build_station_server(
        "peptide_station", current_path, needs_task_directory=True
    )
    peptide_station_server.start()


if __name__ == "__main__":
    main()
