"""Client for the CR10 robot dashboard interface."""

from __future__ import annotations

import socket

from .config import ROBOT_DASHBOARD_PORT, ROBOT_HOST, ROBOT_SOCKET_TIMEOUT
from .robot_commands import (
    CLEAR_ERROR,
    DISABLE_ROBOT,
    EMERGENCY_STOP,
    ENABLE_ROBOT,
    GET_POSE,
    GET_ROBOT_MODE,
    build_run_script_command,
)


class CR10:
    """Send dashboard commands to the CR10 robot arm."""

    def __init__(
        self,
        host: str = ROBOT_HOST,
        dashboard_port: int = ROBOT_DASHBOARD_PORT,
        timeout: float = ROBOT_SOCKET_TIMEOUT,
    ) -> None:
        self.host = host
        self.dashboard_port = dashboard_port
        self.timeout = timeout
        self._dashboard_socket = socket.create_connection((self.host, self.dashboard_port), timeout=self.timeout)
        self._dashboard_socket.settimeout(self.timeout)

    def __enter__(self) -> "CR10":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def close(self) -> None:
        """Close the dashboard connection."""

        self._dashboard_socket.close()

    def _send_dashboard_command(self, command: str) -> str:
        """Send one command and return a single response frame."""

        self._dashboard_socket.sendall(command.encode("utf-8"))
        try:
            return self._dashboard_socket.recv(4096).decode("utf-8").strip()
        except socket.timeout:
            return ""

    def enable_robot(self) -> str:
        """Enable the robot controller."""

        return self._send_dashboard_command(ENABLE_ROBOT)

    def disable_robot(self) -> str:
        """Disable the robot controller."""

        return self._send_dashboard_command(DISABLE_ROBOT)

    def clear_error(self) -> str:
        """Clear active controller errors."""

        return self._send_dashboard_command(CLEAR_ERROR)

    def get_state(self) -> str:
        """Query the current robot mode."""

        return self._send_dashboard_command(GET_ROBOT_MODE)

    def get_pose(self) -> str:
        """Query the current robot pose."""

        return self._send_dashboard_command(GET_POSE)

    def emergency_stop(self) -> str:
        """Trigger an emergency stop."""

        return self._send_dashboard_command(EMERGENCY_STOP)

    def run_script(self, script_name: str) -> str:
        """Run a named robot-side script."""

        return self._send_dashboard_command(build_run_script_command(script_name))
