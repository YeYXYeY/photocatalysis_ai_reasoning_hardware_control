import logging
import os
import shlex
import socket
import subprocess
import threading
import time

import pandas as pd


class StationServer:
    def __init__(
        self, ip: str, port: int, logger: logging.Logger, file_path: str = "./task"
    ):
        self.ip = ip
        self.port = port
        self.logger = logger
        self.file_path = file_path
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ip, port))
        self.buffer_size = 8192
        self.server_socket.listen(5)
        self.logger.info("%s listening on %s:%s.", self.__class__.__name__, ip, port)

    def handle_client_connection(self, client_socket):
        try:
            command = client_socket.recv(self.buffer_size).decode("utf-8").strip()
            if command == "receive_file":
                client_socket.sendall("ready".encode())
                data_length = int(client_socket.recv(self.buffer_size).decode())
                client_socket.sendall("length_received".encode())

                received_chunks = []
                bytes_received = 0
                while bytes_received < data_length:
                    chunk = client_socket.recv(
                        min(self.buffer_size, data_length - bytes_received)
                    )
                    if chunk == b"":
                        break
                    received_chunks.append(chunk)
                    bytes_received += len(chunk)

                df_json = b"".join(received_chunks).decode()
                task_file_df = pd.read_json(df_json, orient="split")
                current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                file_name = os.path.join(self.file_path, f"{current_time}.xlsx")
                task_file_df.to_excel(file_name, index=False)
                client_socket.sendall(file_name.encode())
                self.logger.info("Received task file and saved it as %s.", file_name)

            elif command == "run_task":
                client_socket.sendall("ready".encode())
                task_command = client_socket.recv(self.buffer_size).decode()
                self.logger.info("Running task command: %s", task_command)
                client_socket.sendall("Started".encode())
                result = self.process_command(task_command)
                if result == "Completed":
                    self.logger.info("Task completed.")
                    client_socket.sendall(result.encode())
                else:
                    self.logger.error("Task failed: %s", result)
                    client_socket.sendall("Failed".encode())
            else:
                self.logger.warning("Unknown command: %s", command)
                client_socket.sendall("Unknown command.".encode())
        except socket.error as e:
            self.logger.error("Socket error occurred: %s", e)
            client_socket.sendall(f"Socket error occurred: {e}".encode())
        except Exception as e:
            self.logger.error("An unexpected error occurred: %s", e)
            client_socket.sendall(f"An unexpected error occurred: {e}".encode())
        finally:
            client_socket.close()

    def process_command(self, command):
        try:
            command_parts = shlex.split(command)

            if (
                len(command_parts) < 2
                or command_parts[0] != "python"
                or command_parts[1] != "main.py"
            ):
                return (
                    "Invalid command format. Expected 'python main.py' with optional "
                    "arguments."
                )

            for i in range(2, len(command_parts), 2):
                if i + 1 >= len(command_parts) or command_parts[i] not in [
                    "--taskfile",
                    "--func",
                ]:
                    return f"Invalid argument: {command_parts[i]}"
                if command_parts[i] == "--taskfile" and not os.path.isfile(
                    command_parts[i + 1]
                ):
                    return f"Task file does not exist: {command_parts[i + 1]}"
                if (
                    command_parts[i] == "--func"
                    and not command_parts[i + 1].isidentifier()
                ):
                    return f"Invalid function name: {command_parts[i + 1]}"

            process_result = subprocess.run(
                command_parts, capture_output=True, text=True
            )

            if process_result.returncode == 0:
                if (
                    "Error" in process_result.stdout
                    or "Exception" in process_result.stdout
                ):
                    return f"The script reported an error: {process_result.stdout}"
                return "Completed"

            return f"Script execution failed: {process_result.stderr}"
        except Exception as e:
            return f"Command execution failed: {e}"

    def start(self):
        try:
            while True:
                self.logger.info("%s waiting for a client connection...", self.__class__.__name__)
                client_socket, client_address = self.server_socket.accept()
                self.logger.info(
                    "%s client connected from %s.",
                    self.__class__.__name__,
                    client_address,
                )
                client_thread = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client_socket,),
                )
                client_thread.start()
        except KeyboardInterrupt:
            self.logger.info("%s shut down.", self.__class__.__name__)
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    server = StationServer("127.0.0.1", 65432, logger, "./")
    print(
        server.process_command(
            "python main.py --func func_name --taskfile "
            "'D:/Users/autoc/Documents/AutoChem/Code/automatic-control-system/task/task.xlsx'"
        )
    )
