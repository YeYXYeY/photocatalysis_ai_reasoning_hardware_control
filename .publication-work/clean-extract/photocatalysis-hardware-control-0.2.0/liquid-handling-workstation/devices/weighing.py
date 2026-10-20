import yaml
import serial
import struct
from time import sleep


def calculate_crc(data: bytes) -> bytes:
    # 16 CRC 0xFFFF
    crc = 0xFFFF
    for byte in data:
        # XOR ( ): CRC 8 8 CRC
        crc ^= byte
        # ( 8 )
        for _ in range(8):
            # CRC LSB( ) 1, CRC , 0xA001 CRC
            if crc & 0x0001:
                # crc = (crc >> 1) ^ 0xA001
                crc = (crc >> 1) ^ 0xA001
            else:
                # CRC
                crc >>= 1
    # CRC
    crc = ((crc & 0xFF00) >> 8) | ((crc & 0x00FF) << 8)
    # CRC
    return crc.to_bytes(2, byteorder="big")


# yaml
class Weighing:
    def __init__(self) -> None:
        pass

    def weigh(self, param):
        weighing_param = param["weighing_modbus_prm"]
        relay_param = param["relay_modbus_prm"]

        target = 5000
        value = 0

        weigh = serial.Serial(**weighing_param)
        relay = serial.Serial(**relay_param)

        open1 = b"\x01\x05\x00\x10\xff\x00\x8d\xff"
        open2 = b"\x01\x05\x00\x11\xff\x00\xdc\x3f"
        close1 = b"\x01\x05\x00\x10\x00\x00\xcc\x0f"
        close2 = b"\x01\x05\x00\x11\x00\x00\x9d\xcf"
        close = b"\x01\x0f\x00\x10\x00\x04\x01\x00\xff\x55"
        clock = b"\x01\x0f\x00\x10\x00\x04\x01\x01\x3e\x95"
        unticlock = b"\x01\x0f\x00\x10\x00\x04\x01\x02\x7e\x94"
        # relay.write(close)
        relay.write(open1)
        sleep(2)
        relay.write(close1)
        while True:
            relay.write(clock)
            sleep(0.5)
            relay.write(unticlock)
            sleep(0.4)
