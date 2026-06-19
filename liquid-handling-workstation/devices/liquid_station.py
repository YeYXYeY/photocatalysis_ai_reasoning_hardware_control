import math
import os
import sys
from time import sleep

import pandas as pd

from devices.controller import Controller
from devices.liquid_station_runtime import (
    build_liquid_station_paths,
    build_runtime_logger,
    load_coordinate_tables,
    load_runtime_config,
)
from devices.rs485 import RS485
from utils.calc import calculate_crc

# Rotation gripper parameters.
reset_rgi = calculate_crc(b"\x04\x06\x01\x00\x00\x01")
rgi_pos_0 = calculate_crc(b"\x04\x06\x01\x03\x00\x00")
rgi_pos_40 = calculate_crc(b"\x04\x06\x01\x03\x01\x90")
rgi_pos_50 = calculate_crc(b"\x04\x06\x01\x03\x03\x52")  # Tuned to 85%.
rgi_pos_100 = calculate_crc(b"\x04\x06\x01\x03\x03\xe8")
rotate_open = calculate_crc(b"\x04\x06\x01\x09\x04\x38")
rotate_close = calculate_crc(b"\x04\x06\x01\x09\xfb\xc7")
rotate_90 = calculate_crc(b"\x04\x06\x01\x09\x00\x5a")
rotate_speed_12 = calculate_crc(b"\x04\x06\x01\x07\x00\x08")  # Tuned to 9%.
gripper_state = calculate_crc(b"\x04\x03\x02\x01\x00\x01")
open_cap_speed = 15
inflate_speed = 200
nomal_speed = 1500
saft_height = 100
saft_height_tip = 100
saft_height_bottle = 100
saft_height_pipetting = 100

# Robot handoff position for the main module.
gripper_pos_x = 5600
gripper_pos_y = 100
gripper_pos_z = 100


# Syringe pump parameters.
step = 12000
volume = 5000
reset_pump = b"\xcc\x00\x45\x00\x00\xdd\xee\x01"
pump_speed = b"\xcc\x00\x4b\x64\x00\xdd\x58\x02"

# Parallel gripper parameters.
reset_pge = calculate_crc(b"\x05\x06\x01\x00\x00\x01")
pge_close = calculate_crc(b"\x05\x06\x01\x03\x00\x00")
pge_open = calculate_crc(b"\x05\x06\x01\x03\x03\xe8")

# Tubing liquid detection.
check_water_1 = b"\x11\x02\x00\x00\x00\x01\xbb\x5a"
check_water_2 = b"\x11\x02\x00\x01\x00\x01\xea\x9a"
check_water_12 = b"\x11\x02\x00\x00\x00\x02\xfb\x5b"

# Pushrod direction relays.
relay_1_nc = b"\x11\x05\x00\x10\xff\x00\x8f\x6f"
relay_1_no = b"\x11\x05\x00\x10\x00\x00\xce\x9f"
relay_2_nc = b"\x11\x05\x00\x11\xff\x00\xde\xaf"
relay_2_no = b"\x11\x05\x00\x11\x00\x00\x9f\x5f"


# Gas control solenoid.
relay_3_nc = calculate_crc(b"\x11\x05\x00\x12\xff\x00")
relay_3_no = calculate_crc(b"\x11\x05\x00\x12\x00\x00")

RUNTIME_PATHS = build_liquid_station_paths()
logger = build_runtime_logger(RUNTIME_PATHS)
logger.info("Starting liquid station runtime.")
config = load_runtime_config(RUNTIME_PATHS, logger=logger)
logger.info("Loaded liquid station configuration successfully.")
COORDINATE_TABLES = load_coordinate_tables(RUNTIME_PATHS)


