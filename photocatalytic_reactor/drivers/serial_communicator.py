"""Thread-safe serial communication helpers."""

from __future__ import annotations

import logging
import threading

try:
    import serial
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    serial = None


class SerialCommunicator:
    """Wrap a pyserial connection with logging and a shared lock."""

    def __init__(self, serial_param: dict, logger: logging.Logger):
        self.logger = logger
        self.serial_param = serial_param
        self.serial_conn = None
        self.connected = False
        self.lock = threading.Lock()
        self.connect()

    def connect(self) -> None:
        """Open the configured serial port if it is not already connected."""
        if serial is None:
            raise ModuleNotFoundError(
                "pyserial is required to open hardware serial connections."
            )
        try:
            if not self.connected:
                self.serial_conn = serial.Serial(**self.serial_param)
                self.connected = True
                self.logger.info(
                    "Connected to serial port %s.", self.serial_param["port"]
                )
        except serial.SerialException as exc:
            self.logger.error("Failed to connect to the serial port: %s", exc)
            raise

    def disconnect(self) -> None:
        """Close the serial connection if it is open."""
        if self.connected:
            self.serial_conn.close()
            self.connected = False
            self.logger.info(
                "Disconnected serial port %s.", self.serial_param["port"]
            )

    def write_with_lock(self, data: bytes) -> bool:
        """Write bytes to the serial port while holding the shared lock."""
        with self.lock:
            if self.connected:
                try:
                    self.serial_conn.write(data)
                    return True
                except serial.SerialException as exc:
                    self.logger.error("Failed to write serial data: %s", exc)
                    raise
        return False

    def readline_with_lock(self) -> bytes | None:
        """Read one line from the serial port while holding the shared lock."""
        with self.lock:
            if self.connected:
                try:
                    return self.serial_conn.readline()
                except serial.SerialException as exc:
                    self.logger.error("Failed to read a serial line: %s", exc)
                    raise
        return None

    def read_bytes_with_lock(self, size: int) -> bytes | None:
        """Read a fixed number of bytes while holding the shared lock."""
        with self.lock:
            if self.connected:
                try:
                    return self.serial_conn.read(size)
                except serial.SerialException as exc:
                    self.logger.error("Failed to read serial bytes: %s", exc)
                    raise
        return None

    def read_until_with_lock(self, terminator: bytes) -> bytes | None:
        """Read until the requested terminator arrives while holding the lock."""
        with self.lock:
            if self.connected:
                try:
                    return self.serial_conn.read_until(terminator)
                except serial.SerialException as exc:
                    self.logger.error("Failed to read serial bytes until terminator: %s", exc)
                    raise
        return None
