"""Shared configuration values for robot arm and AGV control."""

from __future__ import annotations

ROBOT_HOST = "192.0.2.6"
ROBOT_DASHBOARD_PORT = 29999
ROBOT_SOCKET_TIMEOUT = 5.0

AGV_HOST = "192.0.2.100"
AGV_PORT = 8080
AGV_HTTP_TIMEOUT = 10.0
AUTOCHEM_MAP_ID = "5f2434d0-d091-11ee-9ed8-0242ac110002"

MAP_IDS = {
    "autochem": AUTOCHEM_MAP_ID,
}

MARKER_IDS = {
    "charge": "560660ae-1a58-11ee-93af-0242ac110002",
    "weighing": "a08296ac-1ae3-11ee-ac79-0242ac110002",
    "pipetting": "c0bc80f8-1ae3-11ee-ac79-0242ac110002",
    "photocatalytic": "d006655f-1ae3-11ee-ac79-0242ac110002",
    "nmr": "e835022f-1ae3-11ee-ac79-0242ac110002",
}

MISSION_REQUESTS = {
    "rotate_0": {
        "missionId": "fd87abe2-06b7-43eb-a849-359f85f4641d",
        "missionCode": "WM10380",
    },
}

KNOWN_MARKERS = tuple(sorted(MARKER_IDS))
KNOWN_MISSIONS = tuple(sorted(MISSION_REQUESTS))


def build_agv_urls(host: str = AGV_HOST, port: int = AGV_PORT) -> dict[str, str]:
    """Build AGV endpoint URLs from host and port values."""

    api_root = f"http://{host}:{port}"
    return {
        "map_list": f"{api_root}/api/v3/AGVMaps",
        "map_sync": f"{api_root}/api/v3/vehicles/maps/sync",
        "manual_relocation": f"{api_root}/api/v3/vehicles/maps/relocation/manual",
        "auto_relocation": f"{api_root}/api/v3/vehicles/maps/relocation/auto",
        "move_to_marker": f"{api_root}/api/v3/vehicles/task/moveToMarker",
        "list_markers": f"{api_root}/api/v3/markers",
        "list_missions": f"{api_root}/api/v3/missionWorks",
        "run_mission": f"{api_root}/api/v3/missionWorks",
        "auto_mode": f"{api_root}/api/v3/vehicles/controls/autoMode",
        "manual_mode": f"{api_root}/api/v3/vehicles/controls/manualMode",
        "vehicle_info": f"{api_root}/api/v3/vehicles/",
    }
