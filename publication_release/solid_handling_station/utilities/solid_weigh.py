import sys
from devices.motion import Motion
from devices.weighing import Weighing
from time import sleep
from tqdm import tqdm
from threading import Thread, Event

from app.runtime import load_station_runtime


class SolidWeigh:
    def __init__(self, runtime=None):
        runtime = runtime or load_station_runtime()
        weighing_param = runtime.config["solid_weighing"]
        # Set up logging information
        self.logger = runtime.logger
        self.logger.info("Solid Weighing Started")

        # Axis related parameters
        self.z1_safe_pos = weighing_param.get("z1_safe_pos")
        self.z2_safe_pos = weighing_param.get("z2_safe_pos")
        self.y_safe_pos = weighing_param.get("y_safe_pos")
        self.init_pos = weighing_param.get("init_pos")
        self.align_pos = weighing_param.get("align_pos")
        self.action_pos = weighing_param.get("action_pos")
        self.r_pos = weighing_param.get("r_pos")
        self.zero_pos = weighing_param.get("zero_pos")
        self.chemical_data_path = str(runtime.chemical_data_dir)
        self.coordinates_path = str(runtime.coordinates_dir)
        self.database_df = runtime.tables["database_df"]
        self.balance_coordinates_df = runtime.tables["balance_coordinates_df"]
        self.head_coordinates_df = runtime.tables["head_coordinates_df"]
        self.reaction_coordinates_df = runtime.tables["reaction_coordinates_df"]

        # Initialize device instance
        self.motion = Motion(self.logger)
        try:
            self.weighing = Weighing(self.logger)
        except Exception:
            self.motion.ser.close()
            raise

        # Create stop event
        self.stop_event = Event()

    def init_device(self) -> int:
        """Initialize the gripper and axes, home the stage, and tare the balance."""
        self.motion.init_pge()
        self.motion.initial_setup()
        self.motion.datum()
        self.weighing.tare()
        self.logger.info("Device initialized")
        return 0

    def get_pos_dict(self, chemical):

        pos_dict = (
            self.head_coordinates_df.loc[
                self.head_coordinates_df["Chemical"] == chemical,
                ["init_pos", "align_pos", "action_pos"],
            ]
            .iloc[0]
            .to_dict()
        )
        return pos_dict

    def handle_weighing_head(self, chemical: str, flag: int) -> dict:
        """Pick up (flag=1) or return (flag=2) the head for a chemical.

        Return the initial, alignment, and dispensing positions from the head table."""

        if chemical not in self.head_coordinates_df["Chemical"].values:
            self.logger.error(f"Chemical {chemical} not found in head_coordinates_df")
            sys.exit(1)

        head_num = self.head_coordinates_df.loc[self.head_coordinates_df["Chemical"] == chemical][
            "NO"
        ].values[0]

        if head_num not in range(1, 22):
            raise ValueError("Invalid head number")
        elif head_num in range(1, 8):
            pass
        elif head_num in range(8, 15):
            pass
        elif head_num in range(15, 22):
            pass
        # coordinates_dict
        coordinates_dict = (
            self.head_coordinates_df.loc[
                self.head_coordinates_df["Chemical"] == chemical,
                ["X", "Y", "Z1", "Z1Up", "Y1", "Y1Ready"],
            ]
            .iloc[0]
            .to_dict()
        )

        pos_dict = (
            self.head_coordinates_df.loc[
                self.head_coordinates_df["Chemical"] == chemical,
                ["init_pos", "align_pos", "action_pos"],
            ]
            .iloc[0]
            .to_dict()
        )

        movement_orders = {
            1: ["x", "z1", "y", "y1", "z1", "y1"],
            2: ["x", "y", "z1", "y1"],
        }
        if flag == 1:
            self.motion.single_move("y1", coordinates_dict["Y1Ready"])
            self.motion.single_move("x", coordinates_dict["X"])
            self.motion.single_move("y", coordinates_dict["Y"])
            self.motion.single_move("z1", coordinates_dict["Z1"])
            self.motion.single_move("y1", coordinates_dict["Y1"])
            self.motion.single_move("z1", coordinates_dict["Z1Up"])
            self.motion.single_move("y1", coordinates_dict["Y1Ready"])

        elif flag == 2:
            self.motion.single_move("y", self.y_safe_pos)
            self.motion.single_move("y1", coordinates_dict["Y1Ready"])
            self.motion.single_move("x", coordinates_dict["X"])
            self.motion.single_move("z1", coordinates_dict["Z1Up"])
            self.motion.single_move("y", coordinates_dict["Y"])
            self.motion.single_move("y1", coordinates_dict["Y1"])
            self.motion.single_move("z1", coordinates_dict["Z1"])
            self.motion.single_move("y1", coordinates_dict["Y1Ready"])

        self.motion.single_move("y", self.y_safe_pos)
        self.motion.single_move("z1", self.z1_safe_pos)
        return pos_dict

    def align_weighing_head(self, init_pos: int, align_pos: int):
        """Align the weighing head with the ZR actuator."""
        align_coordinates_dict = (
            self.balance_coordinates_df.loc[
                self.balance_coordinates_df["usage"] == "align", ["X", "Y", "Z1"]
            ]
            .iloc[0]
            .to_dict()
        )
        self.motion.single_move("x", align_coordinates_dict["X"])
        self.motion.single_move("y", align_coordinates_dict["Y"])
        self.motion.single_move("z1", align_coordinates_dict["Z1"])
        self.motion.end_alignment(init_pos, align_pos)
        self.motion.single_move("z1", self.z1_safe_pos)
        self.motion.single_move("y", self.y_safe_pos)

    def move_to_xyz(self, coordinates: dict, flag: int):
        """Move axes in the sequence selected by flag.

        1: x,y,z1; 2: z1,x,y; 3: x,y,z2; 4: z2,x,y; 5: z1,z2,x,y."""
        movement_orders = {
            1: ["x", "y", "z1"],
            2: ["z1", "x", "y"],
            3: ["x", "y", "z2"],
            4: ["z2", "x", "y"],
            5: ["z1", "z2", "x", "y"],
        }

        movement_order = movement_orders.get(flag)
        if not movement_order:
            raise ValueError(f"Invalid flag: {flag}")

        for axis in movement_order:
            axis_key = axis.upper()
            if axis_key not in coordinates:
                raise ValueError(f"Missing coordinate for axis: {axis}")
            self.motion.single_move(axis, coordinates[axis_key])

    def handle_sample_bottle(self, bottle_num: int, flag: int):
        """Transfer a bottle to the balance (flag=1) or return it to the rack (flag=2)."""

        if bottle_num is None or bottle_num not in self.reaction_coordinates_df["NO"].values:
            self.logger.error(f"Bottle {bottle_num} is not in the rack")
            sys.exit(1)
        movement_order = ["x", "y", "z2"]

        bottle_coordinates_dict = (
            self.reaction_coordinates_df.loc[
                self.reaction_coordinates_df["NO"] == bottle_num,
                ["X", "Y", "Z2", "ZBack"],
            ]
            .iloc[0]
            .to_dict()
        )

        placing_coordinates_dict = (
            self.balance_coordinates_df.loc[
                self.balance_coordinates_df["usage"] == "place", ["X", "Y", "Z2"]
            ]
            .iloc[0]
            .to_dict()
        )

        if flag == 1:
            self.motion.single_move("x", bottle_coordinates_dict["X"])
            self.motion.single_move("y", bottle_coordinates_dict["Y"])
            self.motion.single_move("z2", bottle_coordinates_dict["Z2"])
            self.motion.close_pge()
            self.motion.single_move("z2", self.z2_safe_pos)
            self.motion.single_move("x", placing_coordinates_dict["X"])
            self.motion.single_move("y", placing_coordinates_dict["Y"])
            self.motion.single_move("z2", placing_coordinates_dict["Z2"] - 500)
            self.motion.open_pge()
            self.motion.single_move("z2", self.z2_safe_pos)

        elif flag == 2:
            self.motion.single_move("x", placing_coordinates_dict["X"])
            self.motion.single_move("y", placing_coordinates_dict["Y"])
            self.motion.single_move("z2", placing_coordinates_dict["Z2"])
            self.motion.close_pge()
            self.motion.single_move("z2", self.z2_safe_pos)
            self.motion.single_move("y", bottle_coordinates_dict["Y"])
            self.motion.single_move("x", bottle_coordinates_dict["X"])
            self.motion.single_move("z2", bottle_coordinates_dict["ZBack"])
            self.motion.open_pge()
            self.motion.single_move("z2", self.z2_safe_pos)

        self.motion.single_move("y", self.y_safe_pos)

    # weigh action
    def weighing_action(self, align_pos: int, action_pos: int, times: int, flag: bool = False):
        """Run the specified number of actuator cycles at the alignment and dispensing positions."""
        self.logger.info(f"Starting dispensing cycles: {times}; actuator depth: {action_pos}")

        for i in tqdm(range(times), desc="Progress", ascii=True):
            self.motion.single_move_zr("r", 5000)
            self.motion.single_move("z", action_pos)
            self.motion.single_move_zr("r", 10000)
            self.motion.single_move("z", align_pos)
            self.motion.send_instr("r", self.motion.set_zero_point)
            self.motion.single_move_zr("r", 5000)
            self.motion.single_move("z", action_pos)
            self.motion.single_move_zr("r", 10000)
            self.motion.single_move("z", align_pos)
            self.motion.single_move("r", 9900)
            self.motion.send_instr("r", self.motion.set_zero_point)

    def coarse_weighing(self, align_pos: int, action_pos: int):
        action_times = 0
        while not self.stop_event.is_set():
            self.motion.single_move_zr("r", 5000)
            self.motion.single_move("z", action_pos)
            self.motion.single_move_zr("r", 10000)
            self.motion.single_move("z", align_pos)
            self.motion.send_instr("r", self.motion.set_zero_point)
            self.motion.single_move_zr("r", 5000)
            self.motion.single_move("z", action_pos)
            self.motion.single_move_zr("r", 10000)
            self.motion.single_move("z", align_pos)
            self.motion.single_move("r", 9900)
            self.motion.send_instr("r", self.motion.set_zero_point)
            action_times += 1
            if action_times > 50:
                self.calibrate_actuator(align_pos)

    # balance reading monitoring
    def monitor_weight(self, weight_threshold: float) -> float:
        """Set the stop event when the measured mass reaches the coarse threshold in mg."""
        while not self.stop_event.is_set():
            current_weight = self.weighing.stable_weight()
            if current_weight >= weight_threshold:
                self.logger.info(
                    f"Current mass (mg): {current_weight}; reached coarse threshold (mg): {weight_threshold}"
                )
                self.stop_event.set()
            sleep(0.5)

    def weighing_params(self, target_weight: float) -> tuple:
        if target_weight <= 3.0:
            test_action_times = 4
            drop_weight = 0.2
            weight_threshold = 1.0
        elif target_weight <= 5.0:
            test_action_times = 4
            drop_weight = 0.3
            weight_threshold = 1.5
        elif target_weight <= 10.0:
            test_action_times = 5
            drop_weight = 0.3
            weight_threshold = 2.0
        elif target_weight <= 20.0:
            test_action_times = 5
            drop_weight = 0.4
            weight_threshold = 2.5
        elif target_weight <= 50.0:
            test_action_times = 5
            drop_weight = 0.5
            weight_threshold = 3.0
        elif target_weight <= 100.0:
            test_action_times = 10
            drop_weight = 0.7
            weight_threshold = 3.5
        else:
            test_action_times = 10
            drop_weight = 1
            weight_threshold = 4.0

        return test_action_times, drop_weight, weight_threshold

    def calibrate_actuator(self, align_pos):
        self.motion.send_instr("z", self.motion.back_zero)
        while True:
            sleep(2)
            status = self.motion.get_running_status("z")
            if status[4:7] == "111":
                break
        self.motion.single_move("z", align_pos)
        self.motion.single_move("r", 20000)
        self.motion.send_instr("r", self.motion.set_zero_point)

    # start weighing
    def start_weighing(self, align_pos: int, action_pos: int, target_weight: float) -> float:
        """Run coarse and fine dispensing and return the measured mass in mg."""

        if not 0 < target_weight < float("inf"):
            raise ValueError("Target mass must be finite and positive.")
        self.stop_event.clear()
        speed_z = "00 64"
        speed_r = "00 C8"
        self.motion.send_instr("z", self.motion.speed, speed_z)
        self.motion.send_instr("r", self.motion.speed, speed_r)

        # get the balance weighing position
        weighing_coordinates_dict = (
            self.balance_coordinates_df.loc[
                self.balance_coordinates_df["usage"] == "weigh", ["X", "Y", "Z1"]
            ]
            .iloc[0]
            .to_dict()
        )
        # move to the balance weighing position
        self.motion.single_move("x", weighing_coordinates_dict["X"])
        self.motion.single_move("y", weighing_coordinates_dict["Y"])
        self.motion.single_move("z1", weighing_coordinates_dict["Z1"])

        # calculate weighing parameters
        test_action_times, drop_weight, weight_threshold = self.weighing_params(target_weight)

        # weigh action
        self.logger.info(
            f"Starting weighing; target mass (mg): {target_weight}; actuator depth: {action_pos}"
        )

        self.weighing.tare()
        prev_weight = 0
        test_thresh_weight = 0.1

        # test the average drop amount
        while True:
            self.weighing_action(
                align_pos=align_pos,
                action_pos=action_pos,
                times=test_action_times,
            )
            current_weight = self.weighing.stable_weight()
            sleep(2)
            current_weight = self.weighing.stable_weight()
            if current_weight - prev_weight > test_action_times * test_thresh_weight:
                total_weight = current_weight - prev_weight
                average_weight = total_weight / test_action_times
                if average_weight - drop_weight > 0.2:
                    action_pos -= 10
                elif drop_weight - average_weight > 0.2:
                    action_pos += 10
                self.logger.info(
                    f"Mean dispensed mass (mg): {average_weight}; target dispensed mass (mg): {drop_weight}"
                )
                break
            elif (
                current_weight - prev_weight < test_action_times * test_thresh_weight
                and current_weight - prev_weight > 0
            ):
                total_weight = current_weight - prev_weight
                average_weight = total_weight / test_action_times
                self.logger.info(f"Mean dispensed mass (mg): {average_weight}; retrying")
                action_pos += 20
            else:
                self.logger.info(f"Mean dispensed mass is zero; retrying")
                action_pos += 30
        self.calibrate_actuator(align_pos)

        weighing_thread = Thread(target=self.coarse_weighing, args=(align_pos, action_pos))
        monitor_thread = Thread(target=self.monitor_weight, args=(weight_threshold,))

        weighing_thread.start()
        monitor_thread.start()

        weighing_thread.join()
        monitor_thread.join()

        self.calibrate_actuator(align_pos)

        # fine weighing action
        current_weight = self.weighing.stable_weight()
        action_count = 0
        while current_weight < target_weight:
            if abs(target_weight - current_weight) <= 0.1:
                break
            self.weighing_action(
                align_pos=align_pos,
                action_pos=action_pos,
                times=1,
            )
            prev_weight = current_weight
            current_weight = self.weighing.stable_weight()
            sleep(2)
            current_weight = self.weighing.stable_weight()
            average_weight = current_weight - prev_weight
            self.logger.info(
                f"Target mass (mg): {target_weight}，Current mass (mg): ：{current_weight}; dispensed mass (mg): {round(average_weight, 2)}"
            )
            action_count += 1
            if action_count > 20:
                self.calibrate_actuator(align_pos)
                action_count = 0
            if current_weight == prev_weight:
                action_pos += 3
            elif current_weight - prev_weight > 0.3:
                action_pos -= 10
        self.calibrate_actuator(align_pos)
        actual_weight = current_weight
        self.logger.info(
            f"Target mass (mg): {target_weight}; measured mass (mg): {actual_weight}; error (mg): {actual_weight - target_weight}; relative error (%): {(actual_weight - target_weight) / target_weight * 100}%"
        )

        # move to the safe position
        self.motion.single_move("z1", self.z1_safe_pos)

        return actual_weight
