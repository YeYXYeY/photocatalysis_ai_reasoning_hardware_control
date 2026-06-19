"""HTTP client for the Trans200 AGV fleet API."""

from __future__ import annotations

from typing import Any

import requests

from .config import (
    AGV_HOST,
    AGV_HTTP_TIMEOUT,
    AGV_PORT,
    KNOWN_MARKERS,
    KNOWN_MISSIONS,
    MAP_IDS,
    MARKER_IDS,
    MISSION_REQUESTS,
    build_agv_urls,
)


class Trans200:
    """Wrap the Trans200 REST API with a small, reusable client."""

    def __init__(
        self,
        host: str = AGV_HOST,
        port: int = AGV_PORT,
        timeout: float = AGV_HTTP_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout = timeout
        self.urls = build_agv_urls(host=host, port=port)
        self.session = session or requests.Session()
        self.headers = {"Content-Type": "application/json"}

    def __enter__(self) -> "Trans200":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP session."""

        self.session.close()

    def _request(
        self,
        method: str,
        url: str,
        *,
        payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Send an HTTP request and decode JSON when available."""

        response = self.session.request(
            method=method,
            url=url,
            json=payload,
            params=params,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        content_type = response.headers.get("Content-Type", "")
        if "json" in content_type.lower():
            return response.json()
        return response.text

    def list_maps(self) -> Any:
        """Return the available AGV maps."""

        return self._request("GET", self.urls["map_list"])

    def sync_map(self, map_name: str) -> Any:
        """Sync the AGV to a known map."""

        map_id = MAP_IDS.get(map_name, map_name)
        return self._request("POST", self.urls["map_sync"], payload={"agvMapId": map_id})

    def switch_mode(self, mode: str) -> Any:
        """Switch the AGV between auto and manual control."""

        if mode not in {"auto", "manual"}:
            raise ValueError("Mode must be 'auto' or 'manual'.")
        return self._request("POST", self.urls[f"{mode}_mode"])

    def relocate_manual(self, x: float, y: float, angle: float) -> Any:
        """Set the manual relocation pose."""

        payload = {"init_x": x, "init_y": y, "init_angle": angle}
        return self._request("POST", self.urls["manual_relocation"], payload=payload)

    def relocate_auto(self) -> Any:
        """Trigger automatic relocation."""

        return self._request("POST", self.urls["auto_relocation"])

    def list_markers(self) -> Any:
        """Return marker metadata from the fleet server."""

        return self._request("GET", self.urls["list_markers"])

    def move_to_marker(self, marker_name: str) -> Any:
        """Move the AGV to a named marker."""

        if marker_name not in MARKER_IDS:
            raise ValueError(f"Unknown marker '{marker_name}'. Known markers: {', '.join(KNOWN_MARKERS)}")
        return self._request(
            "POST",
            self.urls["move_to_marker"],
            payload={"markerId": MARKER_IDS[marker_name]},
        )

    def list_missions(self) -> Any:
        """Return mission definitions from the fleet server."""

        return self._request("GET", self.urls["list_missions"])

    def run_mission(self, mission_name: str) -> Any:
        """Run a named AGV mission."""

        if mission_name not in MISSION_REQUESTS:
            raise ValueError(
                f"Unknown mission '{mission_name}'. Known missions: {', '.join(KNOWN_MISSIONS)}",
            )
        return self._request(
            "POST",
            self.urls["run_mission"],
            payload=MISSION_REQUESTS[mission_name],
        )

    def get_vehicle_info(self) -> Any:
        """Fetch the current AGV vehicle state."""

        return self._request("GET", self.urls["vehicle_info"])
