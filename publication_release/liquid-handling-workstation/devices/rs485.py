import re
import struct
import serial
from time import sleep

from devices.motion import Motion


class MyError(Exception):
    def __init__(self, message, code=9999):
        super().__init__(message)
        self.code = code

    def __str__(self):
        return f"{self.code}: {self.args[0]}"


class RS485:
    VALID_KEYS = {
        "port",
        "baudrate",
        "bytesize",
        "parity",
        "stopbits",
        "timeout",
        "write_timeout",
    }
    VALID_PUMP_FLAGS = {1, 2}

    def __init__(self, modbus_prm, logger) -> None:
        self.modbus_prm = modbus_prm
        self.logger = logger
        self.ser = None
        self._validate_config()
        try:
            self.ser = serial.Serial(**self.modbus_prm)
            self.logger.info("Opened the RS485 serial port.")
        except serial.SerialException as e:
            raise ValueError(f"Failed to initialize the RS485 serial port: {e}") from e
        self.motion = Motion(self.ser, self.logger)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def _validate_config(self):
        for key in self.modbus_prm:
            if key not in self.VALID_KEYS:
                raise ValueError(f"Unsupported RS485 configuration key: {key}")

    def _ensure_open(self):
        if not self.ser.is_open:
            self.ser.open()

    def connect(self):
        try:
            self.ser = serial.Serial(**self.modbus_prm)
            self.motion.ser = self.ser
        except serial.SerialException as e:
            raise ValueError(f"Failed to reconnect the RS485 serial port: {e}") from e

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.logger.info("Closed the RS485 serial port.")

    def init_devices(self, reset_rgi, reset_pge, reset_pump, pump_speed):
        self.send_msg(reset_pump)
        sleep(0.5)
        res = self.send_msg(reset_rgi)
        sleep(0.5)
        if res and res.hex() != reset_rgi.hex():
            self.logger.info("RS485 device initialization failed")
        res = self.send_msg(pump_speed)
        res = self.send_msg(reset_pge)
        if res and res.hex() != reset_pge.hex():
            self.logger.info("RS485 device initialization failed")

    def send_msg(self, msg: bytes):
        try:
            self._ensure_open()
            self.ser.write(msg)
            sleep(0.1)
            return self.recv_msg()
        except Exception as e:
            self.logger.info("Failed to send an RS485 message: %s", e)
            return None

    def recv_msg(self):
        response = None
        try:
            self._ensure_open()
            response = self.ser.read(1024)
        except Exception as e:
            self.logger.info("Failed to receive an RS485 message: %s", e)
        return response

    def gene_instr(self, addr: str, func: str, step: int, flag=0):
        """Build a pump command frame."""
        if flag not in self.VALID_PUMP_FLAGS:
            raise ValueError("Pump flag must be 1 or 2.")

        head = "CC"
        trail = "DD"
        encoded_step = struct.pack("<H", step).hex()
        data = head + addr + func + encoded_step + trail
        data = re.sub(r"(\w{2})", r"\1 ", data).strip()
        to_cal = data.split(" ")
        checksum_value = 0
        for byte in to_cal:
            checksum_value += int(byte, 16)
        checksum_hex = struct.pack("<H", checksum_value).hex()
        check = re.sub(r"(\w{2})", r"\1 ", checksum_hex).strip()
        frame = data + " " + check
        return bytes.fromhex(frame)

    def send_instr(self, addr: str, func: str, step: int, flag, ret=0) -> int:
        msg = self.gene_instr(addr, func, step, flag)
        rec_msg = b""
        try:
            self._ensure_open()
            self.ser.write(msg)
            rec_msg = self.ser.read(16)
            if not rec_msg:
                raise serial.SerialException("No response frame was received.")
            ret = 1
        except serial.SerialException as e:
            self.logger.info("Failed to send a pump instruction: %s", e)
        finally:
            if self.ser and self.ser.is_open:
                self.ser.close()
        return ret, rec_msg


# if __name__ == "__main__":
# reset_rgi = b"\x01\x06\x01\x00\x00\x01\x49\xF6"
# from utils.calc import calculate_crc

# reset_rgi = calculate_crc(b"\x04\x06\x01\x00\x00\x01")
# pos_0 = b"\x01\x06\x01\x03\x00\x00\x78\x36"
# pos_50 = b"\x01\x06\x01\x03\x01\xC2\xF8\x37"
# pos_100 = b"\x01\x06\x01\x03\x03\xE8\x78\x88"
# rotate_open = b"\x01\x06\x01\x09\x02\xD0\x58\xC8"
# rotate_close = b"\x01\x06\x01\x09\xFD\x2F\x59\x78"
# ratate_90 = b"\x01\x06\x01\x09\x00\x5A\xD8\x0F"
# rotate_speed_10 = b"\x01\x06\x01\x07\x00\x0A\xB9\xF0"

# Example command constants kept for manual serial debugging.
# reset_pge = b"\x02\x06\x01\x00\x00\x01\x49\xc5"
# pge_close = b"\x02\x06\x01\x03\x00\x00\x78\x05"
# pge_open = b"\x02\x06\x01\x03\x03\xE8\x78\xBB"
# rs485 = RS485()
# # sleep(5)
# # _, res = rs485.send_instr("01", "48", 0, 2)
# rs485.send_msg(reset_rgi)
