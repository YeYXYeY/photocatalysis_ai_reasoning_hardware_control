import os

from server.bootstrap import build_station_server


def main():
    """Start the liquid station server."""
    current_path = os.path.abspath(os.path.dirname(__file__))
    liquid_station_server = build_station_server(
        "liquid_station", current_path, needs_task_directory=True
    )
    liquid_station_server.start()


if __name__ == "__main__":
    main()
