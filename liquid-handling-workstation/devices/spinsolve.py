import sys
import socket
import xml.etree.ElementTree as ET
import serial
from time import sleep, time
import struct
import re


pump_in_999 = bytes.fromhex("E9 01 06 57 4A 03 E7 01 01 FE")
pump_in_200 = bytes.fromhex("E9 01 06 57 4A 00 C8 01 01 D2")
pump_in_500 = bytes.fromhex("E9 01 06 57 4A 01 F4 01 01 EF")
close_pump_in_500 = bytes.fromhex("E9 01 06 57 4A 01 F4 00 01 EE")
close_pump_in_200 = bytes.fromhex("E9 01 06 57 4A 00 C8 00 01 D3")
close_pump_in_999 = bytes.fromhex("E9 01 06 57 4A 03 E7 00 01 FF")
pump_out_999 = bytes.fromhex("E9 01 06 57 4A 03 E7 01 00 FF")
close_pump_out_999 = bytes.fromhex("E9 01 06 57 4A 03 E7 00 00 FE")
pump_out_200 = bytes.fromhex("E9 01 06 57 4A 00 C8 01 00 D3")
close_pump_out_200 = bytes.fromhex("E9 01 06 57 4A 00 C8 00 00 D2")
serial_settings = {
    "port": "COM7",
    "baudrate": 9600,
    "bytesize": serial.EIGHTBITS,
    "parity": "N",
    "stopbits": serial.STOPBITS_ONE,
    "timeout": 0.5,  # ( )
}
socket_settings = ("localhost", 13000)


class MyError(Exception):
    def __init__(self, message, code=9999):
        super().__init__(message)
        self.code = code

    def __str__(self):
        return f"{self.code}: {self.args[0]}"


