import unittest
from unittest.mock import patch

from devices.config import build_agv_urls
from devices.cr10 import CR10
from devices.robot_commands import build_run_script_command
from devices.trans200 import Trans200


class FakeSocket:
    def __init__(self, response: bytes = b"ok\n") -> None:
        self.response = response
        self.sent_messages: list[bytes] = []
        self.timeout: float | None = None
        self.closed = False

    def settimeout(self, timeout: float) -> None:
        self.timeout = timeout

    def sendall(self, payload: bytes) -> None:
        self.sent_messages.append(payload)

    def recv(self, _: int) -> bytes:
        return self.response

    def close(self) -> None:
        self.closed = True


class FakeResponse:
    def __init__(self, *, json_data=None, text: str = "", content_type: str = "application/json") -> None:
        self._json_data = json_data
        self.text = text or ""
        self.headers = {"Content-Type": content_type}
        if json_data is None:
            self.content = self.text.encode("utf-8")
        else:
            self.content = b'{"ok": true}'

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._json_data


class RecordingSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[dict] = []
        self.closed = False

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return self.response

    def close(self) -> None:
        self.closed = True


class DeviceTests(unittest.TestCase):
    @patch("devices.cr10.socket.create_connection")
    def test_cr10_enable_robot_sends_expected_command(self, mock_create_connection) -> None:
        fake_socket = FakeSocket()
        mock_create_connection.return_value = fake_socket

        with CR10(host="127.0.0.1") as robot:
            response = robot.enable_robot()

        self.assertEqual(response, "ok")
        self.assertEqual(fake_socket.sent_messages, [b"EnableRobot()"])
        self.assertTrue(fake_socket.closed)

    def test_build_run_script_command_formats_script_name(self) -> None:
        self.assertEqual(build_run_script_command("pipetting"), "RunScript(pipetting)")

    def test_build_agv_urls_uses_supplied_host_and_port(self) -> None:
        urls = build_agv_urls(host="10.0.0.5", port=9000)

        self.assertEqual(
            urls["move_to_marker"],
            "http://10.0.0.5:9000/api/v3/vehicles/task/moveToMarker",
        )

    def test_trans200_move_to_marker_sends_named_marker_payload(self) -> None:
        response = FakeResponse(json_data={"status": "queued"})
        session = RecordingSession(response)
        client = Trans200(host="127.0.0.1", port=8080, session=session)

        result = client.move_to_marker("weighing")
        client.close()

        self.assertEqual(result, {"status": "queued"})
        self.assertEqual(session.calls[0]["method"], "POST")
        self.assertEqual(
            session.calls[0]["json"],
            {"markerId": "a08296ac-1ae3-11ee-ac79-0242ac110002"},
        )
        self.assertTrue(session.closed)

    def test_trans200_run_mission_sends_named_mission_payload(self) -> None:
        response = FakeResponse(json_data={"status": "started"})
        session = RecordingSession(response)
        client = Trans200(host="127.0.0.1", port=8080, session=session)

        result = client.run_mission("rotate_0")

        self.assertEqual(result, {"status": "started"})
        self.assertEqual(session.calls[0]["json"]["missionCode"], "WM10380")

    def test_trans200_rejects_unknown_mode(self) -> None:
        client = Trans200(
            host="127.0.0.1",
            port=8080,
            session=RecordingSession(FakeResponse(json_data={})),
        )

        with self.assertRaises(ValueError):
            client.switch_mode("invalid")
