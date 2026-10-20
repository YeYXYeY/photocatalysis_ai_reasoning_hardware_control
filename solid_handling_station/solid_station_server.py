from server.station_server import StationServer
from client.station_info import station_info
from utils.config import config_logger
import time
import os


class SolidStationServer(StationServer):
    def __init__(self, ip, port, logger, file_path):
        super().__init__(ip, port, logger, file_path)


if __name__ == "__main__":
    # Set the log file name
    current_time = time.strftime("%Y%m%d%H%M", time.localtime())
    current_path = os.path.abspath(os.path.dirname(__file__))
    log_file_path = os.path.join(current_path, "log")
    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)
    log_file_name = os.path.join(log_file_path, f"{current_time}.log")
    logger = config_logger(log_file_name)

    task_file_path = os.path.join(current_path, "task")
    if not os.path.exists(task_file_path):
        os.makedirs(task_file_path)

    # LiquidStationServer
    reactor_station_server = SolidStationServer(
        *station_info["solid_station"], logger, task_file_path
    )
    reactor_station_server.start()
