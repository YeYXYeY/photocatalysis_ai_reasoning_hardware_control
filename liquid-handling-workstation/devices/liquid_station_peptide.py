import pandas as pd
from devices.controller import *
from devices.rs485 import *
from devices.cr10 import *
from devices.trans200 import *
from devices.relay4 import *
from devices.weighing import *
from devices.spinsolve import *
from utils.calc import *
from utils.split_liquid_task import generate_task_df
from utils.config import config_logger
import os
import yaml
from time import sleep
import time
import math
from datetime import datetime
import datetime

current_path = os.path.abspath(os.path.dirname(__file__))
project_path = os.path.abspath(os.path.dirname(current_path))

# log , log
log_file = os.path.join(
    project_path, "log/" + datetime.datetime.now().strftime("%Y%m%d%H%m") + ".log"
)
logger = config_logger(log_file)

config_file = os.path.join(current_path, "config.yaml")
with open(config_file, "r", encoding="utf-8") as param:
    logger.info("Starting peptide liquid station runtime.")
    config = yaml.safe_load(param)
    logger.info("Loaded peptide liquid station configuration successfully.")

reset_rgi = calculate_crc(b"\x04\x06\x01\x00\x00\x01")
rgi_pos_0 = calculate_crc(b"\x04\x06\x01\x03\x00\x00")
rgi_pos_40 = calculate_crc(b"\x04\x06\x01\x03\x01\x90")
rgi_pos_50 = calculate_crc(b"\x04\x06\x01\x03\x01\xF4")  # 35%
rgi_pos_100 = calculate_crc(b"\x04\x06\x01\x03\x03\xE8")
rotate_open = calculate_crc(b"\x04\x06\x01\x09\x04\x38")
rotate_close = calculate_crc(b"\x04\x06\x01\x09\xFB\xC7")
rotate_90 = calculate_crc(b"\x04\x06\x01\x09\x00\x5A")
rotate_speed_12 = calculate_crc(b"\x04\x06\x01\x07\x00\x0C")
gripper_state = calculate_crc(b"\x04\x03\x02\x01\x00\x01")
open_cap_speed = 15
nomal_speed = 1500
saft_height = 100
saft_height_tip = 500
saft_height_bottle = 700
saft_height_pipetting = 700

gripper_pos_x = 5600
gripper_pos_y = 100
gripper_pos_z = 100

step = 12000
volume = 5000
reset_pump = b"\xCC\x00\x45\x00\x00\xDD\xEE\x01"
pump_speed = b"\xCC\x00\x4B\x64\x00\xDD\x58\x02"

reset_pge = calculate_crc(b"\x05\x06\x01\x00\x00\x01")
pge_close = calculate_crc(b"\x05\x06\x01\x03\x00\x00")
pge_open = calculate_crc(b"\x05\x06\x01\x03\x03\xE8")

serial_settings = {
    "port": "COM7",
    "baudrate": 9600,
    "bytesize": serial.EIGHTBITS,
    "parity": serial.PARITY_EVEN,
    "stopbits": serial.STOPBITS_ONE,
    "timeout": 1,  # ( )
}
socket_settings = ("localhost", 13000)

check_water_1 = b"\x11\x02\x00\x00\x00\x01\xBB\x5A"
check_water_2 = b"\x11\x02\x00\x01\x00\x01\xEA\x9A"
check_water_12 = b"\x11\x02\x00\x00\x00\x02\xFB\x5B"

relay_1_nc = b"\x11\x05\x00\x10\xFF\x00\x8F\x6F"
relay_1_no = b"\x11\x05\x00\x10\x00\x00\xCE\x9F"
relay_2_nc = b"\x11\x05\x00\x11\xFF\x00\xDE\xAF"
relay_2_no = b"\x11\x05\x00\x11\x00\x00\x9F\x5F"

relay_3_nc = calculate_crc(b"\x11\x05\x00\x12\xFF\x00")
relay_3_no = calculate_crc(b"\x11\x05\x00\x12\x00\x00")

reagent_df = pd.read_excel(os.path.join(project_path, "coordinates/reagent.xlsx"))
gripper_df = pd.read_excel(os.path.join(project_path, "coordinates/gripper.xlsx"))
reaction_for_pump_df = pd.read_excel(
    os.path.join(project_path, "coordinates/reaction_for_pump.xlsx")
)
reaction_for_pump2_df = pd.read_excel(
    os.path.join(project_path, "coordinates/reaction_for_pump2.xlsx")
)
slot_for_pump_df = pd.read_excel(
    os.path.join(project_path, "coordinates/slot_for_pump.xlsx")
)
dosing_head_df = pd.read_excel(
    os.path.join(project_path, "coordinates/dosing_head.xlsx")
)
tip_for_gripper_df = pd.read_excel(
    os.path.join(project_path, "coordinates/tip_for_gripper.xlsx")
)
reaction_for_dosing_df = pd.read_excel(
    os.path.join(project_path, "coordinates/reaction_for_dosing_wzy.xlsx")
)
slot_for_gripper_df = pd.read_excel(
    os.path.join(project_path, "coordinates/slot_for_gripper.xlsx")
)
clean_for_gripper_df = pd.read_excel(
    os.path.join(project_path, "coordinates/clean_for_gripper.xlsx")
)
nmr_prepare_df = pd.read_excel(
    os.path.join(project_path, "coordinates/nmr_prepare.xlsx")
)
reaction_for_gripper_df = pd.read_excel(
    os.path.join(project_path, "coordinates/reaction_for_gripper.xlsx")
)
tip_for_pump_df = pd.read_excel(
    os.path.join(project_path, "coordinates/tip_for_pump.xlsx")
)
tip_for_pump_file_path = os.path.join(project_path, "coordinates/tip_for_pump.xlsx")
tip_for_gripper_file_path = os.path.join(
    project_path, "coordinates/tip_for_gripper.xlsx"
)
rs485_param = config["RS485"]
controller_param = config["controller"]
trans200_param = config["trans200"]
cr10_param = config["cr10"]
peristaltic_pump = config["peristaltic_pump"]


