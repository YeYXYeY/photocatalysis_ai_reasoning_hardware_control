import os

from server.bootstrap import build_station_server


def main():
    """Start the reactor station server."""
    current_path = os.path.abspath(os.path.dirname(__file__))
    reactor_station_server = build_station_server(
        "reactor_station", current_path, needs_task_directory=False
    )
    reactor_station_server.start()


if __name__ == "__main__":
    main()
