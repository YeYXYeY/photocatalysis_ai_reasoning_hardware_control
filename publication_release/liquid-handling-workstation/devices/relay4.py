from utils.calc import *


class Relay4:
    def __init__(self, param: dict, id: int, do_list: list = []) -> None:
        self.id = id.to_bytes(1, "little")
        self.open_all_do = bytes.fromhex("0F 00 10 00 10 02 FF FF")
        self.open_ins = crc_little(self.id + self.open_all_do)

    def __enter__(self):
        # with
        print("Initializing resources...")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # with
        print("Cleaning up resources...")

    def connect():
        pass


if __name__ == "__main__":
    rel = Relay4(7)
    print(rel.id)
    print(rel.open_all_do)
    print(rel.open_ins.hex())

    hexs = "0700100010"
    bytess = bytes.fromhex(hexs)
    print(bytess)