class LiquidStation:
    def __init__(self, task_df):
        controller = Controller(controller_param, logger)
        spinsolve = Spinsolve(serial_settings, socket_settings, logger=logger)
        rs485 = RS485(modbus_prm=rs485_param, logger=logger)
        self.controller = controller
        self.spinsolve = spinsolve
        self.rs485 = rs485
        # log
        self.logger = logger
        self.task_df = task_df
        self.post_nmr_df = task_df
        self.pre_nmr_df = task_df
        self.nums_of_task = len(task_df)
        self.max_task = 28
        # nums_of_task 28
        if self.nums_of_task > 28:
            self.logger.info(
                f"Total number of tasks is {self.nums_of_task}, which is greater than the liquid station's capacity, please check the task file."
            )
            sys.exit(-1)
        self.reagent_df = reagent_df
        self.gripper_df = gripper_df
        self.reaction_for_pump_df = reaction_for_pump_df
        self.reaction_for_pump2_df = reaction_for_pump2_df
        self.slot_for_pump_df = slot_for_pump_df
        self.dosing_head_df = dosing_head_df
        self.tip_for_gripper_df = tip_for_gripper_df
        self.reaction_for_dosing_df = reaction_for_dosing_df
        self.slot_for_gripper_df = slot_for_gripper_df
        self.clean_for_gripper_df = clean_for_gripper_df
        self.nmr_prepare_df = nmr_prepare_df
        self.reaction_for_gripper_df = reaction_for_gripper_df
        self.tip_for_pump_df = tip_for_pump_df
        self.bottle_volume = 8000
        self.pre_task_df = self.task_df.copy()
        self.task_df = generate_task_df(
            self.task_df, self.reagent_df, self.bottle_volume
        )

    def init_devices(self):
        """This a function to initial all devices

        Args:
            spinsolve (Spinsolve): instance object of Spinsolve class
            controller (Controller): instance object of Controller class
            rs485 (RS485): instance object of RS485 class
        """
        self.controller.datum_xyz()  # zyx
        self.rs485.init_devices(reset_rgi, reset_pge, reset_pump, pump_speed)
        self.rs485.motion.initial_setup()
        self.rs485.motion.datum()
        self.rs485.send_msg(rgi_pos_50)
        sleep(1)
        self.rs485.send_msg(rotate_speed_12)
        sleep(1)
        self.controller.set_motion_params()
        sleep(1)
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)
        self.logger.info("Liquid station initialization completed\n")

    def pushrod(self, flag: int = 0):
        """This a function to pushrod\n
        Args:\n
            flag (int, optional):\n
                1: pushrod_out\n
                2: pushrod_in\n
                0: pushrod_stop\n
        """
        if flag == 1:
            self.rs485.send_msg(relay_1_nc)
            self.rs485.send_msg(relay_2_no)
            sleep(8)
            self.rs485.send_msg(relay_1_no)
            self.rs485.send_msg(relay_2_no)
            self.logger.info("pushrod in to hold the tip rack")
        elif flag == 2:
            self.rs485.send_msg(relay_1_no)
            self.rs485.send_msg(relay_2_nc)
            sleep(8)
            self.rs485.send_msg(relay_1_no)
            self.rs485.send_msg(relay_2_no)
            self.logger.info("pushrod out to release the tip rack")
        elif flag == 0:
            self.rs485.send_msg(relay_1_no)
            self.rs485.send_msg(relay_2_no)
        else:
            self.logger.error("Invalid flag value")
            sys.exit(-1)

    def gas_control(self, flag):
        if flag == 1:
            self.rs485.send_msg(relay_3_nc)
        else:
            self.rs485.send_msg(relay_3_no)

    def open_cap(self):
        self.set_rgi()
        open_cap_count = 0
        for index, row in self.reaction_for_gripper_df.iterrows():
            if open_cap_count == 5:
                self.set_rgi()
                open_cap_count = 0
            x_fix, y_fix, z_fix = self.gripper_df.loc[
                self.gripper_df["usage"] == "fix", ["X", "Y", "Z"]
            ].values[0]
            x_open, y_open, z_open = self.gripper_df.loc[
                self.gripper_df["usage"] == "open", ["X", "Y", "Z"]
            ].values[0]
            x_close, y_close, z_close = self.gripper_df.loc[
                self.gripper_df["usage"] == "close", ["X", "Y", "Z"]
            ].values[0]

            no = row["NO"]
            x = row["X"]
            y = row["Y"]
            z = row["Z"]
            cap = row["Cap"]
            xc = row["XC"]
            yc = row["YC"]
            zc = row["ZC"]
            empty = row["EMPTY"]

            if int(no) > self.nums_of_task:
                break
            self.controller.move_xyz(x, y, z)
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.controller.movez(saft_height_bottle)

            self.controller.move_xyz(x_fix, y_fix, z_fix)
            self.rs485.send_msg(pge_close)
            sleep(0.5)

            self.controller.set_speed("z", open_cap_speed)
            self.rs485.send_msg(rotate_open)
            self.controller.single_move_abs("z", float(z_open))
            sleep(1)
            self.controller.set_speed("z", nomal_speed)
            self.controller.single_move_abs("z", saft_height_bottle)

            self.controller.move_xyz(xc, yc, zc)
            self.rs485.send_msg(rgi_pos_50)
            sleep(0.5)
            self.controller.single_move_abs("z", saft_height_bottle)

            z_fix1 = float(z_fix) + 30
            self.controller.move_xyz(x_fix, y_fix, z_fix1)
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.rs485.send_msg(pge_open)
            sleep(1)
            self.controller.single_move_abs("z", saft_height_bottle)

            z_back = float(z) - 50
            self.controller.move_xyz(x, y, z_back)
            self.rs485.send_msg(rgi_pos_50)
            sleep(0.5)
            self.controller.single_move_abs("z", saft_height_bottle)
            open_cap_count += 1

            self.logger.info(f"Open the bottle cap of NO.{no} and finished")

        self.controller.single_move_abs("z", saft_height)
        self.set_rgi()
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)
        self.logger.info("Open all the bottle caps and finished")

    def set_rgi(self, flag=0):
        """


        flag: 0 ,1 90

        """
        self.rs485.send_msg(reset_rgi)
        sleep(3)
        self.rs485.send_msg(rgi_pos_50)
        sleep(1)
        self.rs485.send_msg(rotate_speed_12)
        sleep(1)
        if flag == 1:
            self.rs485.send_msg(rotate_90)
        self.logger.info("Reset the rotation gripper and finished")

    def prepare_solution(self):
        print(self.task_df)
        breakpoint()
        task_df = self.task_df.drop(columns=["NO"])
        # #
        not_null_column_sums = {}
        divided_not_null_columns = {}
        reactant_df = task_df.copy()

        self.logger.info("Start reactant adding")
        open_cap_count = 0
        for column in reactant_df.columns:
            if open_cap_count == 5:
                self.set_rgi()
                open_cap_count = 0
            reactant_df[column] = pd.to_numeric(reactant_df[column], errors="coerce")
            column_sum = reactant_df[column].sum()
            if column_sum == 0:
                continue
            self.logger.info(f"Statrting adding reactant {column}")

            not_null_column_sums[column] = column_sum

            divided_not_null_columns[column] = []
            index_list = []
            value_list = []
            sum_temp = 0
            # 2400
            for index, value in enumerate(reactant_df[column]):
                if pd.isnull(value):
                    continue
                value = math.ceil(value * step / volume)
                # If the value itself is greater than 2400, split it and store the same index multiple times
                if value > 2400:
                    divided_not_null_columns[column].append(
                        (index_list, value_list, sum_temp)
                    )  # 1000
                    index_list = []
                    value_list = []
                    sum_temp = 0
                    index_list.append(index)
                    value_list.append(2400)
                    divided_not_null_columns[column].append(
                        (index_list, value_list, 2400)
                    )  # 1000
                    index_list = []
                    value_list = []

                    index_list.append(index)
                    value_list.append(value - 2400)
                    divided_not_null_columns[column].append(
                        (index_list, value_list, value - 2400)
                    )  # 1000
                    index_list = []
                    value_list = []
                else:
                    sum_temp += value
                    index_list.append(index)
                    value_list.append(value)
                    if (
                        sum_temp > 2400
                    ):  # 1000,
                        divided_not_null_columns[column].append(
                            (index_list[:-1], value_list[:-1], sum_temp - value)
                        )  # 1000
                        index_list = [index_list[-1]]
                        value_list = [value_list[-1]]
                        sum_temp = value

            if index_list:
                divided_not_null_columns[column].append(
                    (index_list, value_list, sum_temp)
                )

            x_fix, y_fix, z_fix = self.gripper_df.loc[
                self.gripper_df["usage"] == "fix", ["X", "Y", "Z"]
            ].values[0]
            x_open, y_open, z_open = self.gripper_df.loc[
                self.gripper_df["usage"] == "open", ["X", "Y", "Z"]
            ].values[0]
            x_close, y_close, z_close = self.gripper_df.loc[
                self.gripper_df["usage"] == "close", ["X", "Y", "Z"]
            ].values[0]

            no, x, y, z, h = self.reagent_df.loc[
                self.reagent_df["Chemicals"] == column, ["NO", "X", "Y", "Z", "H"]
            ].values[0]

            # take the corresponding reagent bottle
            self.controller.single_move_abs("z", saft_height)
            # first move the linear slider to move the corresponding solvents bottle rack to the corresponding position
            self.rs485.motion.single_move("h", h)

            # move the three-axis module to the reagent bottle position
            self.controller.move_xyz(x, y, z)
            # close the gripper to take the reagent bottle
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            # move the three-axis module to the safe height
            self.controller.single_move_abs("z", saft_height)
            self.controller.move_xyz(x_fix, y_fix, z_fix)
            self.rs485.send_msg(pge_close)
            sleep(0.5)
            # move the linear slider to the initial position
            self.rs485.motion.single_move("h", 0)
            self.controller.set_speed("z", open_cap_speed)
            self.rs485.send_msg(rotate_open)
            self.controller.single_move_abs("z", float(z_open))
            sleep(1)
            self.controller.set_speed("z", nomal_speed)
            self.controller.single_move_abs("z", saft_height_tip)
            x3, y3, z3 = self.tip_for_pump_df.loc[
                self.tip_for_pump_df["Presence"] == 1, ["X", "Y", "Z"]
            ].values[0]
            index = self.tip_for_pump_df.loc[
                self.tip_for_pump_df["Presence"] == 1
            ].index[0]
            self.tip_for_pump_df.loc[index, "Presence"] = 0
            self.tip_for_pump_df.to_excel(
                tip_for_pump_file_path,
                index=False,
            )
            self.controller.move_xyz(x3, y3, z3)

            self.controller.single_move_abs("z", saft_height_tip)
            x4, y4, z4 = self.gripper_df.loc[
                self.gripper_df["usage"] == "pipette", ["X", "Y", "Z"]
            ].values[0]
            rinse_flag = 1

            for divided_list, value_list, sum_of_value in divided_not_null_columns[
                column
            ]:
                if len(divided_list) == 0:
                    continue
                self.controller.move_xyz(x4, y4, z4)
                self.logger.info(
                    f"Divided list: {divided_list}, Value list: {value_list}, Sum of value: {sum_of_value}"
                )
                if rinse_flag == 1:
                    self.rs485.send_instr("00", "4D", 2400, 1)
                    sleep(6)
                    self.rs485.send_instr("00", "42", 2400, 1)
                    sleep(7)
                self.rs485.send_instr("00", "4D", sum_of_value, 1)
                sleep(sum_of_value / 2400 * 6)
                self.controller.single_move_abs("z", saft_height_pipetting)

                x7, y7, z7 = self.slot_for_pump_df.loc[
                    self.slot_for_pump_df["usage"] == "BEFORE", ["X", "Y", "Z"]
                ].values[0]

                for index, value in zip(divided_list, value_list):
                    no = index + 1
                    x_thf, y_thf, z_thf = self.reaction_for_pump_df.loc[
                        self.reaction_for_pump_df["NO"] == no, ["X", "Y", "Z"]
                    ].values[0]
                    self.controller.move_xyz(x_thf, y_thf, z_thf)
                    self.rs485.send_instr("00", "42", value, 1)
                    sleep(value / 2400 * 6)
                    self.controller.single_move_abs("z", z7)

                rinse_flag = 0

            self.controller.move_xyz(x7, y7, z7)
            x8, y8, z8 = self.slot_for_pump_df.loc[
                self.slot_for_pump_df["usage"] == "GO", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", float(x8))
            x9, y9, z9 = self.slot_for_pump_df.loc[
                self.slot_for_pump_df["usage"] == "AFTER", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("z", float(z9))
            self.controller.single_move_abs("z", saft_height)

            self.controller.move_xyz(x_close, y_close, z_open)
            self.controller.set_speed("z", open_cap_speed)
            self.rs485.send_msg(rotate_close)
            self.controller.single_move_abs("z", float(z_close))
            sleep(0.5)
            self.rs485.send_msg(pge_open)
            sleep(0.5)
            self.controller.set_speed("z", nomal_speed)
            self.controller.single_move_abs("z", saft_height)
            self.rs485.motion.single_move("h", h)
            z_back = float(z) - 50
            self.controller.move_xyz(x, y, z_back)
            self.rs485.send_msg(rgi_pos_50)
            self.controller.single_move_abs("z", saft_height)
            open_cap_count += 1

            self.logger.info(f"Reactant {column} addition completed")

        self.logger.info(f"Reaction addition all completed")

        self.rs485.motion.single_move("h", 0)

        self.logger.info(f"Solvent addition all completed")
        self.controller.single_move_abs("z", saft_height)
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)

    def close_cap(self):
        self.set_rgi()

        # #
        open_cap_cout = 0
        for index, row in self.reaction_for_gripper_df.iterrows():
            if open_cap_cout == 5:
                self.set_rgi()
                open_cap_cout = 0
            x_fix, y_fix, z_fix = self.gripper_df.loc[
                self.gripper_df["usage"] == "fix", ["X", "Y", "Z"]
            ].values[0]
            x_open, y_open, z_open = self.gripper_df.loc[
                self.gripper_df["usage"] == "open", ["X", "Y", "Z"]
            ].values[0]
            x_close, y_close, z_close = self.gripper_df.loc[
                self.gripper_df["usage"] == "close", ["X", "Y", "Z"]
            ].values[0]
            no = row["NO"]
            x = row["X"]
            y = row["Y"]
            z = row["Z"]
            cap = row["Cap"]
            xc = row["XC"]
            yc = row["YC"]
            zc = row["ZC"]
            empty = row["EMPTY"]

            if int(no) > self.max_task:
                break
            z_catch = float(z) + 30
            self.controller.move_xyz(x, y, z_catch)
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.controller.single_move_abs("z", saft_height_bottle)

            z_fix2 = float(z_fix) + 30
            self.controller.move_xyz(x_fix, y_fix, z_fix2)
            self.rs485.send_msg(pge_close)
            sleep(0.5)
            self.rs485.send_msg(rgi_pos_50)
            sleep(0.5)
            self.controller.single_move_abs("z", saft_height_bottle)

            self.controller.move_xyz(xc, yc, zc)
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.controller.single_move_abs("z", saft_height_bottle)

            self.controller.move_xyz(x_open, y_open, z_open)

            self.controller.set_speed("z", open_cap_speed)
            self.rs485.send_msg(rotate_close)
            self.controller.single_move_abs("z", float(z_close))
            sleep(0.5)
            self.rs485.send_msg(pge_open)
            sleep(0.5)
            self.controller.set_speed("z", nomal_speed)
            self.controller.single_move_abs("z", saft_height_bottle)

            z_back = float(z) - 50
            self.controller.move_xyz(x, y, z_back)

            self.rs485.send_msg(rgi_pos_50)
            sleep(0.5)
            self.controller.single_move_abs("z", saft_height_bottle)
            open_cap_cout += 1
            self.logger.info(f"Close the bottle cap of NO.{no} and finished")

        self.controller.movez(saft_height)
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)

        self.logger.info("Close all the bottle caps and finished")

    def pre_nmr_test(self):
        self.logger.info("Starting pre-NMR-test")
        pre_nmr_df = self.task_df.drop(columns=["NO"])
        # solvent_df = pre_nmr_df.loc[:, pre_nmr_df.columns.str.contains("D")]
        # solvent_cols = solvent_df.columns.tolist()
        # solvent_name = solvent_cols[0]
        # solvent_addr = self.clean_for_gripper_df.loc[
        #     self.clean_for_gripper_df["usage"] == solvent_name, "addr"
        # ].values[0]
        # solvent_addr = "0" + str(solvent_addr)[0]
        self.set_rgi(1)
        x_dosing, y_dosing, z_dosing = self.dosing_head_df.loc[
            self.dosing_head_df["usage"] == "NMR", ["X", "Y", "Z"]
        ].values[0]
        self.controller.single_move_abs("x", x_dosing)
        self.controller.single_move_abs("y", y_dosing)
        self.controller.single_move_abs("z", z_dosing)
        # self.controller.move_xyz(x,y,z)
        self.rs485.send_msg(rgi_pos_0)
        sleep(0.5)
        self.controller.movez(saft_height)
        clean_flag = True
        completed_list = []
        uncompleted_list = []
        for index, row in self.pre_task_df.iterrows():
            no = row["NO"]
            # self.reaction_for_dosing_df NO no X,Y,Z,ZBack
            x, y, z, z_back = self.reaction_for_dosing_df.loc[
                self.reaction_for_dosing_df["NO"] == no, ["X", "Y", "Z", "ZBack"]
            ].values[0]
            if int(no) > self.max_task:
                break
            self.logger.info(f"Start to pre-NMR-test of NO.{no} task")
            # 200ul
            x1, y1, z1 = self.tip_for_gripper_df.loc[
                self.tip_for_gripper_df["Presence"] == 1, ["X", "Y", "Z"]
            ].values[0]
            tip_index = self.tip_for_gripper_df.loc[
                self.tip_for_gripper_df["Presence"] == 1
            ].index[0]
            self.tip_for_gripper_df.loc[tip_index, "Presence"] = 0
            self.tip_for_gripper_df.to_excel(
                tip_for_gripper_file_path,
                index=False,
            )
            # self.controller.move_xyz(x1,y1,z1)
            self.controller.single_move_abs("x", x1)
            self.controller.single_move_abs("y", y1)
            self.controller.single_move_abs("z", z1)
            self.controller.movez(saft_height)

            self.controller.single_move_abs("x", x)
            self.controller.single_move_abs("y", y)
            self.controller.single_move_abs("z", z)
            if clean_flag:
                self.rs485.send_instr("08", "40", 3400, 2)
                sleep(0.5)
                self.rs485.send_instr("03", "40", 3500, 2)
                clean_flag = False
            else:
                self.rs485.send_instr("08", "40", 3000, 2)
                sleep(0.5)
                self.rs485.send_instr("03", "40", 3000, 2)

            self.spinsolve.nmr_pump_in()
            times = 0
            while True:
                flag = 0
                for i in range(5):
                    res = self.rs485.send_msg(check_water_12)
                    res = res.hex()
                    if res[6:8] == "01" or res[6:8] == "02" or res[6:8] == "03":
                        flag += 1
                    sleep(1.5)
                if flag >= 4:
                    self.spinsolve.nmr_close_in()
                    # self.spinsolve.back_to(6)
                    state_proton = "failed"
                    state_fluorine = "failed"
                    state_proton = self.spinsolve.start_protocol(
                        "1D PROTON", "Scan", "StandardScan"
                    )
                    if state_proton == "failed":
                        self.logger.info(
                            f"Task NO.{int(no)}'s 【1D PROTON】test is not sure whether finished, please dobble check it"
                        )
                        break
                    state_fluorine = self.spinsolve.start_protocol(
                        "1D FLUORINE", "Scan", "PowerScan"
                    )
                    if state_fluorine == "failed":
                        self.logger.info(
                            f"Task NO.{int(no)}'s 【1D FLUORINE】test is not sure whether finished, please dobble check it"
                        )
                        break
                    self.logger.info(
                        f"Task NO.{int(no)} pre-NMR-test finished, please check the data in {state_proton[2]} and {state_fluorine[2]}"
                    )
                    completed_list.append(int(no))
                    proton_name = f"1D PROTON_No.{int(no)}"
                    fluorine_name = f"1D FLUORINE_No.{int(no)}"
                    dir_name = os.path.dirname(state_proton[2])
                    proton_dir = os.path.join(dir_name, proton_name)
                    fluorine_dir = os.path.join(dir_name, fluorine_name)
                    os.rename(state_proton[2], proton_dir)
                    os.rename(state_fluorine[2], fluorine_dir)

                    # row_index = self.pre_nmr_df.index[self.pre_nmr_df['NO'] == no]
                    # fluorine_lsit = ["A1", "A2", "A3", 'A4', "A5"]
                    # for a in fluorine_lsit:
                    #     a_val = self.pre_nmr_df.loc[row_index[0], a]
                    #     is_a_empty = pd.isna(a_val)
                    #     if not is_a_empty:
                    #         stat = self.spinsolve.start_protocol('1D FLUORINE','Scan','PowerScan')
                    #         break
                    break
                times += 1
                if times >= 15:
                    self.spinsolve.nmr_close_in()
                    self.logger.info(
                        f"Task NO.{int(no)}'s NMR test is not completed, please retry"
                    )
                    uncompleted_list.append(int(no))
                    break

            self.controller.movez(saft_height)

            x2, y2, z2 = self.slot_for_gripper_df.loc[
                self.slot_for_gripper_df["usage"] == "BEFORE", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", x2)
            self.controller.single_move_abs("y", y2)
            self.controller.single_move_abs("z", z2)
            # self.controller.move_xyz(x2,y2,z2)

            x3, y3, z3 = self.slot_for_gripper_df.loc[
                self.slot_for_gripper_df["usage"] == "GO", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", float(x3))
            x4, y4, z4 = self.slot_for_gripper_df.loc[
                self.slot_for_gripper_df["usage"] == "AFTER", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("z", float(z4))
            self.controller.single_move_abs("z", saft_height)
            try:
                res = self.rs485.send_msg(gripper_state)
                res = res.hex()[8:10]
                if res == "03":
                    self.logger.error("Dosing head is dropped down")
                    raise
                if res == "01":
                    self.rs485.send_msg(rgi_pos_0)
            except:
                sys.exit(-1)

            self.controller.single_move_abs("x", x)
            self.controller.single_move_abs("y", y)
            self.controller.single_move_abs("z", z_back)

            self.spinsolve.pump_out_with_stop(30)
            self.controller.movez(saft_height)

            # 03 40
            x_thf, y_thf, z_thf = self.clean_for_gripper_df.loc[
                self.clean_for_gripper_df["usage"] == "acetone", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", x_thf)
            self.controller.single_move_abs("y", y_thf)
            self.controller.single_move_abs("z", z_thf)

            # self.controller.move_xyz(x5,y5,z5)
            self.spinsolve.pump_in_without_stop(15)
            self.controller.movez(saft_height)

            # DMA 01 40
            x5, y5, z5 = self.clean_for_gripper_df.loc[
                self.clean_for_gripper_df["usage"] == "D1", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", x5)
            self.controller.single_move_abs("y", y5)
            self.controller.single_move_abs("z", z5)
            # self.controller.move_xyz(x6,y6,z6)
            self.spinsolve.pump_stop()
            self.spinsolve.pump_in_with_stop(38)
            sleep(4)
            self.spinsolve.pump_in_with_low_speed(15)
            self.controller.movez(saft_height)

        z_dosing_back = z_dosing
        self.controller.move_xyz(x_dosing, y_dosing, z_dosing_back)
        self.rs485.send_msg(rgi_pos_50)
        self.controller.movez(saft_height)
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)

        self.logger.info("Pre-NMR-test finished")

    def post_nmr_test(self):
        self.set_rgi(1)
        self.logger.info("Starting post-NMR-test")

        post_nmr_df = self.task_df.drop(columns=["NO"])
        solvent_df = post_nmr_df.loc[:, post_nmr_df.columns.str.contains("D")]
        solvent_cols = solvent_df.columns.tolist()
        solvent_name = solvent_cols[0]
        solvent_addr = self.clean_for_gripper_df.loc[
            self.clean_for_gripper_df["usage"] == solvent_name, "addr"
        ].values[0]
        solvent_addr = "0" + str(solvent_addr)[0]

        self.logger.info("Adding internal standard")
        # Start post NMR test
        self.nmr_prepare_df = self.nmr_prepare_df.head(
            self.nums_of_task
        )
        self.nmr_prepare_df = self.nmr_prepare_df.drop(columns=["NO"])  # "NO"
        # calculate the sum of each column
        not_null_column_sums_nmr = {}
        # store the index list of each column
        divided_not_null_columns_nmr = {}
        # the columns of solvent
        nmr_solvent_df = self.nmr_prepare_df.loc[
            :, self.nmr_prepare_df.columns.str.contains("D")
        ]
        # the columns of internal standard
        internal_standard_df = self.nmr_prepare_df.loc[
            :, ~self.nmr_prepare_df.columns.str.contains("D")
        ]

        # ####### , Iterate through all internal standard columns, add internal standard
        for column in internal_standard_df.columns:
            column_sum = internal_standard_df[column].sum()
            if column_sum == 0:
                continue

            not_null_column_sums_nmr[column] = column_sum

            divided_not_null_columns_nmr[column] = []
            index_list = []
            value_list = []
            sum_temp = 0
            # 2400
            for index, value in enumerate(internal_standard_df[column]):
                if pd.isnull(value):
                    continue
                value = math.ceil(value * step / volume)
                # If the value itself is greater than 2400, split it and store the same index multiple times
                if value > 2400:
                    index_list.append(index)
                    value_list.append(2400)
                    divided_not_null_columns_nmr[column].append(
                        (index_list, value_list, 2400)
                    )  # 1000
                    index_list = []
                    value_list = []

                    index_list.append(index)
                    value_list.append(value - 2400)
                    divided_not_null_columns_nmr[column].append(
                        (index_list, value_list, value - 2400)
                    )  # 1000
                    index_list = []
                    value_list = []
                else:
                    sum_temp += value
                    index_list.append(index)
                    value_list.append(value)
                    if (
                        sum_temp > 2400
                    ):  # 1000,
                        divided_not_null_columns_nmr[column].append(
                            (index_list[:-1], value_list[:-1], sum_temp - value)
                        )  # 1000
                        index_list = [index_list[-1]]
                        value_list = [value_list[-1]]
                        sum_temp = value

            if index_list:
                divided_not_null_columns_nmr[column].append(
                    (index_list, value_list, sum_temp)
                )

            x_fix, y_fix, z_fix = self.gripper_df.loc[
                self.gripper_df["usage"] == "fix", ["X", "Y", "Z"]
            ].values[0]
            x_open, y_open, z_open = self.gripper_df.loc[
                self.gripper_df["usage"] == "open", ["X", "Y", "Z"]
            ].values[0]
            x_close, y_close, z_close = self.gripper_df.loc[
                self.gripper_df["usage"] == "close", ["X", "Y", "Z"]
            ].values[0]

            x, y, z, h = self.reagent_df.loc[
                self.reagent_df["Chemicals"] == column, ["X", "Y", "Z", "H"]
            ].values[0]

            self.controller.single_move_abs("z", saft_height)
            self.rs485.motion.single_move("h", h)
            self.controller.move_xyz(x, y, z)
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.controller.single_move_abs("z", saft_height)
            self.rs485.motion.single_move("h", 0)

            self.controller.move_xyz(x_fix, y_fix, z_fix)
            self.rs485.send_msg(pge_close)
            sleep(0.5)

            self.controller.set_speed("z", open_cap_speed)
            self.rs485.send_msg(rotate_open)
            self.controller.single_move_abs("z", float(z_open))
            sleep(1)
            self.controller.set_speed("z", nomal_speed)
            self.controller.single_move_abs("z", saft_height_tip)
            x3, y3, z3 = self.tip_for_pump_df.loc[
                self.tip_for_pump_df["Presence"] == 1, ["X", "Y", "Z"]
            ].values[0]
            index = self.tip_for_pump_df.loc[
                self.tip_for_pump_df["Presence"] == 1
            ].index[0]
            self.tip_for_pump_df.loc[index, "Presence"] = 0
            self.tip_for_pump_df.to_excel(
                tip_for_pump_file_path,
                index=False,
            )
            self.controller.move_xyz(x3, y3, z3)

            self.controller.single_move_abs("z", saft_height_tip)
            x4, y4, z4 = self.gripper_df.loc[
                self.gripper_df["usage"] == "pipette", ["X", "Y", "Z"]
            ].values[0]
            rinse_flag = 1
            for divided_list, value_list, sum_of_value in divided_not_null_columns_nmr[
                column
            ]:
                self.controller.move_xyz(x4, y4, z4)

                if rinse_flag == 1:
                    self.rs485.send_instr("00", "4D", 2400, 1)
                    sleep(6)
                    self.rs485.send_instr("00", "42", 2400, 1)
                    sleep(6)
                self.rs485.send_instr("00", "4D", sum_of_value, 1)
                sleep(sum_of_value / 2400 * 6)
                self.controller.single_move_abs("z", saft_height_pipetting)

                for index, value in zip(divided_list, value_list):
                    no = index + 1
                    x_thf, y_thf, z_thf = self.reaction_for_pump_df.loc[
                        self.reaction_for_pump_df["NO"] == no, ["X", "Y", "Z"]
                    ].values[0]
                    self.controller.move_xyz(x_thf, y_thf, z_thf)
                    self.rs485.send_instr("00", "42", value, 1)
                    sleep(value / 2400 * 6)
                    self.controller.single_move_abs("z", saft_height_pipetting)

                rinse_flag = 0

            x7, y7, z7 = self.slot_for_pump_df.loc[
                self.slot_for_pump_df["usage"] == "BEFORE", ["X", "Y", "Z"]
            ].values[0]

            self.controller.single_move_abs("z", z7)

            self.controller.move_xyz(x7, y7, z7)
            x8, y8, z8 = self.slot_for_pump_df.loc[
                self.slot_for_pump_df["usage"] == "GO", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", float(x8))
            x9, y9, z9 = self.slot_for_pump_df.loc[
                self.slot_for_pump_df["usage"] == "AFTER", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("z", float(z9))
            self.controller.single_move_abs("z", saft_height)

            self.controller.move_xyz(x_close, y_close, z_open)
            self.controller.set_speed("z", open_cap_speed)
            self.rs485.send_msg(rotate_close)
            self.controller.single_move_abs("z", float(z_close))
            sleep(0.5)
            self.rs485.send_msg(pge_open)
            sleep(0.5)
            self.controller.set_speed("z", nomal_speed)
            self.controller.single_move_abs("z", saft_height)
            self.rs485.motion.single_move("h", h)
            z_back = float(z) - 50
            self.controller.move_xyz(x, y, z_back)
            self.rs485.send_msg(rgi_pos_50)
            self.controller.single_move_abs("z", saft_height)

        self.rs485.motion.single_move("h", 0)

        # Iterate through all solvent columns, add solvent
        self.controller.movez(saft_height)
        self.rs485.send_msg(rotate_90)
        for column in nmr_solvent_df.columns:
            index_list = []
            value_list = []
            for index, value in enumerate(nmr_solvent_df[column]):
                if pd.isnull(value):
                    continue
                value *= peristaltic_pump["steps_per_ul"]
                value = int(value)
                index_list.append(index)
                value_list.append(value)
            if len(index_list) == 0:
                continue
            x_solvent, y_solvent, z_solvent, addr_solvent = self.dosing_head_df.loc[
                self.dosing_head_df["usage"] == column, ["X", "Y", "Z", "addr"]
            ].values[0]
            addr_solvent = "0" + str(addr_solvent)[0]
            self.controller.move_xyz(x_solvent, y_solvent, z_solvent)
            self.rs485.send_msg(rgi_pos_0)
            sleep(0.5)
            self.controller.movez(saft_height_bottle)

            x_thf, y_thf, z_thf = self.clean_for_gripper_df.loc[
                self.clean_for_gripper_df["usage"] == column, ["X", "Y", "Z"]
            ].values[0]
            z_thf -= 50
            self.controller.single_move_abs("x", x_thf)
            self.controller.single_move_abs("y", y_thf)
            self.controller.single_move_abs("z", z_thf)
            self.rs485.send_instr(addr_solvent, "40", 300, 2)
            sleep(1)
            while True:
                _, res = self.rs485.send_instr(addr_solvent, "4A", 0, 2)
                if res.hex()[4:6] == "00":
                    break
                sleep(1)

            self.controller.movez(saft_height_bottle)

            for index, value in zip(index_list, value_list):
                no = index + 1
                x_thf, y_thf, z_thf = self.reaction_for_pump2_df.loc[
                    self.reaction_for_pump2_df["NO"] == no, ["X", "Y", "Z"]
                ].values[0]
                self.controller.move_xyz(x_thf, y_thf, z_thf)
                self.rs485.send_instr(addr_solvent, "40", value, 2)
                sleep(1)
                while True:
                    _, res = self.rs485.send_instr(addr_solvent, "4A", 0, 2)
                    if res.hex()[4:6] == "00":
                        break
                    sleep(1)
                self.controller.single_move_abs("z", saft_height_pipetting)

            self.controller.move_xyz(x_solvent, y_solvent, z_solvent - 5)
            self.rs485.send_msg(rgi_pos_50)
            sleep(0.5)
            self.controller.movez(saft_height_pipetting)

        self.controller.single_move_abs("z", saft_height)

        # ##
        self.rs485.send_msg(reset_rgi)
        sleep(3)
        self.rs485.send_msg(rgi_pos_50)
        sleep(1)
        self.rs485.send_msg(rotate_speed_12)
        sleep(3)
        self.rs485.send_msg(rotate_90)

        x_dosing, y_dosing, z_dosing = self.dosing_head_df.loc[
            self.dosing_head_df["usage"] == "NMR", ["X", "Y", "Z"]
        ].values[0]
        self.controller.single_move_abs("x", x_dosing)
        self.controller.single_move_abs("y", y_dosing)

        self.controller.single_move_abs("z", z_dosing)
        # self.controller.move_xyz(x,y,z)
        self.rs485.send_msg(rgi_pos_0)
        sleep(0.5)
        self.controller.movez(saft_height)

        clean_flag = True
        for index, row in self.reaction_for_dosing_df.iterrows():
            no = row["NO"]
            x = row["X"]
            y = row["Y"]
            z = row["ZAfter"]
            z_back = row["ZBack"]
            if int(no) > self.nums_of_task:
                break
            # 200ul
            x1, y1, z1 = self.tip_for_gripper_df.loc[
                self.tip_for_gripper_df["Presence"] == 1, ["X", "Y", "Z"]
            ].values[0]
            tip_index = self.tip_for_gripper_df.loc[
                self.tip_for_gripper_df["Presence"] == 1
            ].index[0]
            self.tip_for_gripper_df.loc[tip_index, "Presence"] = 0
            self.tip_for_gripper_df.to_excel(
                tip_for_gripper_file_path,
                index=False,
            )
            # self.controller.move_xyz(x1,y1,z1)
            self.controller.single_move_abs("x", x1)
            self.controller.single_move_abs("y", y1)
            self.controller.single_move_abs("z", z1)
            self.controller.movez(saft_height)


            self.controller.single_move_abs("x", x)
            self.controller.single_move_abs("y", y)
            self.controller.single_move_abs("z", z)
            # self.controller.move_xyz(x,y,z)

            if clean_flag:
                self.rs485.send_instr(solvent_addr, "40", 3400, 2)
                sleep(0.5)
                self.rs485.send_instr("03", "40", 3500, 2)
                clean_flag = False
            else:
                self.rs485.send_instr(solvent_addr, "40", 3000, 2)
                sleep(0.5)
                self.rs485.send_instr("03", "40", 3000, 2)

            self.spinsolve.nmr_pump_in()
            times = 0
            while True:
                flag = 0
                for i in range(5):
                    res = self.rs485.send_msg(check_water_12)
                    res = res.hex()
                    if res[6:8] == "01" or res[6:8] == "02" or res[6:8] == "03":
                        flag += 1
                    sleep(1.5)
                if flag >= 4:
                    self.spinsolve.nmr_close_in()
                    # self.spinsolve.back_to(6)
                    state_proton = "failed"
                    state_fluorine = "failed"
                    state_proton = self.spinsolve.start_protocol(
                        "1D PROTON", "Scan", "StandardScan"
                    )
                    if state_proton == "failed":
                        self.logger.info(
                            f"Task NO.{int(no)}'s 【1D PROTON】test is not sure whether finished, please dobble check it"
                        )
                        break
                    state_fluorine = self.spinsolve.start_protocol(
                        "1D FLUORINE", "Scan", "PowerScan"
                    )
                    if state_fluorine == "failed":
                        self.logger.info(
                            f"Task NO.{int(no)}'s 【1D FLUORINE】test is not sure whether finished, please dobble check it"
                        )
                        break
                    self.logger.info(
                        f"Task NO.{int(no)} post-NMR-test finished, please check the data in {state_proton[2]} and {state_fluorine[2]}"
                    )
                    # row_index = self.pre_nmr_df.index[self.pre_nmr_df['NO'] == no]
                    # fluorine_lsit = ["A1", "A2", "A3", 'A4', "A5"]
                    # for a in fluorine_lsit:
                    #     a_val = self.pre_nmr_df.loc[row_index[0], a]
                    #     is_a_empty = pd.isna(a_val)
                    #     if not is_a_empty:
                    #         stat = self.spinsolve.start_protocol('1D FLUORINE','Scan','PowerScan')
                    #         break
                    break
                times += 1
                if times >= 7:
                    self.spinsolve.nmr_close_in()
                    self.logger.info(
                        f"Task NO.{int(no)}'s NMR test is not completed, please retry"
                    )
                    break

            self.controller.movez(saft_height)

            x2, y2, z2 = self.slot_for_gripper_df.loc[
                self.slot_for_gripper_df["usage"] == "BEFORE", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", x2)
            self.controller.single_move_abs("y", y2)
            self.controller.single_move_abs("z", z2)
            # self.controller.move_xyz(x2,y2,z2)

            x3, y3, z3 = self.slot_for_gripper_df.loc[
                self.slot_for_gripper_df["usage"] == "GO", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", float(x3))
            x4, y4, z4 = self.slot_for_gripper_df.loc[
                self.slot_for_gripper_df["usage"] == "AFTER", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("z", float(z4))
            self.controller.single_move_abs("z", saft_height)
            try:
                res = self.rs485.send_msg(gripper_state)
                res = res.hex()[8:10]
                if res == "03":
                    self.logger.info("Dosing head is dropped down")
                    raise
                elif res == "02":
                    res = self.rs485.send_msg(rgi_pos_0)
            except:
                sys.exit(-1)

            self.controller.single_move_abs("x", x)
            self.controller.single_move_abs("y", y)
            self.controller.single_move_abs("z", z_back)

            self.spinsolve.pump_out_with_stop(30)
            self.controller.movez(saft_height)

            x5, y5, z5 = self.clean_for_gripper_df.loc[
                self.clean_for_gripper_df["usage"] == "acetone", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", x5)
            self.controller.single_move_abs("y", y5)
            self.controller.single_move_abs("z", z5)
            # self.controller.move_xyz(x5,y5,z5)
            self.spinsolve.pump_in_without_stop(15)
            self.controller.movez(saft_height)
            # DMA
            x_thf, y_thf, z_thf = self.clean_for_gripper_df.loc[
                self.clean_for_gripper_df["usage"] == solvent_name, ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("x", x_thf)
            self.controller.single_move_abs("y", y_thf)
            self.controller.single_move_abs("z", z_thf)
            # self.controller.move_xyz(x6,y6,z6)
            self.spinsolve.pump_stop()
            self.spinsolve.pump_in_with_stop(38)
            sleep(4)
            self.spinsolve.pump_in_with_low_speed(15)
            self.controller.movez(saft_height)

        z_dosing_back = z_dosing
        self.controller.move_xyz(x_dosing, y_dosing, z_dosing_back)
        self.rs485.send_msg(rgi_pos_50)
        self.controller.movez(saft_height)
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)

        self.logger.info("Post-NMR-test finished")

    def replace_reactants(self, reactant_dict: {str, str}):
        self.set_rgi()
        self.controller.movez(saft_height)

        x_fix, y_fix, z_fix = self.gripper_df.loc[
            self.gripper_df["usage"] == "fix", ["X", "Y", "Z"]
        ].values[0]
        for reactant_name, reactant_pos in reactant_dict.items():
            print(f"Replacing reagent {reactant_name} at position {reactant_pos}")
            x_reactant, y_reactant, z_reactant, h_reactant = self.reagent_df.loc[
                self.reagent_df["Chemicals"] == reactant_name, ["X", "Y", "Z", "H"]
            ].values[0]
            x_replace, y_replace, z_replace = self.reaction_for_gripper_df.loc[
                self.reaction_for_gripper_df["NO"] == reactant_pos, ["X", "Y", "Z"]
            ].values[0]
            print(f"Moving the corresponding rack to h={h_reactant}")
            self.rs485.motion.single_move("h", h_reactant)
            print(
                f"Moving to reagent {reactant_name}: X={x_reactant}, Y={y_reactant}, Z={z_reactant}"
            )
            self.controller.move_xyz(x_reactant, y_reactant, z_reactant)
            print("Closing the rotary gripper")
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            print("Moving to the safe height")
            self.controller.movez(saft_height)
            print(f"Moving to the fixed position: X={x_fix}, Y={y_fix}, Z={z_fix}")
            self.controller.move_xyz(x_fix, y_fix, z_fix)
            print("Closing the parallel gripper")
            self.rs485.send_msg(pge_close)
            sleep(1)
            print("Opening the rotary gripper")
            self.rs485.send_msg(rgi_pos_50)
            sleep(1)
            print("Moving to the safe height")
            self.controller.movez(saft_height)
            print(
                f"Moving to the replacement position: X={x_replace}, Y={y_replace}, Z={z_replace}"
            )
            self.controller.move_xyz(x_replace, y_replace, z_replace)
            print("Closing the rotary gripper")
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            print("Moving to the safe height")
            self.controller.movez(saft_height)
            print(
                f"Returning to reagent {reactant_name}: X={x_reactant}, Y={y_reactant}, Z={z_reactant}"
            )
            self.controller.move_xyz(x_reactant, y_reactant, z_reactant)
            print("Opening the rotary gripper")
            self.rs485.send_msg(rgi_pos_50)
            sleep(1)
            print("Moving to the safe height")
            self.controller.movez(saft_height)
            print(f"Moving to the fixed position: X={x_fix}, Y={y_fix}, Z={z_fix}")
            self.controller.move_xyz(x_fix, y_fix, z_fix)
            print("Closing the rotary gripper")
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            print("Opening the parallel gripper")
            self.rs485.send_msg(pge_open)
            sleep(1)
            print("Moving to the safe height")
            self.controller.movez(saft_height)
            print(
                f"Moving back to the replacement position: X={x_replace}, Y={y_replace}, Z={z_replace}"
            )
            self.controller.move_xyz(x_replace, y_replace, z_replace - 30)
            print("Opening the rotary gripper")
            self.rs485.send_msg(rgi_pos_50)
            sleep(1)
            print("Moving to the safe height")
            self.controller.movez(saft_height)

        print("Moving to the robot pickup safe position")
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)
        self.rs485.motion.single_move("h", 0)

    def handle_tip_rack(self, flag: int):
        """
        \n
        :param flag:\n
            1: \n
            2
        """
        self.controller.movez(saft_height)
        self.set_rgi()
        x_take_1, y_take_1, z_take_1 = self.gripper_df.loc[
            self.gripper_df["usage"] == "take_1", ["X", "Y", "Z"]
        ].values[0]
        x_take_2, y_take_2, z_take_2 = self.gripper_df.loc[
            self.gripper_df["usage"] == "take_2", ["X", "Y", "Z"]
        ].values[0]
        x_put_1, y_put_1, z_put_1 = self.gripper_df.loc[
            self.gripper_df["usage"] == "put_1", ["X", "Y", "Z"]
        ].values[0]
        x_put_2, y_put_2, z_put_2 = self.gripper_df.loc[
            self.gripper_df["usage"] == "put_2", ["X", "Y", "Z"]
        ].values[0]
        if flag == 1:
            self.pushrod(2)
            self.controller.move_xyz(x_take_1, y_take_1, z_take_1)
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.controller.movez(saft_height)
            self.controller.single_move_abs("x", x_put_1)
            self.controller.single_move_abs("y", y_put_1)
            self.controller.single_move_abs("z", z_put_1)
            self.rs485.send_msg(rgi_pos_50)
            sleep(1)
            self.controller.movez(saft_height)
        elif flag == 2:
            self.pushrod(2)
            self.controller.move_xyz(x_take_2, y_take_2, z_take_2)
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.controller.movez(saft_height)
            self.controller.single_move_abs("y", y_put_2)
            self.controller.single_move_abs("x", x_put_2)
            self.controller.single_move_abs("z", z_put_2)
            self.rs485.send_msg(rgi_pos_50)
            sleep(1)
            self.controller.movez(saft_height)
            self.pushrod(1)
            self.generate_tip_info()

        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)

    def generate_tip_info(self):
        self.tip_for_gripper_df["Presence"] = 1
        self.tip_for_pump_df["Presence"] = 1
        self.tip_for_pump_df.to_excel(tip_for_pump_file_path, index=False)
        self.tip_for_gripper_df.to_excel(tip_for_gripper_file_path, index=False)
        self.logger.info("Generate tip info successfully")


if __name__ == "__main__":
    # generate task dataframe for test
    task_df = [
        {"name": "test", "solvent": "DMA", "tip": "tip1", "volume": 10, "number": 1}
    ]
    liquid_station = LiquidStation(task_df=task_df)
    # reactant_dict = {"A1": 1, "A2": 2}
    # liquid_station.rs485.motion.single_move("h", 0)
    # liquid_station.replace_reactants(reactant_dict)
    # liquid_station.rs485.motion.initial_setup()
    # liquid_station.rs485.motion.datum()
    # liquid_station.rs485.motion.single_move('h', 600000)
    # liquid_station.rs485.motion.single_move('h', 960000)
    # liquid_station.controller.datum_xyz()
    # liquid_station.init_devices()
    # liquid_station.rs485.send_msg(relay_1_nc)
    # dict = {"A1": 1, "B1": 9, "C8": 25}
    # liquid_station.handle_tip_rack(1)
    # liquid_station.pushrod(2)
    # liquid_station.generate_tip_info()
    # liquid_station.pushrod(1)
    liquid_station.gas_control(1)
    # i = 0
    # while True:
    #     sleep(1)
    #     print(i)
    #     i += 1
    # liquid_station.replace_reactants(dict)
