"""Single CLI entry point for the mobile robot project."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from devices import CR10, Trans200
from devices.config import KNOWN_MARKERS, KNOWN_MISSIONS
from workflows import KNOWN_WORKFLOWS, run_named_workflow


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""

    parser = argparse.ArgumentParser(
        description="Control the CR10 robot arm and the Trans200 AGV from one entry point.",
    )
    subparsers = parser.add_subparsers(dest="resource", required=True)

    robot_parser = subparsers.add_parser("robot", help="Send commands to the CR10 robot arm.")
    robot_subparsers = robot_parser.add_subparsers(dest="robot_action", required=True)
    for action_name in (
        "enable",
        "disable",
        "clear-error",
        "state",
        "pose",
        "emergency-stop",
    ):
        robot_subparsers.add_parser(action_name)
    run_script_parser = robot_subparsers.add_parser(
        "run-script",
        help="Run a robot-side script by name.",
    )
    run_script_parser.add_argument("script_name", help="Robot script name, for example 'pipetting'.")

    agv_parser = subparsers.add_parser("agv", help="Send commands to the Trans200 AGV.")
    agv_subparsers = agv_parser.add_subparsers(dest="agv_action", required=True)
    switch_mode_parser = agv_subparsers.add_parser("switch-mode", help="Switch AGV mode.")
    switch_mode_parser.add_argument("mode", choices=("auto", "manual"))
    move_parser = agv_subparsers.add_parser("move", help="Move the AGV to a named marker.")
    move_parser.add_argument("marker_name", help=f"Known markers: {', '.join(KNOWN_MARKERS)}")
    mission_parser = agv_subparsers.add_parser("run-mission", help="Run a named AGV mission.")
    mission_parser.add_argument("mission_name", help=f"Known missions: {', '.join(KNOWN_MISSIONS)}")
    sync_map_parser = agv_subparsers.add_parser("sync-map", help="Sync a named AGV map.")
    sync_map_parser.add_argument("map_name", nargs="?", default="autochem")
    agv_subparsers.add_parser("list-markers", help="List AGV markers.")
    agv_subparsers.add_parser("list-missions", help="List AGV missions.")
    agv_subparsers.add_parser("vehicle-info", help="Fetch the latest AGV state.")

    workflow_parser = subparsers.add_parser(
        "workflow",
        help="Run a predefined multi-device workflow.",
    )
    workflow_parser.add_argument(
        "workflow_name",
        choices=KNOWN_WORKFLOWS,
        help="Workflow name.",
    )
    return parser


def handle_robot_command(args: argparse.Namespace) -> int:
    """Execute a CR10 command."""

    with CR10() as robot:
        if args.robot_action == "run-script":
            response = robot.run_script(args.script_name)
        else:
            action_map = {
                "enable": robot.enable_robot,
                "disable": robot.disable_robot,
                "clear-error": robot.clear_error,
                "state": robot.get_state,
                "pose": robot.get_pose,
                "emergency-stop": robot.emergency_stop,
            }
            response = action_map[args.robot_action]()
    if response:
        print(response)
    return 0


def handle_agv_command(args: argparse.Namespace) -> int:
    """Execute a Trans200 AGV command."""

    with Trans200() as agv:
        if args.agv_action == "switch-mode":
            response = agv.switch_mode(args.mode)
        elif args.agv_action == "move":
            response = agv.move_to_marker(args.marker_name)
        elif args.agv_action == "run-mission":
            response = agv.run_mission(args.mission_name)
        elif args.agv_action == "sync-map":
            response = agv.sync_map(args.map_name)
        elif args.agv_action == "list-markers":
            response = agv.list_markers()
        elif args.agv_action == "list-missions":
            response = agv.list_missions()
        else:
            response = agv.get_vehicle_info()
    print(response)
    return 0


def handle_workflow_command(args: argparse.Namespace) -> int:
    """Execute a predefined workflow."""

    with CR10() as robot, Trans200() as agv:
        run_named_workflow(args.workflow_name, robot=robot, agv=agv)
    print(f"Workflow '{args.workflow_name}' completed.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and dispatch the selected command."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.resource == "robot":
            return handle_robot_command(args)
        if args.resource == "agv":
            return handle_agv_command(args)
        return handle_workflow_command(args)
    except Exception as exc:  # pragma: no cover - defensive CLI guard.
        print(f"Command failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
