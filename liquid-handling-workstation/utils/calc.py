from crccheck.crc import Crc16Modbus


def calculate_crc(data: bytes) -> bytes:
    """Append a Modbus CRC using the existing big-endian project convention."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    crc = ((crc & 0xFF00) >> 8) | ((crc & 0x00FF) << 8)
    crc = crc.to_bytes(2, byteorder="big")

    return data + crc


def crc_little(data: bytes) -> bytes:
    crc = Crc16Modbus.calc(data)
    crc_bytes = crc.to_bytes(2, "little")
    return data + crc_bytes


def crc_big(data: bytes) -> bytes:
    crc = Crc16Modbus.calc(data)
    crc_bytes = crc.to_bytes(2, "big")
    return data + crc_bytes


def calc_xor(data: str):
    data_bytes = data.split()
    xor_results = 0
    for byte in data_bytes:
        xor_results ^= int(byte, 16)
    return xor_results

if __name__ == "__main__":
    data = b"\x11\x02\x00\x00\x00\x02"

    ins = calculate_crc(data)
    print(ins.hex())