class LiquidStation:
    def __init__(self, task_df):
        # Initialize the device wrappers used by the workstation.
        self.rs485 = RS485(modbus_prm=config["RS485"], logger=logger)
        self.controller = Controller(config["controller"], logger, self.rs485.ser)
        # Task data.
        self.task_df = task_df

        self.nmr_task_df = self.task_df.copy()
        self.gas_protect_df = self.task_df.copy()
        self.post_nmr_df = task_df
        self.pre_nmr_df = task_df
        self.nums_of_task = len(task_df)
        # The current deck cannot handle more than 28 tasks at once.
        if self.nums_of_task > 28:
            self.logger.info(
                "The task file contains %s entries, which exceeds the liquid station capacity of 28.",
                self.nums_of_task,
            )
            sys.exit(-1)
        # Coordinate tables.
        self.reagent_df = COORDINATE_TABLES["reagent_df"].copy()
        self.gripper_df = COORDINATE_TABLES["gripper_df"].copy()
        self.reaction_for_pump_df = COORDINATE_TABLES["reaction_for_pump_df"].copy()
        self.reaction_for_pump2_df = COORDINATE_TABLES[
            "reaction_for_pump2_df"
        ].copy()
        self.slot_for_pump_df = COORDINATE_TABLES["slot_for_pump_df"].copy()
        self.dosing_head_df = COORDINATE_TABLES["dosing_head_df"].copy()
        self.tip_for_gripper_df = COORDINATE_TABLES["tip_for_gripper_df"].copy()
        self.reaction_for_dosing_df = COORDINATE_TABLES[
            "reaction_for_dosing_df"
        ].copy()
        self.slot_for_gripper_df = COORDINATE_TABLES["slot_for_gripper_df"].copy()
        self.clean_for_gripper_df = COORDINATE_TABLES["clean_for_gripper_df"].copy()
        self.nmr_prepare_df = COORDINATE_TABLES["nmr_prepare_df"].copy()
        self.reaction_for_gripper_df = COORDINATE_TABLES[
            "reaction_for_gripper_df"
        ].copy()
        self.tip_for_pump_df = COORDINATE_TABLES["tip_for_pump_df"].copy()
        self.tip_for_pump_file_path = RUNTIME_PATHS.tip_for_pump_path
        self.tip_for_gripper_file_path = RUNTIME_PATHS.tip_for_gripper_path
        self.peristaltic_pump = config["peristaltic_pump"]
        self.logger = logger

    def init_devices(self):
        """Initialize the configured liquid workstation hardware."""
        # Initialize all configured devices.
        self.controller.datum_xyz()  # Home the XYZ axes.
        self.controller.set_motion_params()
        self.rs485.init_devices(reset_rgi, reset_pge, reset_pump, pump_speed)
        self.rs485.motion.initial_setup()
        self.rs485.motion.datum()
        self.rs485.send_msg(rgi_pos_50)
        sleep(1)
        self.rs485.send_msg(rotate_speed_12)
        sleep(1)
        sleep(1)
        self.logger.info("Liquid station initialization completed\n")

    def pushrod(self, flag: int = 0):
        """Control the tip-rack pushrod.

        Args:
            flag (int, optional):
                1 moves the pushrod in,
                2 moves the pushrod out,
                0 stops the pushrod.
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

    def open_cap(self):
        self.set_rgi()
        # Open each reaction bottle needed by the current task file.
        open_cap_count = 0
        for index, row in self.reaction_for_gripper_df.iterrows():
            if open_cap_count % 5 == 0:
                self.set_rgi()
            # Load the fixed gripper coordinates used during cap handling.
            x_fix, y_fix, z_fix = self.gripper_df.loc[
                self.gripper_df["usage"] == "fix", ["X", "Y", "Z"]
            ].values[0]
            x_open, y_open, z_open = self.gripper_df.loc[
                self.gripper_df["usage"] == "open", ["X", "Y", "Z"]
            ].values[0]
            x_close, y_close, z_close = self.gripper_df.loc[
                self.gripper_df["usage"] == "close", ["X", "Y", "Z"]
            ].values[0]

            # Load the bottle and cap placement coordinates.
            no = row["NO"]
            x = row["X"]
            y = row["Y"]
            z = row["Z"]
            cap = row["Cap"]
            xc = row["XC"]
            yc = row["YC"]
            zc = row["ZC"]
            empty = row["EMPTY"]

            # Only process the bottles referenced by the active task file.
            if open_cap_count >= self.nums_of_task:
                break
            # Move to the bottle and grip it with the rotation gripper.
            self.controller.move_xyz(x, y, z)
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.controller.movez(saft_height_bottle)

            # Move to the fixed gripper so the bottle can be stabilized.
            self.controller.move_xyz(x_fix, y_fix, z_fix)
            self.rs485.send_msg(pge_close)
            sleep(0.5)

            # Unscrew and lift the cap.
            self.controller.set_speed("z", open_cap_speed)
            self.rs485.send_msg(rotate_open)
            self.controller.single_move_abs("z", float(z_open))
            sleep(1)
            self.controller.set_speed("z", nomal_speed)
            self.controller.single_move_abs("z", saft_height_bottle)

            # Place the removed cap in its storage position.
            self.controller.move_xyz(xc, yc, zc)
            self.rs485.send_msg(rgi_pos_50)
            sleep(0.5)
            self.controller.single_move_abs("z", saft_height_bottle)

            # Re-grip the bottle after the cap has been parked.
            z_fix1 = float(z_fix) + 30
            self.controller.move_xyz(x_fix, y_fix, z_fix1)
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.rs485.send_msg(pge_open)
            sleep(1)
            self.controller.single_move_abs("z", saft_height_bottle)

            # Return the bottle to its reaction position.
            z_back = float(z) - 50
            self.controller.move_xyz(x, y, z_back)
            self.rs485.send_msg(rgi_pos_50)
            sleep(0.5)
            self.controller.single_move_abs("z", saft_height_bottle)
            open_cap_count += 1

            self.logger.info(f"Open the bottle cap of NO.{no} and finished")

        # Return to the global safe height.
        self.controller.single_move_abs("z", saft_height)
        # Reset the rotation gripper after the cap-opening loop.
        self.set_rgi()
        # Move back to the robot handoff position.
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)
        self.logger.info("Open all the bottle caps and finished")

    def set_rgi(self, flag=0):
        """Reset the rotation gripper and optionally turn it by 90 degrees."""
        self.rs485.send_msg(reset_rgi)
        sleep(3)
        self.rs485.send_msg(rgi_pos_50)
        sleep(1)
        self.rs485.send_msg(rotate_speed_12)
        sleep(1)
        if flag == 1:
            self.rs485.send_msg(rotate_90)
        self.logger.info("Reset the rotation gripper and finished")

    def gas_control(self, flag: int = 0):
        if flag == 1:
            self.rs485.send_msg(relay_3_nc)
        elif flag == 0:
            self.rs485.send_msg(relay_3_no)
        else:
            self.logger.error("Invalid flag value")
            sys.exit(-1)

    def gas_protection(self):
        # self.set_rgi()

        # Gas protection uses the fixed gripper and inflation coordinates.
        x_fix, y_fix, z_fix = self.gripper_df.loc[
            self.gripper_df["usage"] == "fix", ["X", "Y", "Z"]
        ].values[0]
        x_open, y_open, z_open = self.gripper_df.loc[
            self.gripper_df["usage"] == "open", ["X", "Y", "Z"]
        ].values[0]
        x_close, y_close, z_close = self.gripper_df.loc[
            self.gripper_df["usage"] == "close", ["X", "Y", "Z"]
        ].values[0]
        x_inflate_head, y_inflate_head, z_inflate_head = self.gripper_df.loc[
            self.gripper_df["usage"] == "inflate_head", ["X", "Y", "Z"]
        ].values[0]
        x_inflate_head, y_inflate_head, z_inflate_head = self.gripper_df.loc[
            self.gripper_df["usage"] == "inflate_head", ["X", "Y", "Z"]
        ].values[0]
        x_inflate, y_inflate, z_inflate = self.gripper_df.loc[
            self.gripper_df["usage"] == "inflate", ["X", "Y", "Z"]
        ].values[0]

        self.logger.info("Start gas protection")
        gas_protect_count = 0

        # Move to the global safe height before starting the gas-protection loop.
        self.controller.single_move_abs("z", saft_height)
        for index, row in self.gas_protect_df.iterrows():
            # Look up the reaction vessel coordinates for the current task item.
            no = row["NO"]
            x, y, z = self.reaction_for_gripper_df.loc[
                self.reaction_for_gripper_df["NO"] == no, ["X", "Y", "Z"]
            ].values[0]

            # Only process the bottles referenced by the active task file.
            if gas_protect_count >= self.nums_of_task:
                break

            self.rs485.send_msg(pge_close)
            # Move above the inflation point, then descend at a reduced speed.
            self.controller.move_xyz(x_inflate, y_inflate, z_inflate - 500)
            self.controller.set_speed("z", inflate_speed)
            self.controller.single_move_abs("z", z_inflate)

            # Open the gas valve for the configured protection window.
            self.gas_control(1)
            sleep(60)
            self.gas_control(0)
            self.controller.single_move_abs("z", z_inflate - 500)

            self.controller.set_speed("z", nomal_speed)
            # Return to the global safe height before the next vessel.
            self.controller.single_move_abs("z", saft_height)

            self.rs485.send_msg(pge_open)

            gas_protect_count += 1
            self.logger.info(f"Gas protection of NO.{no} completed")

        self.logger.info(f"Gas protection all completed")
        # Finish in the global safe position.
        self.controller.single_move_abs("z", saft_height)

    def prepare_solution(self):
        task_df = self.task_df.drop(columns=["NO"])
        # Split the task file into reactant and solvent columns.
        not_null_column_sums = {}
        divided_not_null_columns = {}
        solvent_df = task_df.loc[:, task_df.columns.str.contains("D")]
        reactant_df = task_df.loc[:, ~task_df.columns.str.contains("D")]

        self.logger.info("Start reactant adding")
        open_cap_count = 1
        for column in reactant_df.columns:
            if open_cap_count % 5 == 0:
                self.set_rgi()
            column_sum = reactant_df[column].sum()
            if column_sum == 0:
                continue
            self.logger.info(f"Statrting adding reactant {column}")

            not_null_column_sums[column] = column_sum

            divided_not_null_columns[column] = []
            index_list = []
            value_list = []
            sum_temp = 0
            # Group dispenses so each pump cycle stays within the 2400-step limit.
            for index, value in enumerate(reactant_df[column]):
                if pd.isnull(value):
                    continue
                value = math.ceil(value * step / volume)
                # If the value itself is greater than 2400, split it and store the same index multiple times
                if value > 2400:
                    divided_not_null_columns[column].append(
                        (index_list, value_list, sum_temp)
                    )  # Flush the current group before splitting a large request.
                    index_list = []
                    value_list = []
                    sum_temp = 0
                    index_list.append(index)
                    value_list.append(2400)
                    divided_not_null_columns[column].append(
                        (index_list, value_list, 2400)
                    )  # Record the first full-capacity chunk.
                    index_list = []
                    value_list = []

                    index_list.append(index)
                    value_list.append(value - 2400)
                    divided_not_null_columns[column].append(
                        (index_list, value_list, value - 2400)
                    )  # Record the remaining chunk for the same bottle.
                    index_list = []
                    value_list = []
                else:
                    sum_temp += value
                    index_list.append(index)
                    value_list.append(value)
                    if (
                        sum_temp > 2400
                    ):  # Flush the current group once it exceeds the limit.
                        divided_not_null_columns[column].append(
                            (index_list[:-1], value_list[:-1], sum_temp - value)
                        )  # Exclude the item that caused the overflow.
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
            self.tip_for_pump_df.to_excel(self.tip_for_pump_file_path, index=False)
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

                for index, value in zip(divided_list, value_list):
                    no = index + 1
                    x_thf, y_thf, z_thf = self.reaction_for_pump_df.loc[
                        self.reaction_for_pump_df["NO"] == no, ["X", "Y", "Z"]
                    ].values[0]
                    self.controller.move_xyz(x_thf, y_thf, z_thf)
                    self.rs485.send_instr("00", "42", value, 1)
                    sleep(value / 2400 * 6)
                    self.controller.single_move_abs("z", saft_height)

                rinse_flag = 0

            self.collect_tip(1)

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

        self.controller.movez(saft_height)
        self.rs485.send_msg(reset_rgi)
        sleep(3)
        self.rs485.send_msg(rgi_pos_50)
        sleep(1)
        self.rs485.send_msg(rotate_speed_12)
        sleep(3)
        self.rs485.send_msg(rotate_90)
        self.logger.info("Start adding solvent")
        for column in solvent_df.columns:
            index_list = []
            value_list = []
            for index, value in enumerate(solvent_df[column]):
                if pd.isnull(value):
                    continue
                value *= self.peristaltic_pump["steps_per_ul"]
                value = int(value)
                index_list.append(index)
                value_list.append(value)
            if len(index_list) == 0:
                continue
            self.logger.info(f"Start adding solvent {column}")
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
                    # self.logger.info("complete")
                    break
                sleep(1)

            self.controller.movez(saft_height_bottle)
            self.logger.info(index_list, value_list)
            for index, value in zip(index_list, value_list):
                no = index + 1
                x_thf, y_thf, z_thf = self.reaction_for_pump2_df.loc[
                    self.reaction_for_pump2_df["NO"] == no, ["X", "Y", "Z"]
                ].values[0]
                self.controller.move_xyz(x_thf, y_thf, z_thf)
                self.rs485.send_instr(
                    addr_solvent, "40", value, 2
                )  # Updated solvent address mapping.
                sleep(1)
                while True:
                    _, res = self.rs485.send_instr(
                        addr_solvent, "4A", 0, 2
                    )  # Updated solvent address mapping.
                    if res.hex()[4:6] == "00":
                        # self.logger.info("complete")
                        break
                    sleep(1)
                self.controller.single_move_abs("z", saft_height_pipetting)

            self.controller.single_move_abs("z", 50)
            self.controller.move_xyz(x_solvent, y_solvent, z_solvent - 5)
            self.rs485.send_msg(rgi_pos_50)
            sleep(0.5)
            self.controller.movez(saft_height_pipetting)

            self.logger.info(f"Solvent {column} addition completed")

        self.logger.info(f"Solvent addition all completed")
        self.controller.single_move_abs("z", saft_height)
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)

    def close_cap(self):
        self.set_rgi()

        # Close the reaction bottle caps for the active task set.
        open_cap_cout = 1
        for index, row in self.reaction_for_gripper_df.iterrows():
            if open_cap_cout % 5 == 0:
                self.set_rgi()
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

            if open_cap_cout > self.nums_of_task:
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
        solvent_df = pre_nmr_df.loc[:, pre_nmr_df.columns.str.contains("D")]
        solvent_cols = solvent_df.columns.tolist()
        solvent_name = solvent_cols[0]
        solvent_addr = self.clean_for_gripper_df.loc[
            self.clean_for_gripper_df["usage"] == solvent_name, "addr"
        ].values[0]
        solvent_addr = "0" + str(solvent_addr)[0]
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
        nmr_test_count = 0
        for index, row in self.nmr_task_df.iterrows():
            no = row["NO"]
            x, y, z, z_back = self.reaction_for_dosing_df.loc[
                self.reaction_for_dosing_df["NO"] == no, ["X", "Y", "Z", "ZBack"]
            ].values[0]
            if nmr_test_count >= self.nums_of_task:
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
                self.tip_for_gripper_file_path, index=False
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
                for i in range(8):
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
                    # rename the NMR data file
                    proton_file_name = f"1D PROTON_No.{int(no)}_pre"
                    fluorine_file_name = f"1D FLUORINE_No.{int(no)}_pre"

                    dir_name = os.path.dirname(state_proton[2])
                    proton_dir = os.path.join(dir_name, proton_file_name)
                    fluorine_dir = os.path.join(dir_name, fluorine_file_name)
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
                if times >= 8:
                    self.spinsolve.nmr_close_in()
                    self.logger.info(
                        f"Task NO.{int(no)}'s NMR test is not completed, please retry"
                    )
                    break

            self.controller.movez(saft_height)

            self.collect_tip(2)
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
                self.clean_for_gripper_df["usage"] == solvent_name, ["X", "Y", "Z"]
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
            nmr_test_count += 1

        z_dosing_back = z_dosing
        self.controller.move_xyz(x_dosing, y_dosing, z_dosing_back)
        self.rs485.send_msg(rgi_pos_50)
        self.controller.movez(saft_height)
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)

        self.logger.info("Pre-NMR-test finished")

    def collect_tip(self, flag):
        if flag == 1:
            x7, y7, z7 = self.slot_for_pump_df.loc[
                self.slot_for_pump_df["usage"] == "BEFORE", ["X", "Y", "Z"]
            ].values[0]
            self.controller.move_xyz(x7, y7, z7)
            x8, y8, z8 = self.slot_for_pump_df.loc[
                self.slot_for_pump_df["usage"] == "GO", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs_nocheck("x", float(x8))
            x9, y9, z9 = self.slot_for_pump_df.loc[
                self.slot_for_pump_df["usage"] == "AFTER", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs("z", float(z9))
            self.controller.single_move_abs("z", saft_height)
        elif flag == 2:
            x2, y2, z2 = self.slot_for_gripper_df.loc[
                self.slot_for_gripper_df["usage"] == "BEFORE", ["X", "Y", "Z"]
            ].values[0]
            self.controller.move_xyz(x2, y2, z2)
            # self.controller.move_xyz(x2,y2,z2)

            x3, y3, z3 = self.slot_for_gripper_df.loc[
                self.slot_for_gripper_df["usage"] == "GO", ["X", "Y", "Z"]
            ].values[0]
            self.controller.single_move_abs_nocheck("x", float(x3))
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
        else:
            self.logger.error("Wrong flag")
            sys.exit(-1)

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
        self.nmr_prepare_df = self.nmr_prepare_df.drop(
            columns=["NO"]
        )  # Drop the numbering column.
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

        # Add each internal-standard column in sequence.
        for column in internal_standard_df.columns:
            column_sum = internal_standard_df[column].sum()
            if column_sum == 0:
                continue

            not_null_column_sums_nmr[column] = column_sum

            divided_not_null_columns_nmr[column] = []
            index_list = []
            value_list = []
            sum_temp = 0
            # Group dispenses so each pump cycle stays within the 2400-step limit.
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
                    )  # Record the first full-capacity chunk.
                    index_list = []
                    value_list = []

                    index_list.append(index)
                    value_list.append(value - 2400)
                    divided_not_null_columns_nmr[column].append(
                        (index_list, value_list, value - 2400)
                    )  # Record the remaining chunk for the same bottle.
                    index_list = []
                    value_list = []
                else:
                    sum_temp += value
                    index_list.append(index)
                    value_list.append(value)
                    if (
                        sum_temp > 2400
                    ):  # Flush the current group once it exceeds the limit.
                        divided_not_null_columns_nmr[column].append(
                            (index_list[:-1], value_list[:-1], sum_temp - value)
                        )  # Exclude the item that caused the overflow.
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
            self.tip_for_pump_df.to_excel(self.tip_for_pump_file_path, index=False)
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

            self.collect_tip(1)

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
                value *= self.peristaltic_pump["steps_per_ul"]
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

        # Reset the rotation gripper before the post-NMR sampling pass.
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
        nmr_test_count = 0
        for index, row in self.nmr_task_df.iterrows():
            no = row["NO"]
            # self.reaction_for_dosing_dfNOnoX,Y,Z,ZBack
            x, y, z, z_back = self.reaction_for_dosing_df.loc[
                self.reaction_for_dosing_df["NO"] == no, ["X", "Y", "Z", "ZBack"]
            ].values[0]
            if nmr_test_count > self.nums_of_task:
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
                self.tip_for_gripper_file_path, index=False
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
                for i in range(8):
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
                    # rename the NMR data file
                    proton_file_name = f"1D PROTON_No.{int(no)}_post"
                    fluorine_file_name = f"1D FLUORINE_No.{int(no)}_post"

                    dir_name = os.path.dirname(state_proton[2])
                    proton_dir = os.path.join(dir_name, proton_file_name)
                    fluorine_dir = os.path.join(dir_name, fluorine_file_name)
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
                if times >= 8:
                    self.spinsolve.nmr_close_in()
                    self.logger.info(
                        f"Task NO.{int(no)}'s NMR test is not completed, please retry"
                    )
                    break

            self.controller.movez(saft_height)

            self.collect_tip(2)

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
            # Solvent rinse.
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
            nmr_test_count += 1

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
            self.logger.info(
                "Replacing reagent %s at reaction position %s.",
                reactant_name,
                reactant_pos,
            )
            x_reactant, y_reactant, z_reactant, h_reactant = self.reagent_df.loc[
                self.reagent_df["Chemicals"] == reactant_name, ["X", "Y", "Z", "H"]
            ].values[0]
            x_replace, y_replace, z_replace = self.reaction_for_gripper_df.loc[
                self.reaction_for_gripper_df["NO"] == reactant_pos, ["X", "Y", "Z"]
            ].values[0]
            self.logger.info("Moving the reagent rack to h=%s.", h_reactant)
            self.rs485.motion.single_move("h", h_reactant)
            self.logger.info(
                "Moving to reagent %s at X=%s, Y=%s, Z=%s.",
                reactant_name,
                x_reactant,
                y_reactant,
                z_reactant,
            )
            self.controller.move_xyz(x_reactant, y_reactant, z_reactant)
            self.logger.info("Closing the rotation gripper on the reagent bottle.")
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.logger.info("Returning to the safe height.")
            self.controller.movez(saft_height)
            self.logger.info(
                "Moving to the bottle-fix position at X=%s, Y=%s, Z=%s.",
                x_fix,
                y_fix,
                z_fix,
            )
            self.controller.move_xyz(x_fix, y_fix, z_fix)
            self.logger.info("Closing the parallel gripper to stabilize the bottle.")
            self.rs485.send_msg(pge_close)
            sleep(1)
            self.logger.info("Opening the rotation gripper to release the bottle.")
            self.rs485.send_msg(rgi_pos_50)
            sleep(1)
            self.logger.info("Returning to the safe height.")
            self.controller.movez(saft_height)
            self.logger.info(
                "Moving to the replacement slot at X=%s, Y=%s, Z=%s.",
                x_replace,
                y_replace,
                z_replace,
            )
            self.controller.move_xyz(x_replace, y_replace, z_replace)
            self.logger.info("Closing the rotation gripper on the replacement bottle.")
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.logger.info("Returning to the safe height.")
            self.controller.movez(saft_height)
            self.logger.info(
                "Returning the original reagent %s to X=%s, Y=%s, Z=%s.",
                reactant_name,
                x_reactant,
                y_reactant,
                z_reactant,
            )
            self.controller.move_xyz(x_reactant, y_reactant, z_reactant)
            self.logger.info("Opening the rotation gripper.")
            self.rs485.send_msg(rgi_pos_50)
            sleep(1)
            self.logger.info("Returning to the safe height.")
            self.controller.movez(saft_height)
            self.logger.info(
                "Moving back to the bottle-fix position at X=%s, Y=%s, Z=%s.",
                x_fix,
                y_fix,
                z_fix,
            )
            self.controller.move_xyz(x_fix, y_fix, z_fix)
            self.logger.info("Closing the rotation gripper.")
            self.rs485.send_msg(rgi_pos_0)
            sleep(1)
            self.logger.info("Opening the parallel gripper.")
            self.rs485.send_msg(pge_open)
            sleep(1)
            self.logger.info("Returning to the safe height.")
            self.controller.movez(saft_height)
            self.logger.info(
                "Moving back to the replacement slot at X=%s, Y=%s, Z=%s.",
                x_replace,
                y_replace,
                z_replace,
            )
            self.controller.move_xyz(x_replace, y_replace, z_replace - 30)
            self.logger.info("Opening the rotation gripper.")
            self.rs485.send_msg(rgi_pos_50)
            sleep(1)
            self.logger.info("Returning to the safe height.")
            self.controller.movez(saft_height)

        self.logger.info("Moving back to the robot handoff position.")
        self.controller.move_xyz(gripper_pos_x, gripper_pos_y, gripper_pos_z)
        self.rs485.motion.single_move("h", 0)

    def handle_tip_rack(self, flag: int):
        """Move the tip rack in or out of the manual replacement position."""
        self.controller.movez(saft_height)
        self.set_rgi()
        # Load the grab and placement coordinates for the tip rack.
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
        self.tip_for_pump_df.to_excel(self.tip_for_pump_file_path, index=False)
        self.tip_for_gripper_df.to_excel(self.tip_for_gripper_file_path, index=False)
        self.logger.info("Regenerated tip inventory files successfully.")


if __name__ == "__main__":
    # generate task dataframe for test
    task_df = [
        {"name": "test", "solvent": "DMA", "tip": "tip1", "volume": 10, "number": 1}
    ]
    liquid_station = LiquidStation(task_df=task_df)
    # liquid_station.controller.get_axis_status()
    # liquid_station.controller.datum_xyz()
    # liquid_station.controller.move_xyz(500, gripper_pos_y, gripper_pos_z)
    # reactant_dict = {"A1": 1, "A2": 2}
    # liquid_station.rs485.motion.single_move("h", 0)
    # liquid_station.replace_reactants(reactant_dict)
    # liquid_station.rs485.motion.initial_setup()
    # liquid_station.rs485.motion.datum()
    # liquid_station.rs485.motion.single_move('h', 600000)
    # liquid_station.rs485.motion.single_move("h", 0)
    # liquid_station.controller.datum_xyz()
    # liquid_station.init_devices()
    # liquid_station.rs485.send_msg(relay_1_nc)
    # dict = {"A1": 1, "B1": 9, "C8": 25}
    # liquid_station.handle_tip_rack(1)
    # liquid_station.pushrod(2)
    # liquid_station.generate_tip_info()
    liquid_station.pushrod(1)
    # liquid_station.gas_control(0)
    # liquid_station.gas_control(1)
    # liquid_station.rs485.send_msg(reset_pump)
    # liquid_station.controller.set_motion_params()

    # liquid_station.rs485.send_instr("08", "40", 3000, 2)
    # sleep(0.5)
    # liquid_station.rs485.send_instr("03", "40", 3000, 2)
    # liquid_station.replace_reactants(dict)
