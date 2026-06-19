"""Client used to dispatch commands and task files to station servers."""

from __future__ import annotations

import socket
import sys

import pandas as pd

from client.station_info import station_command_dict, station_info


class MasterControlClient:
    """Manage TCP connections to each station service."""

    def __init__(self):
        self.station_info = station_info
        self.stations = {
            name: {"connected": False, "connection": None} for name in station_info
        }

    def connect_to_station(self, station_name):
        """Connect to the selected station if it is configured."""
        info = self.station_info.get(station_name)
        if info is None:
            print(f"No information for station: {station_name}")
            return False

        ip, port = info
        self.stations[station_name] = {
            "connected": False,
            "connection": None,
        }
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            self.stations[station_name] = {
                "connected": True,
                "connection": sock,
            }
            print(f"Successfully connected to {station_name}.")
            return True
        except socket.error as exc:
            print(f"Error connecting to {station_name} server: {exc}")
            self.stations[station_name]["connected"] = False
            self.stations[station_name]["connection"] = None
            return False

    def send_task_file(self, station_name, task_file_df):
        """Send a task DataFrame to the remote station and return the saved filename."""
        station = self.stations.get(station_name)
        if station and not station["connected"]:
            self.connect_to_station(station_name)

        try:
            station["connection"].sendall("receive_file".encode())
            response = station["connection"].recv(1024).decode()
            if response == "ready":
                df_json = task_file_df.to_json(orient="split")
                data_length = len(df_json.encode())
                station["connection"].sendall(str(data_length).encode() + b"\n")
                response = station["connection"].recv(1024).decode()
                if response == "length_received":
                    station["connection"].sendall(df_json.encode())
                    file_name = station["connection"].recv(1024).decode()
                    print(f"Task file sent to {station_name} server: {file_name}")
                    return file_name
            else:
                print(f"Received unexpected response: {response}")
                return None
        except Exception as exc:
            print(f"An error occurred while sending the task file: {exc}")
            return None

    def send_task_command(self, station_name, task_command):
        """Send a task command string to the remote station."""
        station = self.stations.get(station_name)

        if station and not station["connected"]:
            self.connect_to_station(station_name)
        try:
            station["connection"].sendall("run_task".encode())
            response = station["connection"].recv(1024).decode()
            if response == "ready":
                station["connection"].sendall(task_command.encode())
                result = station["connection"].recv(1024).decode()
                if result == "Started":
                    print(f"Task started on {station_name} server.")
                    result = station["connection"].recv(1024).decode()
                    if result == "Completed":
                        print(f"Task completed on {station_name} server.")
                    elif result == "Failed":
                        print(f"Task failed on {station_name} server.")
                else:
                    print(f"Task failed to start on {station_name} server.")
            else:
                print(f"Received unexpected response: {response}")
                return None
        except Exception as exc:
            print(f"An error occurred while sending the task command: {exc}")
            return None

    def execute_task(self, station_name, task_file_df=None, command=None):
        """Send an optional task file and execute a validated command remotely."""
        task_command = ["python", "main.py"]
        station = self.stations.get(station_name)
        if station and not station["connected"]:
            self.connect_to_station(station_name)
        try:
            if task_file_df is not None:
                file_name = self.send_task_file(station_name, task_file_df)
                task_command.extend(["--taskfile", file_name])
            if command is not None:
                station_command_list = station_command_dict.get(station_name)
                if command not in station_command_list:
                    print(f"Invalid command for {station_name}: {command}")
                    sys.exit(1)
                task_command.extend(["--func", command])
            self.send_task_command(station_name, " ".join(task_command))
        except Exception as exc:
            print(f"An error occurred while executing the task: {exc}")
            return None

    def liquid_station(self, task_file_df, command):
        self.execute_task("liquid_station", task_file_df, command)

    def solid_station(self, task_file_df, command):
        self.execute_task("solid_station", task_file_df, command)

    def reactor_station(self, command):
        self.execute_task("reactor_station", command=command)

    def mobile_robot(self, station_name, command):
        self.send_task_command(station_name, command)

    def peptide_station(self, task_file_df, command):
        self.execute_task("peptide_station", task_file_df, command)

    def confirm_all_task(self):
        """Placeholder for future workflow synchronization."""
        return None


if __name__ == "__main__":
    task_file_df = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "David"],
            "age": [25, 26, 27, 28],
            "gender": ["F", "M", "M", "M"],
        }
    )
    client = MasterControlClient()
    client.connect_to_station("test")
    client.send_task_file("test", task_file_df)
