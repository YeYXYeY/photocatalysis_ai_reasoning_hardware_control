import os

from server.bootstrap import build_station_server


def main():
    """Start the solid station server."""
    current_path = os.path.abspath(os.path.dirname(__file__))
    solid_station_server = build_station_server(
        "solid_station", current_path, needs_task_directory=True
    )
    solid_station_server.start()


if __name__ == "__main__":
    main()
