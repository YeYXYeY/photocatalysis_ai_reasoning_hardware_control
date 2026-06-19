"""Reusable workflow definitions for the mobile robot system."""

from __future__ import annotations

from time import sleep
from typing import Callable


KNOWN_WORKFLOWS = ("photocatalysis",)


def _rotate_to_default(agv) -> None:
    """Run the default rotation mission after a move."""

    agv.switch_mode("auto")
    agv.run_mission("rotate_0")


def run_photocatalysis_workflow(robot, agv, sleep_fn: Callable[[float], None] = sleep) -> None:
    """Execute the pipetting to photocatalysis transfer workflow."""

    robot.enable_robot()
    robot.run_script("pipetting")
    sleep_fn(30)

    agv.switch_mode("manual")
    agv.move_to_marker("photocatalytic")
    _rotate_to_default(agv)
    sleep_fn(10)

    robot.run_script("photocatalytic")
    sleep_fn(30)

    agv.switch_mode("manual")
    agv.move_to_marker("weighing")
    _rotate_to_default(agv)


def run_named_workflow(workflow_name: str, *, robot, agv, sleep_fn: Callable[[float], None] = sleep) -> None:
    """Dispatch a named workflow."""

    if workflow_name == "photocatalysis":
        run_photocatalysis_workflow(robot, agv, sleep_fn=sleep_fn)
        return
    raise ValueError(f"Unknown workflow '{workflow_name}'.")
