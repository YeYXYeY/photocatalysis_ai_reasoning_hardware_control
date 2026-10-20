from typing import Union
from crccheck.crc import Crc16Modbus as cm


def calc_crc(data: Union[str, bytes]) -> Union[str, bytes]:
    """Append a little-endian Modbus CRC16.

    Accept hexadecimal text or bytes and preserve the input representation."""

    if isinstance(data, str):
        data_bytes = bytes.fromhex(data)
    elif isinstance(data, bytes):
        data_bytes = data
    else:
        raise ValueError("Invalid data type. Expected str or bytes.")

    crc = cm.calc(data_bytes)
    crc_bytes = crc.to_bytes(2, "little")

    if isinstance(data, str):
        return (data_bytes + crc_bytes).hex(" ").upper()
    else:
        return data_bytes + crc_bytes


if __name__ == "__main__":
    print(calc_crc(b"\x01\x06\x00\x01\x00\xc8").hex(" "))
