import os

from server.bootstrap import build_station_server


def main():
    """Start the mobile robot station server."""
    current_path = os.path.abspath(os.path.dirname(__file__))
    mobile_robot_server = build_station_server(
        "mobile_robot", current_path, needs_task_directory=True
    )
    mobile_robot_server.start()


if __name__ == "__main__":
    main()
