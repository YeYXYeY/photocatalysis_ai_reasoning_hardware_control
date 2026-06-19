import socket
import sys

import pandas as pd

from client.station_info import station_command_dict, station_info
from station_status.station_status import StationStatus


class MasterControlClient:
    def __init__(self):
        self.station_info = station_info
        self.station_status = StationStatus()
        self.stations = {
            name: {"connected": False, "connection": None} for name in station_info
        }

    def init_status(self):
        return self.station_status.load_status()

    def connect_to_station(self, station_name):
        info = self.station_info.get(station_name)
        if info is None:
            print(f"No information for station: {station_name}")
            return

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
        except socket.error as error:
            print(f"Error connecting to {station_name} server: {error}")
            self.stations[station_name]["connected"] = False
            self.stations[station_name]["connection"] = None
            return False

    def disconnect_from_station(self, station_name):
        station = self.stations.get(station_name)
        if station and station["connected"]:
            try:
                station["connection"].close()
                self.stations[station_name] = {
                    "connected": False,
                    "connection": None,
                }
                print(f"Disconnected from {station_name}.")
                return True
            except Exception as error:
                print(
                    f"An error occurred while disconnecting from {station_name} server: {error}"
                )
                return False
        else:
            print(f"Not connected to {station_name}.")

    def send_task_file(self, station_name, task_file_df):
        station = self.stations.get(station_name)
        if station and not station["connected"]:
            self.connect_to_station(station_name)
            station = self.stations.get(station_name)
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
        except Exception as error:
            print(f"An error occurred while sending the task file: {error}")
            return None
        finally:
            self.disconnect_from_station(station_name)

    def send_task_command(self, station_name, task_command):
        station = self.stations.get(station_name)

        if station and not station["connected"]:
            self.connect_to_station(station_name)
            station = self.stations.get(station_name)
        try:
            print("Sending command to station")
            station["connection"].sendall("run_task".encode())
            print("Command sent to station")
            response = station["connection"].recv(1024).decode()
            if response == "ready":
                station["connection"].sendall(task_command.encode())
                result = station["connection"].recv(1024).decode()
                print(result)
                if result == "Started":
                    print(f"Task started on {station_name} server.")
                    result = station["connection"].recv(1024).decode()
                    if result == "Completed":
                        print(f"Task completed on {station_name} server.")
                        return True
                    elif result == "Failed":
                        print(f"Task failed on {station_name} server.")
                        return False
                else:
                    print(f"Task failed to start on {station_name} server.")
            else:
                print(f"Received unexpected response: {response}")
                return None
        except Exception as error:
            print(f"An error occurred while sending the task command: {error}")
            return None
        finally:
            self.disconnect_from_station(station_name)

    def execute_task(self, station_name, task_file_df=None, command=None):
        # Remote station servers expect `main.py` plus optional task and function arguments.
        task_command = ["python", "main.py"]
        station = self.stations.get(station_name)
        if station and not station["connected"]:
            self.connect_to_station(station_name)
        try:
            if task_file_df is not None:
                file_name = self.send_task_file(station_name, task_file_df)
                file_name = file_name.replace("\\", "/")
                task_command.append("--taskfile")
                task_command.append(file_name)
            if command is not None:
                station_command_list = station_command_dict.get(station_name)
                if command not in station_command_list:
                    print(f"Invalid command for {station_name} station: {task_command}")
                    sys.exit(1)
                task_command.append("--func")
                task_command.append(command)
            result = self.send_task_command(station_name, " ".join(task_command))
            return result
        except Exception as error:
            print(f"An error occurred while executing the task: {error}")
            return None

    def liquid_station(self, task_file_df, command):
        if command in station_command_dict.get("liquid_station"):
            result = self.execute_task("liquid_station", task_file_df, command)
        else:
            print(f"Invalid command for liquid_station: {command}")
            result = False
        return result

    def solid_station(self, task_file_df, command):
        if command in station_command_dict.get("solid_station"):
            result = self.execute_task("solid_station", task_file_df, command)
        else:
            result = False
            print(f"Invalid command for solid_station: {command}")
        return result

    def reactor_station(self, command):
        if command in station_command_dict.get("reactor_station"):
            result = self.execute_task(
                "reactor_station", task_file_df=None, command=command
            )
        else:
            result = False
            print(f"Invalid command for reactor_station: {command}")
        return result

    def peptide_station(self, task_file_df, command):
        if command in station_command_dict.get("peptide_station"):
            result = self.execute_task("peptide_station", task_file_df, command)
        else:
            result = False
            print(f"Invalid command for peptide_station: {command}")
        return result

    def mobile_robot(self, command):
        station_name = "mobile_robot"
        if command in station_command_dict.get("mobile_robot"):
            result = self.execute_task(
                station_name=station_name, task_file_df=None, command=command
            )
        else:
            print(f"Invalid command for mobile_robot: {command}")
            return None
        return result

    def confirm_all_task(self):
        pass


if __name__ == "__main__":
    task_file_df = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie", "David"],
            "age": [25, 26, 27, 28],
            "gender": ["F", "M", "M", "M"],
        }
    )
    master_control_client = MasterControlClient()
    master_control_client.connect_to_station("test")
    master_control_client.send_task_file("test", task_file_df)
