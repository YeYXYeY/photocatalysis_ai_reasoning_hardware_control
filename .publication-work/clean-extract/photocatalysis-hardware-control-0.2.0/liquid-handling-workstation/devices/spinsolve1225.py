import socket
import xml.etree.ElementTree as ET
import serial
from time import sleep, time


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
    "port": "COM3",
    "baudrate": 1200,
    "bytesize": serial.EIGHTBITS,
    "parity": serial.PARITY_EVEN,
    "stopbits": serial.STOPBITS_ONE,
    "timeout": 1,  # ( )
}
socket_settings = ("localhost", 13000)


# with , , .
class Spinsolve:
    def __init__(self, serial_settings, socket_settings) -> None:
        try:
            self.ser = serial.Serial(**serial_settings)
            print("Opened the BT100 peristaltic pump serial port successfully.")
        except serial.SerialException as e:
            print(f"Failed to open the BT100 peristaltic pump serial port: {e}")
            self.ser = None
            # sys.exit(1)

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect(socket_settings)
        except (socket.timeout, socket.error) as e:
            print(f"Failed to connect to the Spinsolve server: {e}")
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
                print("Sent data to TCP/IP server:", data)
            except (socket.timeout, socket.error) as e:
                print(f"Failed to send data to TCP/IP server: {e}")

    def recv_tcp(self, bufsize=1024):
        if self.sock:
            try:
                data = self.sock.recv(bufsize)
                return data.decode()
            except (socket.timeout, socket.error) as e:
                print(f"Failed to receive data from TCP/IP server: {e}")
                return None

    def send_serial(self, data):
        if self.ser:
            try:
                self.ser.write(data)
                print("Sent data to serial port:", data)
            except serial.SerialException as e:
                print(f"Failed to send data to serial port: {e}")

    def recv_serial(self, bufsize=1024):
        if self.ser:
            try:
                data = self.ser.read(bufsize)
                print("Received data from serial port:", data)
                return data.decode()
            except serial.SerialException as e:
                print(f"Failed to receive data from serial port: {e}")
                return None

    def nmr_pump_in(self):
        self.send_serial(pump_in_999)
        sleep(20)
        self.send_serial(pump_in_200)

    def nmr_close_in(self):
        self.send_serial(close_pump_in_200)

    def pump_in(self, duration):
        self.send_serial(pump_in_999)
        sleep(duration)
        self.send_serial(close_pump_in_999)

    def pump_out(self, duration):
        self.send_serial(pump_out_999)
        sleep(duration)
        self.send_serial(close_pump_out_999)

    def back_to(self, duration):
        self.send_serial(pump_out_200)
        sleep(duration)
        self.send_serial(close_pump_out_200)

    def start_protocol(self, protocol, name, value):
        msg = f"""<?xml version="1.0" encoding="utf-8"?>
<Message>
    <Start protocol="{protocol}">
        <Option name="{name}" value="{value}" />
    </Start>
</Message>"""
        self.send_tcp(msg)
        response = self.recv_tcp()
        stat_root = ET.fromstring(response)
        state_tags = stat_root.find(".//State")
        try:
            stat1 = state_tags.attrib["protocol"]
            stat2 = state_tags.attrib["status"]
            stat3 = state_tags.attrib["dataFolder"]
            spin_status = [stat1, stat2, stat3]
        except:
            spin_status = ["", "", ""]
        while True:
            response = self.recv_tcp()
            if response:
                if 'successful="true"' in response:
                    response = self.recv_tcp()
                    print(response)
                    try:
                        stat_root = ET.fromstring(response)
                        state_tags = stat_root.find(".//State")
                        protocol = state_tags.attrib["protocol"]
                        status = state_tags.attrib["status"]
                        datafolder = state_tags.attrib["dataFolder"]
                        spin_status = [protocol, status, datafolder]
                        break
                    except:
                        break
        return spin_status

    def available_option_request(self, protocol):
        msg = f"""<?xml version="1.0" encoding="utf-8"?>
<Message> 
  <AvailableOptionsRequest protocol='{protocol}'/>
</Message>"""
        self.send_tcp(msg)
        response = self.recv_tcp()
        print(response)
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
        print(response)
        root = ET.fromstring(response)
        protocol_tags = root.findall(".//Protocol")
        protocols = [tag.text for tag in protocol_tags]
        print(protocols)
        return protocols


if __name__ == "__main__":
    spinsolve = Spinsolve(serial_settings, socket_settings)
    spinsolve.back_to(2)
