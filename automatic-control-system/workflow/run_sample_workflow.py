import os
import sys
import time

import pandas as pd

from client.master_control_client import MasterControlClient
from utils.task_utils import (
    calc_liquid_comsumption,
    check_remaining,
    find_station_by_rackname,
    split_task,
    sup_chemicals,
)
from workflow.replenishment import get_replenishment_plan


def check_result(result: bool) -> None:
    """Stop the sample workflow as soon as a station command reports failure."""
    if result:
        print("Operation succeeded")
        return
    print("Operation failed")
    raise SystemExit(-1)


class SampleWorkflowRunner:
    """Run the retained supplementary sample workflow from the cleaned repository."""

    def __init__(
        self,
        master_control_client: MasterControlClient | None = None,
        task_file_name: str = "0923task.xlsx",
    ):
        self.master_control_client = master_control_client or MasterControlClient()
        self.task_file_name = task_file_name
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.task_dir = os.path.join(self.project_root, "task")

    @property
    def task_file_path(self) -> str:
        return os.path.join(self.task_dir, self.task_file_name)

    def run(self) -> None:
        print(self.task_dir)
        time.sleep(10)
        _, liquid_task_df = split_task(file_path=self.task_file_path)
        self.master_control_client.init_status()

        liquid_consumption = calc_liquid_comsumption(liquid_task_df)
        _, liquid_chemical_list, _, liquid_replacing_dict = check_remaining(
            "liquid_station", liquid_consumption
        )
        print(liquid_chemical_list, list(liquid_replacing_dict.keys()), liquid_replacing_dict)
        self.replenish_solution(liquid_chemical_list, liquid_replacing_dict)

    def replenish_solution(
        self,
        liquid_chemical_list: list[str],
        liquid_replacing_dict: dict[str, dict[str, int]],
    ) -> None:
        """Replace reagents that do not have enough remaining liquid."""
        if not liquid_chemical_list:
            return

        for rack_name, replacing_dict in liquid_replacing_dict.items():
            print(
                f"Chemicals that need replenishment: {replacing_dict} on rack {rack_name}"
            )
            station_name = find_station_by_rackname(
                self.master_control_client.station_status.load_status(), rack_name
            )
            if station_name == "None":
                continue

            replenishment_plan = get_replenishment_plan(station_name, rack_name)
            replacing_task_df = pd.DataFrame(
                list(replacing_dict.items()), columns=["Key", "Value"]
            )

            for command in replenishment_plan.before_replace:
                check_result(self.master_control_client.mobile_robot(command))

            replace_result = self.master_control_client.liquid_station(
                replacing_task_df, "replace_reactants"
            )
            check_result(replace_result)
            if replace_result:
                sup_chemicals(replacing_dict=replacing_dict)

            for command in replenishment_plan.after_replace:
                check_result(self.master_control_client.mobile_robot(command))


def main() -> int:
    """Run the retained sample workflow from the repository root."""
    runner = SampleWorkflowRunner()
    runner.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