# with , , .
class Spinsolve:
    def __init__(self, serial_settings, socket_settings, logger) -> None:
        self.logger = logger
        try:
            self.ser = serial.Serial(**serial_settings)
            self.logger.info("Opened the NMR peristaltic pump serial port successfully.")
        except serial.SerialException as e:
            self.logger.info("Failed to open the NMR peristaltic pump serial port: %s", e)
            self.ser = None
            sys.exit(1)

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect(socket_settings)
        except (socket.timeout, socket.error) as e:
            self.logger.info("Failed to connect to the Spinsolve server: %s", e)
            self.sock = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def connect(self):
        pass

    def close(self):
        pass

    def send_tcp(self, data):
        if self.sock:
            try:
                self.sock.sendall(data.encode())
                # self.logger.info("Sent data to TCP/IP server:", data)
            except (socket.timeout, socket.error) as e:
                self.logger.info(f"Failed to send data to TCP/IP server: {e}")
                sys.exit(-1)

    def recv_tcp(self, bufsize=1024):
        if self.sock:
            try:
                data = self.sock.recv(bufsize)
                return data.decode()
            except (socket.timeout, socket.error) as e:
                self.logger.info(f"Failed to receive data from TCP/IP server: {e}")
                return None

    def send_serial(self, data):
        if self.ser:
            try:
                self.ser.write(data)
                self.logger.info("Sent data to serial port:", data)
            except serial.SerialException as e:
                self.logger.info(f"Failed to send data to serial port: {e}")

    def recv_serial(self, bufsize=1024):
        if self.ser:
            try:
                data = self.ser.read(bufsize)
                self.logger.info("Received data from serial port:", data)
                return data.decode()
            except serial.SerialException as e:
                self.logger.info(f"Failed to receive data from serial port: {e}")
                return None

    def gene_instr(self, addr: str, func: str, step: int, flag=0):
        head = "CC"
        trail = "DD"
        try:
            if flag == 1:
                step = struct.pack("<H", step).hex()
                data = head + addr + func + step + trail
            elif flag == 2:
                step = struct.pack("<H", step).hex()
                data = head + addr + func + step + trail
            else:
                raise MyError("No target pump was selected.")

        except MyError as e:
            self.logger.info("Pump command error: %s", e)
        data = re.sub(r"(\w{2})", r"\1 ", data).strip()
        to_cal = data.split(" ")
        sum = 0
        for byte in to_cal:
            sum += int(byte, 16)
        sum = struct.pack("<H", sum).hex()
        check = re.sub(r"(\w{2})", r"\1 ", sum).strip()
        frame = data + " " + check
        return bytes.fromhex(frame)

    def send_instr(self, addr: str, func: str, step: int, flag, ret=0) -> int:

        msg = self.gene_instr(addr, func, step, flag)
        try:
            if not self.ser.is_open:
                self.ser.open()
            self.ser.write(msg)
            # readline()
            rec_msg = self.ser.read(16)
            if not rec_msg:
                raise serial.SerialException("No response frame was received.")
            ret = 1
        except serial.SerialException as e:
            self.logger.info("Error: ", e.strerror)
        finally:
            self.ser.close()
        return ret, rec_msg

    def nmr_pump_in(self):
        self.send_instr("00", "4B", 200, 2)
        self.send_instr("00", "48", 0, 2)
        sleep(8)
        self.send_instr("00", "49", 0, 2)
        self.send_instr("00", "4B", 20, 2)
        self.send_instr("00", "48", 0, 2)

    def nmr_close_in(self):
        self.send_instr("00", "49", 0, 2)

    def pump_in_with_stop(self, duration):
        self.send_instr("00", "4B", 200, 2)
        self.send_instr("00", "48", 0, 2)
        sleep(duration)
        self.send_instr("00", "49", 0, 2)

    def pump_in_with_low_speed(self, duration):
        self.send_instr("00", "4B", 50, 2)
        self.send_instr("00", "48", 0, 2)
        sleep(duration)
        self.send_instr("00", "49", 0, 2)

    def pump_out_with_stop(self, duration):
        self.send_instr("00", "4B", 200, 2)
        self.send_instr("00", "47", 0, 2)
        sleep(duration)
        self.send_instr("00", "49", 0, 2)

    def pump_in_without_stop(self, duration):
        self.send_instr("00", "4B", 200, 2)
        self.send_instr("00", "48", 0, 2)
        sleep(duration)

    def pump_out_without_stop(self, duration):
        self.send_instr("00", "4B", 200, 2)
        self.send_instr("00", "47", 0, 2)
        sleep(duration)

    def pump_stop(self):
        self.send_instr("00", "49", 0, 2)

    def back_to(self, duration):
        self.send_instr("00", "4B", 20, 2)
        self.send_instr("00", "47", 0, 2)
        sleep(duration)
        self.send_instr("00", "49", 0, 2)

    def start_protocol(self, protocol, name, value):
        msg = f"""<?xml version="1.0" encoding="utf-8"?>
<Message>
    <Start protocol="{protocol}">
        <Option name="{name}" value="{value}" />
    </Start>
</Message>"""
        self.send_tcp(msg)
        response = self.recv_tcp()
        if not response:
            response = self.recv_tcp()

        try:
            stat_root = ET.fromstring(response)
            state_tags = stat_root.find(".//State")
            stat1 = state_tags.attrib["protocol"]
            stat2 = state_tags.attrib["status"]
            stat3 = state_tags.attrib["dataFolder"]
            spin_status = [stat1, stat2, stat3]
        except:
            spin_status = ["", "", ""]
        while True:
            response = self.recv_tcp()
            if response:
                print(response)
                if 'successful="true"' in response:
                    response = self.recv_tcp()
                    # self.logger.info(response)
                    try:
                        stat_root = ET.fromstring(response)
                        state_tags = stat_root.find(".//State")
                        protocol = state_tags.attrib["protocol"]
                        status = state_tags.attrib["status"]
                        datafolder = state_tags.attrib["dataFolder"]
                        spin_status = [protocol, status, datafolder]
                        self.logger.info(spin_status)
                        break
                    except:
                        break
            elif not response:
                print("no response")
                if protocol == "1D PROTON":
                    sleep(60)
                elif protocol == "1D FLUORINE":
                    sleep(210)
                return "failed"
        return spin_status

    def available_option_request(self, protocol):
        msg = f"""<?xml version="1.0" encoding="utf-8"?>
<Message> 
  <AvailableOptionsRequest protocol='{protocol}'/>
</Message>"""
        self.send_tcp(msg)
        response = self.recv_tcp()
        # self.logger.info(response)
        root = ET.fromstring(response)
        options_dict = {}
        for option in root.iter("Option"):
            option_name = option.get("name")
            option_values = [value.text for value in option.iter("Value")]
            options_dict[option_name] = option_values
        return options_dict[option_name]

    def available_protocol_request(self):
        msg = """<?xml version="1.0" encoding="utf-8"?>
    <Message>
        <AvailableProtocolsRequest/>
    </Message>"""

        self.send_tcp(msg)
        response = self.recv_tcp(10240)
        # self.logger.info(response)
        root = ET.fromstring(response)
        protocol_tags = root.findall(".//Protocol")
        protocols = [tag.text for tag in protocol_tags]
        # self.logger.info(protocols)
        return protocols


if __name__ == "__main__":
    import logging
    from devices.spinsolve import Spinsolve

    logger = logging.getLogger(__name__)
    spinsolve = Spinsolve(serial_settings, socket_settings, logger)
    # spinsolve.pump_out_with_stop(30)
    spinsolve.start_protocol("1D PROTON", "Scan", "StandardScan")
    # spinsolve.available_option_request("Pump")
    # spinsolve.start_protocol("Pump", "PumpOut", "30")
