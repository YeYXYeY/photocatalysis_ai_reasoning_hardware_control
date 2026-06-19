"""Low-level command builders for the CR10 dashboard interface."""

ENABLE_ROBOT = "EnableRobot()"
DISABLE_ROBOT = "DisableRobot()"
CLEAR_ERROR = "ClearError()"
GET_ROBOT_MODE = "RobotMode()"
GET_POSE = "GetPose()"
EMERGENCY_STOP = "EmergencyStop()"


def build_run_script_command(script_name: str) -> str:
    """Build the dashboard command that runs a named robot script."""

    return f"RunScript({script_name})"
