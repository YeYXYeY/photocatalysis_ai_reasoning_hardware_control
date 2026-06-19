import serial
import struct
import re

reset = b'\xCC\x00\x45\x00\x00\xDD\xEE\x01'
extract_1ml = b'\xCC\x00\x4D\x60\x09\xDD\x5F\x02'
expel_500ul = b'\xCC\x00\x42\xB0\x04\xDD\x9F\x02'


class MyError(Exception):
    def __init__(self, message, code=9999):
        super().__init__(message)
        self.code = code

    def __str__(self):
        return f'{self.code}: {self.args[0]}'

class Pump:
    def __init__(self, param) -> None:
        self.param = param
        valid_keys = ['port', 'baudrate',
                      'bytesize', 'parity', 'stopbits', 'timeout', 'write_timeout']
        for key in param.keys():
            if key not in valid_keys:
                raise ValueError(f"Invalid parameter: {key}")
        try:
            self.ser = serial.Serial(**self.param)
            self.ser.write(b'\xCC\x00\x45\x00\x00\xDD\xEE\x01')
            # self.ser.write(b'\xCC\x01\x45\x00\x00\xDD\xEF\x01')
            # self.ser.write(b'\xCC\x02\x45\x00\x00\xDD\xF0\x01')
            # self.ser.write(b'\xCC\x03\x45\x00\x00\xDD\xF1\x01')
        except serial.SerialException as e:
            raise ValueError(f"Failed to open the serial port or initialize the pump: {e}")

    def gen_pump_instr(self, volume: float, addr: bytes, func: bytes, flag: int = 0):
        # + +
        head = b'\xCC' + addr + func
        # flag
        if flag == 1:
            step_per_ml = 2400
            steps = volume * step_per_ml
            steps = hex(int(steps))[2:].zfill(4)
            print(steps)
            steps_hex = bytes.fromhex(steps)[::-1]
            print(steps_hex)
        elif flag == 2:
            steps = hex(int(volume))[2:].zfill(4)
            steps_hex = bytes.fromhex(steps)[::-1]
        data = head + steps_hex + b'\xDD'
        data_sum = hex(sum(data))[2:].zfill(4)
        data_sum_rev = bytes.fromhex(data_sum)[::-1]
        data_frame = data + data_sum_rev
        return data_frame

    def gene_instr(self, addr: str, func: str, volume: float, flag=0):
        head = 'CC'
        trail = 'DD'
        try:
            if flag == 1:
                step_per_ml = 2400
                step = int(volume * step_per_ml)
                step = struct.pack('<H', step).hex()
                data = head + addr + func + step + trail
            elif flag == 2:
                step = int(volume * 2400)
                step = struct.pack('<H', step).hex()
                data = head + addr + func + step + trail
            else:
                raise MyError("No target pump was selected.")

        except MyError as e:
            print(f"Pump command error: {e}")
        data = re.sub(r"(\w{2})", r"\1 ", data).strip()
        to_cal = data.split(' ')
        sum = 0
        for byte in to_cal:
            sum += int(byte, 16)
        print(sum)
        sum = struct.pack('<H', sum).hex()
        check = re.sub(r"(\w{2})", r"\1 ", sum).strip()
        frame = data + ' ' + check
        return bytes.fromhex(frame)

    def send_message(self, addr: str, func: str, volume: float, flag, ret=0) -> int:
        msg = self.gene_instr(addr, func, volume, flag)
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
            print("Error: ", e.strerror)
        finally:
            self.ser.close()
        return ret

if __name__ == "__main__":
    pump = Pump()
    pump.send_message('03','41', 2, 2)
