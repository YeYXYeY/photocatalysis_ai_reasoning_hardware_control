import serial
from time import sleep
import logging


from pathlib import Path
from app.runtime import load_yaml


class Weighing:
    """Read and tare the serial balance; reported weights use milligrams."""

    def __init__(self, logger: logging.Logger = None):
        self.serial_param = load_yaml(Path(__file__).with_name("config.yaml"))["mk210"]
        self.logger = logger or logging.getLogger(__name__)

        try:
            self.ser = serial.Serial(**self.serial_param)
        except serial.SerialException as e:
            self.logger.error(f"Failed to open serial port: {e}")
            raise

    def tare(self):
        """Tare the balance and wait for its settling delay."""
        self.ser.write("\033T\n".encode("utf-8"))
        sleep(5)
        self.logger.info("Balance tare completed")

    def test(self):
        self.ser.write("\033N\n".encode("utf-8"))
        response = self.ser.readline().decode("utf-8")
        return response

    def record_weigh(self) -> float:
        """Request a displayed weight in milligrams, or return None on a read failure."""

        try:
            if self.ser.in_waiting == 0:
                self.ser.write("\033P\n".encode("utf-8"))
                response = self.ser.readline().decode("utf-8")
                weight = response[1:11].replace(" ", "")
                self.logger.info(f"Measured weight: {weight} mg")
                return float(weight)
        except Exception as e:
            self.ser.readall()
            return None

    def value(self):
        """
        Return displayed scale value.
        """
        try:
            if self.ser.inWaiting() == 0:
                self.ser.write("\033P\n".encode("utf-8"))
                answer = self.ser.readline().decode("utf-8")
                sign = answer[0]
                ans = answer[1:11].replace(" ", "")
                unit = answer[11:14].replace(" ", "")
            # else: # menu code 7.1.2
            return float(ans)
        except:
            self.ser.read_all()
            return "NA"

    def weigh(self) -> float:
        res = self.value()
        while res == "NA":
            sleep(0.5)
            res = self.value()
        return res

    def stable_weight(self) -> float:
        res = self.value()
        while res == "NA":
            sleep(0.5)
            res = self.value()
        return res

    #     while True:

    #         sleep(0.2)
    #         prev_weight.append(weight)
    #         prev_weight.pop(0)
    #             prev_weight[0] != None
    #             and prev_weight[1] != None
    #             and prev_weight[2] != None
    #             and prev_weight[3] != None
    #             and prev_weight[4] != None
    #         ):
    #         else:

    def close(self):
        if self.ser.is_open:
            self.ser.close()
