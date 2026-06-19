import sys
from devices.zmotion.zauxdllPython import *
from time import sleep
import serial
from typing import Optional


class MyError(Exception):
    def __init__(self, message, code=9999):
        super().__init__(message)
        self.code = code

    def __str__(self):
        return f"{self.code}: {self.args[0]}"


class Controller:
    def __init__(self, motion_prm, logger, ser):
        self.logger = logger
        self.ser = ser
        # Check if all necessary keys are in motion_prm
        required_keys = [
            "ipaddr",
            "axis",
            "axislist",
            "op",
            "param_x",
            "param_y",
            "param_z",
            "param_datum_x",
            "param_datum_y",
            "param_datum_z",
        ]
        for key in required_keys:
            if key not in motion_prm:
                raise ValueError(f"motion_prm is missing key: {key}")

        # Motion controller parameters.
        self.ipaddr = motion_prm["ipaddr"]
        self.iaxisnum = motion_prm["axis"]
        self.iaxislist = motion_prm["axislist"]
        self.op = motion_prm["op"]
        self.param_x = motion_prm["param_x"]
        self.param_y = motion_prm["param_y"]
        self.param_z = motion_prm["param_z"]
        self.param_datum_x = motion_prm["param_datum_x"]
        self.param_datum_y = motion_prm["param_datum_y"]
        self.param_datum_z = motion_prm["param_datum_z"]
        self.axis_x = self.iaxisnum["x"]
        self.axis_y = self.iaxisnum["y"]
        self.axis_z = self.iaxisnum["z"]

        self.gripper_pos_x = 5600
        self.gripper_pos_y = 100
        self.gripper_pos_z = 100
        self.datum_flag = 0
        self.zaux = ZAUXDLL()
        try:
            ret = self.zaux.ZAux_OpenEth(self.ipaddr)
            if ret != 0:
                raise MyError("Failed to connect to the controller over Ethernet.", ret)
            self.logger.info("Connected to the controller successfully.")
        except MyError as e:
            self.logger.error("Controller initialization failed: %s", e)
            raise

        for i, o in enumerate(self.op):
            operation = self.op[i]
            try:
                ret = self.zaux.ZAux_Direct_SetOp(operation, 1)
                if ret != 0:
                    raise MyError("Failed to enable the output port.", code=ret)
            except MyError as e:
                self.logger.error("Output port setup failed: %s", e)
                raise

        self.logger.info("Output ports enabled successfully.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def connect(self):
        try:
            ret = self.zaux.ZAux_OpenEth(self.ipaddr)
            if ret != 0:
                raise MyError("Failed to connect to the controller over Ethernet.", ret)
            self.logger.info("Connected to the controller successfully.")
        except MyError as e:
            self.logger.error("Controller connection failed: %s", e)
            raise

        for i, operation in enumerate(self.op):
            try:
                ret = self.zaux.ZAux_Direct_SetOp(operation, 1)
                if ret != 0:
                    raise MyError("Failed to enable the output port.", code=ret)
            except MyError as e:
                self.logger.error("Output port setup failed: %s", e)
                raise

        self.logger.info("Output ports enabled successfully.")

    def disconnect(self):
        ret = self.zaux.ZAux_Close()
        self.check_command(ret)
        self.logger.info("Disconnected from the controller.")

    def get_datum_in(self):
        pass

    def check_command(self, ret: int):
        if ret != 0:
            self.logger.error("Controller command failed with return code %s.", ret)
            sys.exit(1)

    def r(self):
        for i, j in enumerate(self.op):
            self.logger.info("Operation index %s uses output %s.", i, j)

    def datum_xyz(self):
        self.axis_status()
        # Home the Z axis first.
        self.zaux.ZAux_Direct_SetAtype(self.axis_z, self.param_datum_z[0])
        self.zaux.ZAux_Direct_SetInvertStep(self.axis_z, self.param_datum_z[1])
        self.zaux.ZAux_Direct_SetDpos(self.axis_z, self.param_datum_z[2])
        # self.zaux.ZAux_Direct_SetMpos(self.axis_z, param_datum_z[3])
        self.zaux.ZAux_Direct_SetUnits(self.axis_z, self.param_datum_z[4])
        self.zaux.ZAux_Direct_SetAccel(self.axis_z, self.param_datum_z[5])
        self.zaux.ZAux_Direct_SetDecel(self.axis_z, self.param_datum_z[6])
        self.zaux.ZAux_Direct_SetSpeed(self.axis_z, self.param_datum_z[7])
        self.zaux.ZAux_Direct_SetSramp(self.axis_z, self.param_datum_z[8])
        self.zaux.ZAux_Direct_SetDatumIn(self.axis_z, self.param_datum_z[9])
        self.zaux.ZAux_Direct_SetCreep(self.axis_z, self.param_datum_z[10])
        ret = self.zaux.ZAux_Direct_Single_Datum(self.axis_z, self.param_datum_z[11])
        self.check_command(ret)
        # Wait for the Z axis homing sequence to complete.
        while 1:
            ret, val = self.zaux.ZAux_Direct_GetHomeStatus(self.axis_z)
            self.check_command(ret)
            if val:
                break

        # Home the X axis.
        self.zaux.ZAux_Direct_SetAtype(self.axis_x, self.param_datum_x[0])
        self.zaux.ZAux_Direct_SetInvertStep(self.axis_x, self.param_datum_x[1])
        self.zaux.ZAux_Direct_SetDpos(self.axis_x, self.param_datum_x[2])
        # self.zaux.ZAux_Direct_SetMpos(self.axis_x, param_datum_x[3])
        self.zaux.ZAux_Direct_SetUnits(self.axis_x, self.param_datum_x[4])
        self.zaux.ZAux_Direct_SetAccel(self.axis_x, self.param_datum_x[5])
        self.zaux.ZAux_Direct_SetDecel(self.axis_x, self.param_datum_x[6])
        self.zaux.ZAux_Direct_SetSpeed(self.axis_x, self.param_datum_x[7])
        self.zaux.ZAux_Direct_SetSramp(self.axis_x, self.param_datum_x[8])
        self.zaux.ZAux_Direct_SetDatumIn(self.axis_x, self.param_datum_x[9])
        self.zaux.ZAux_Direct_SetCreep(self.axis_x, self.param_datum_x[10])
        ret = self.zaux.ZAux_Direct_Single_Datum(self.axis_x, self.param_datum_x[11])
        self.check_command(ret)
        # Home the Y axis.
        self.zaux.ZAux_Direct_SetAtype(self.axis_y, self.param_datum_y[0])
        self.zaux.ZAux_Direct_SetInvertStep(self.axis_y, self.param_datum_y[1])
        self.zaux.ZAux_Direct_SetDpos(self.axis_y, self.param_datum_y[2])
        # self.zaux.ZAux_Direct_SetMpos(self.axis_y, param_datum_y[3])
        self.zaux.ZAux_Direct_SetUnits(self.axis_y, self.param_datum_y[4])
        self.zaux.ZAux_Direct_SetAccel(self.axis_y, self.param_datum_y[5])
        self.zaux.ZAux_Direct_SetDecel(self.axis_y, self.param_datum_y[6])
        self.zaux.ZAux_Direct_SetSpeed(self.axis_y, self.param_datum_y[7])
        self.zaux.ZAux_Direct_SetSramp(self.axis_y, self.param_datum_y[8])
        self.zaux.ZAux_Direct_SetDatumIn(self.axis_y, self.param_datum_y[9])
        self.zaux.ZAux_Direct_SetCreep(self.axis_y, self.param_datum_y[10])
        ret = self.zaux.ZAux_Direct_Single_Datum(self.axis_y, self.param_datum_y[11])
        self.check_command(ret)
        while 1:
            ret2, val2 = self.zaux.ZAux_Direct_GetHomeStatus(self.axis_x)
            self.check_command(ret2)
            ret3, val3 = self.zaux.ZAux_Direct_GetHomeStatus(self.axis_y)
            self.check_command(ret3)
            if val2 and val3:
                break
        sleep(3)
        # Reset the position registers after homing completes.
        ret = self.zaux.ZAux_Direct_SetDpos(self.axis_x, 0.000)
        self.check_command(ret)
        ret = self.zaux.ZAux_Direct_SetDpos(self.axis_y, 0.000)
        self.check_command(ret)
        ret = self.zaux.ZAux_Direct_SetDpos(self.axis_z, 0.000)
        self.check_command(ret)
        ret = self.zaux.ZAux_Direct_SetMpos(self.axis_x, 0.000)
        self.check_command(ret)
        ret = self.zaux.ZAux_Direct_SetMpos(self.axis_y, 0.000)
        self.check_command(ret)
        ret = self.zaux.ZAux_Direct_SetMpos(self.axis_z, 0.000)
        self.check_command(ret)

        # Move to the handoff position used by the robot arm.
        self.set_motion_params()
        self.move_xyz(self.gripper_pos_x, self.gripper_pos_y, self.gripper_pos_z)
        self.datum_flag = 1
        self.logger.info("XYZ axes homed successfully.")

    def set_speed(self, axis: str, speed: float):
        self.zaux.ZAux_Direct_SetSpeed(self.iaxisnum[axis], speed)
        while True:
            ret, val = self.zaux.ZAux_Direct_GetSpeed(self.iaxisnum[axis])
            if speed == round(val.value, 2):
                break
            else:
                self.logger.warning(
                    "Retrying speed update for axis %s to %.2f.", axis, speed
                )

    def get_speed(self, axis: str):
        ret1, speed = self.zaux.ZAux_Direct_GetSpeed(self.iaxisnum[axis])
        ret2, mspeed = self.zaux.ZAux_Direct_GetMspeed(self.iaxisnum[axis])
        return speed, mspeed

    def set_motion_params(self):
        # Apply the shared motion profile to each configured axis.
        for axis in self.iaxislist:
            try:
                ret1 = self.zaux.ZAux_Direct_SetAtype(axis, self.param_x[0])
                if ret1 != 0:
                    raise Exception(
                        f"Error in ZAux_Direct_SetAtype with return value: {ret1}"
                    )

                ret2 = self.zaux.ZAux_Direct_SetInvertStep(axis, self.param_x[1])
                if ret2 != 0:
                    raise Exception(
                        f"Error in ZAux_Direct_SetInvertStep with return value: {ret2}"
                    )

                ret3 = self.zaux.ZAux_Direct_SetUnits(axis, self.param_x[2])
                if ret3 != 0:
                    raise Exception(
                        f"Error in ZAux_Direct_SetUnits with return value: {ret3}"
                    )

                ret4 = self.zaux.ZAux_Direct_SetAccel(axis, self.param_x[3])
                if ret4 != 0:
                    raise Exception(
                        f"Error in ZAux_Direct_SetAccel with return value: {ret4}"
                    )

                ret5 = self.zaux.ZAux_Direct_SetDecel(axis, self.param_x[4])
                if ret5 != 0:
                    raise Exception(
                        f"Error in ZAux_Direct_SetDecel with return value: {ret5}"
                    )

                ret6 = self.zaux.ZAux_Direct_SetSpeed(axis, self.param_x[5])
                if ret6 != 0:
                    raise Exception(
                        f"Error in ZAux_Direct_SetSpeed with return value: {ret6}"
                    )
                self.logger.info("Motion parameters applied to axis %s.", axis)
            except Exception as e:
                self.logger.error("%s", e)
                sys.exit(1)  # Exit the program with an error code of 1.

    def axis_status(self):
        try:
            ret1, value1 = self.zaux.ZAux_Direct_GetAxisStatus(0)
            ret2, value2 = self.zaux.ZAux_Direct_GetAxisStatus(1)
            ret3, value3 = self.zaux.ZAux_Direct_GetAxisStatus(2)

            status_x = value1.value
            status_y = value2.value
            status_z = value3.value
            # print(status_x, status_y, status_z)

            if status_x != 0:
                raise ValueError(f"Error: axis x's status code is {status_x}")

            if status_y != 0:
                raise ValueError(f"Error: axis y's status code is {status_y}")

            if status_z != 0:
                raise ValueError(f"Error: axis z's status code is {status_z}")
        except ValueError as e:
            self.logger.error("%s", e)
            sys.exit(1)

    def single_move_abs(self, axis: str, position: float):
        # Execute a guarded single-axis absolute move.
        self.axis_status()
        if axis == "x" or axis == "y":
            if self.datum_flag == 1:
                # XY motion is only allowed once Z is in the safe position.
                self.get_axis_status()
        position = round(position, 2)
        ret = self.zaux.ZAux_Direct_Single_MoveAbs(self.iaxisnum[axis], position)
        self.check_command(ret)
        while 1:
            ret, idle = self.zaux.ZAux_Direct_GetIfIdle(self.iaxisnum[axis])
            if int(idle.value) == -1:
                break
        try:
            ret, mpos = self.zaux.ZAux_Direct_GetDpos(self.iaxisnum[axis])
            mpos = round(float(mpos.value), 2)

            if mpos != position:
                raise MyError(f"{axis}-axis did not reach the requested position.", ret)
        except MyError as e:
            self.logger.error("Single-axis move failed: %s", e)
            raise
        except Exception as e:
            self.logger.error("Unexpected motion error: %s", e)
            raise

    def single_move_abs_nocheck(self, axis: str, position: float):
        # Execute an absolute move without the XY safety interlock.
        position = round(position, 2)
        ret = self.zaux.ZAux_Direct_Single_MoveAbs(self.iaxisnum[axis], position)
        self.check_command(ret)
        while 1:
            ret, idle = self.zaux.ZAux_Direct_GetIfIdle(self.iaxisnum[axis])
            if int(idle.value) == -1:
                break
        try:
            ret, mpos = self.zaux.ZAux_Direct_GetDpos(self.iaxisnum[axis])
            mpos = round(float(mpos.value), 2)

            if mpos != position:
                raise MyError(f"{axis}-axis did not reach the requested position.", ret)
        except MyError as e:
            self.logger.error("Unchecked single-axis move failed: %s", e)
            raise
        except Exception as e:
            self.logger.error("Unexpected motion error: %s", e)
            raise

    def move_xyz(self, x, y, z):
        self.axis_status()
        x = round(float(x), 2)
        y = round(float(y), 2)
        z = round(float(z), 2)
        if self.datum_flag == 1:
            self.get_axis_status()

        retx = self.zaux.ZAux_Direct_Single_MoveAbs(0, x)
        rety = self.zaux.ZAux_Direct_Single_MoveAbs(1, y)
        self.check_command(retx)
        self.check_command(rety)
        while True:
            _, idle1 = self.zaux.ZAux_Direct_GetIfIdle(0)
            _, idel2 = self.zaux.ZAux_Direct_GetIfIdle(1)
            if idle1.value == -1 and idel2.value == -1:
                break
        try:
            ret1, mpos1 = self.zaux.ZAux_Direct_GetDpos(0)
            mpos1 = round(float(mpos1.value), 2)

            if mpos1 != x:
                raise MyError("X axis did not reach the requested position.", ret1)

            ret2, mpos2 = self.zaux.ZAux_Direct_GetDpos(1)
            mpos2 = round(float(mpos2.value), 2)

            if mpos2 != y:
                raise MyError("Y axis did not reach the requested position.", ret2)
        except MyError as e:
            self.logger.error("XY move failed: %s", e)
            raise
        except Exception as e:
            self.logger.error("Unexpected motion error: %s", e)
            raise

        retz = self.zaux.ZAux_Direct_Single_MoveAbs(2, z)
        self.check_command(retz)
        while True:
            _, idle3 = self.zaux.ZAux_Direct_GetIfIdle(2)
            if idle3.value == -1:
                break
        try:
            ret3, mpos3 = self.zaux.ZAux_Direct_GetDpos(2)
            mpos3 = round(float(mpos3.value), 2)

            if mpos3 != z:
                raise MyError("Z axis did not reach the requested position.", ret3)

        except MyError as e:
            self.logger.error("XYZ move failed: %s", e)
            raise
        except Exception as e:
            self.logger.error("Unexpected motion error: %s", e)
            raise

    def movez(self, z):
        retz = self.zaux.ZAux_Direct_Single_MoveAbs(2, float(z))
        self.check_command(retz)
        while True:
            _, idle3 = self.zaux.ZAux_Direct_GetIfIdle(2)
            if idle3.value == -1:
                break
        try:
            ret3, mpos3 = self.zaux.ZAux_Direct_GetDpos(2)
            mpos3 = round(float(mpos3.value), 2)

            if mpos3 != z:
                raise MyError("Z axis did not reach the requested position.", ret3)

        except MyError as e:
            self.logger.error("Z move failed: %s", e)
            raise
        except Exception as e:
            self.logger.error("Unexpected motion error: %s", e)
            raise

    def send_instr(self, instrution) -> Optional[str]:
        instr = bytes.fromhex(instrution)
        try:
            if not self.ser.is_open:
                self.ser.open()
            self.ser.write(instr)
            for attempt in range(3):
                res = self.ser.read(8)
                if res:
                    break
                self.ser.write(instr)
            else:
                self.logger.error("No serial response was received after 3 attempts.")
                sys.exit(1)

        except serial.SerialException as e:
            self.logger.error("Serial communication failed: %s", e)
            return None

        return res.hex() if res else None

    def get_input_status(self):
        instrution = "1f 03 01 79 00 01 57 91"
        res = self.send_instr(instrution)[6:10]
        input_status_dec = int(res, 16)
        input_status = bin(input_status_dec)[2:].zfill(16)[-4]
        return int(input_status)

    def get_axis_status(self):
        input_status = self.get_input_status()
        if input_status == 1:
            return
        else:
            self.logger.error(
                "Z is not in the safe position, so XY motion is blocked."
            )
            sys.exit(-1)

    def test(self, axis: str):
        ret, val = self.zaux.ZAux_Direct_GetIfIdle(self.iaxisnum[axis])
        self.logger.info("Axis %s idle query returned %s, %s.", axis, ret, val.value)
