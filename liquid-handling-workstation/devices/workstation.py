import os
import pandas as pd
from devices.controller import *
from devices.pump import *
from devices.cr10 import *
from devices.trans200 import *
from devices.relay4 import *
from devices.weighing import *
from devices.spinsolve import *
from utils.calc import *
from utils.split_liquid_task import *
import yaml
from time import sleep, time
from datetime import datetime


class Workstation:
    def __init__(self, task_dict: dict) -> None:
        self.task_dict = task_dict
        self.task_file = task_dict["task_file"]
        self.task_path = task_dict["task_path"]
        self.station_volumn = task_dict["station_volumn"]
        self.safe_height = task_dict["safe_height"]
        self.controller_prm = task_dict["controller"]
        self.reaction = task_dict["reaction"]
        self.reagent = task_dict["reagent"]
        self.slot = task_dict["slot"]
        self.gripper = task_dict["gripper"]
        self.tip = task_dict["tip"]

        self.task_list = split_task(
            task_dict["task_file"], task_dict["task_path"], task_dict["station_volumn"]
        )

    def open_reaction(self):
        """






        """
        pass

    def close_reaction(self):
        """






        """
        pass

    def all_in_on(self, non_null_rows, sum_of_column):
        """




        """
        pass

    def one_by_one(self, non_null_rows):
        """




        """
        pass

    def open_cap(self, x, y, z):
        """







        """
        pass

    def close_cap(self, x, y, z):
        """







        """
        pass

    def install_pump_tip(self):
        """






        """
        controller = Controller(self.controller_prm)
        controller.set_motion_params()
        controller.single_move_abs("z", self.task_dict["safe_height"])
        tip_df = pd.read_excel(self.task_dict["tip"])
        x, y, z = tip_df.loc[tip_df["Presence"] == 1, ["X", "Y", "Z"]].iloc[0]
        index = tip_df.loc[tip_df["Presence"] == 1].index[0]
        tip_df.loc[index, "Presence"] = 0
        tip_df.to_excel(self.task_dict["tip"], index=False)
        print(x, y, z)

        controller.single_move_abs("x", x)
        controller.single_move_abs("y", y)
        controller.single_move_abs("z", z)
        controller.single_move_abs(self.task_dict["safe_height"])

        pass

    def uninstall_pump_tip(self):
        """





        """

        # controller = Controller(self.controller)
        # controller.set_motion_params()
        # controller.single_move_abs('z',self.task_dict['safe_height'])

        # controller.single_move_abs('x', float(x))
        # controller.single_move_abs('y', float(y))
        # controller.single_move_abs('z', float(z))
        # print(f' :X7: {x}, Y7: {y}, Z7: {z}')
        # x8, y8, z8 = slot_df.loc[slot_df['usage']
        #                     == 'GO', ['X', 'Y', 'Z']].values[0]
        # controller.single_move_abs('x', float(x8))
        # print(f' :X8: {x8}, Y8: {y8}, Z8: {z8}, {index+1} ')
        # x9, y9, z9 = slot_df.loc[slot_df['usage']
        #                     == 'AFTER', ['X', 'Y', 'Z']].values[0]
        # controller.single_move_abs('z', float(z9))
        # controller.single_move_abs(self.task_dict['safe_height'])

        pass

    def start_work(self):
        for subtask in self.task_list:
            subtask_df = pd.read_excel(subtask)
            reagent_df = pd.read_excel(self.reagent)
            print(subtask_df)

            for column in subtask_df.columns[1:]:
                x, y, z = reagent_df.loc[
                    reagent_df["Chemicals"] == column, ["X", "Y", "Z"]
                ].values[0]
                self.open_cap(x, y, z)
                non_null_rows = subtask_df[column].dropna().index.tolist()
                print(non_null_rows)
                if not non_null_rows:
                    continue
                print("do something")
                sum_of_column = subtask_df.loc[non_null_rows, column].sum()
                if sum_of_column > 0:
                    if sum_of_column < 1000.0:
                        self.all_in_on(non_null_rows, sum_of_column)

                        self.install_pump_tip()
                    else:
                        self.one_by_one(non_null_rows)
                        self.install_pump_tip()

                self.close_cap(x, y, z)
