### master_control_client.py
import socket
import sys
from client.station_info import station_info, station_command_dict


class MasterControlClient:
    def __init__(self):
        self.station_info = station_info
        self.stations = {name: {"connected": False, "connection": None} for name in station_info}

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
        except socket.error as e:
            print(f"Error connecting to {station_name} server: ", e)

            self.stations[station_name]["connected"] = False
            self.stations[station_name]["connection"] = None
            return False

    def send_task_file(self, station_name, task_file_df):
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
        except Exception as e:
            print(f"An error occurred while sending task file: {e}")
            return None

    def send_task_command(self, station_name, task_command):
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
        except Exception as e:
            print(f"An error occurred while sending task command: {e}")
            return None

    def execute_task(self, station_name, task_file_df=None, command=None):

        task_command = ["python", "main.py"]
        station = self.stations.get(station_name)
        # valid connection
        if station and not station["connected"]:
            self.connect_to_station(station_name)

        try:
            if task_file_df is not None:
                file_name = self.send_task_file(station_name, task_file_df)
                task_command.append("--taskfile")
                task_command.append(file_name)
            if command is not None:
                station_command_list = station_command_dict.get(station_name)
                # valid command
                if command not in station_command_list:
                    print(f"Invalid command for {station_name} station: {task_command}")
                    sys.exit(1)
                task_command.append("--func")
                task_command.append(command)

            self.send_task_command(station_name, " ".join(task_command))
        except Exception as e:
            print(f"An error occurred while executing task: {e}")
            return None

    def liquid_station(self, task_file_df, command):
        self.execute_task("liquid_station", task_file_df, command)

    def solid_station(self, task_file_df, command):
        self.execute_task("solid_station", task_file_df, command)

    def photo_reactor(self, command):
        self.send_task_command("photo_reactor", command)

    def mobile_robot(self, station_name, command):
        self.send_task_command(station_name, command)

    def confirm_all_task(self):
        pass
