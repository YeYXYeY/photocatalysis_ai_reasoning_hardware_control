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
    return crc.to_bytes(2, byteorder='big')

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


        open1 = b'\x01\x05\x00\x10\xFF\x00\x8D\xFF'
        open2 = b'\x01\x05\x00\x11\xFF\x00\xDC\x3F'
        close1 = b'\x01\x05\x00\x10\x00\x00\xCC\x0F'
        close2 = b'\x01\x05\x00\x11\x00\x00\x9D\xCF'
        close = b'\x01\x0F\x00\x10\x00\x04\x01\x00\xFF\x55'
        clock = b'\x01\x0F\x00\x10\x00\x04\x01\x01\x3E\x95'
        unticlock = b'\x01\x0F\x00\x10\x00\x04\x01\x02\x7E\x94'
        # relay.write(close)
        relay.write(open1)
        sleep(2)
        relay.write(close1)
        while True:
            relay.write(clock)
            sleep(0.5)
            relay.write(unticlock)
            sleep(0.4)
        

        
