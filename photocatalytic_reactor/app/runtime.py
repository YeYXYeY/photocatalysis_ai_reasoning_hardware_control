"""Runtime assembly helpers for hardware-backed reactor workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from core.config import PROJECT_PATH, config_logger, load_config
from drivers.digital_io_rs485 import DigitalIO_RS485
from drivers.power_controller import PowerController
from drivers.serial_communicator import SerialCommunicator
from drivers.shaker_controller import ShakerController


@dataclass
class ReactorHardware:
    """Connected hardware handles used by the reactor workflows."""

    serial_comm: SerialCommunicator
    power_controller: PowerController
    shaker_controller: ShakerController
    led_relay: DigitalIO_RS485
    pump_relay: DigitalIO_RS485
    temp_sensor: DigitalIO_RS485


@dataclass
class RuntimeContext:
    """Bundle configuration, logger, and live hardware handles."""

    project_dir: Path
    config: dict[str, Any]
    logger: Any
    log_file_path: Path
    hardware: ReactorHardware


def create_log_file_path(project_dir: Path | None = None) -> Path:
    """Create the timestamped log file path used by runtime entrypoints."""
    base_dir = Path(project_dir) if project_dir else PROJECT_PATH
    return base_dir / "logs" / f"{datetime.now():%Y%m%d-%H%M%S}.log"


def build_runtime_context(
    config_path: str | Path | None = None,
    primary_config_key: str = "shaker",
) -> RuntimeContext:
    """Load configuration, create a logger, and connect hardware controllers."""
    project_dir = PROJECT_PATH
    config = load_config(config_path)
    log_file_path = create_log_file_path(project_dir)
    logger = config_logger(log_file_path)

    serial_param = config.get(primary_config_key, {})
    if not serial_param:
        raise ValueError(f"Missing required '{primary_config_key}' serial configuration.")

    serial_comm = SerialCommunicator(serial_param, logger)
    hardware = ReactorHardware(
        serial_comm=serial_comm,
        power_controller=PowerController(serial_comm, 1),
        shaker_controller=ShakerController(serial_comm, 2),
        led_relay=DigitalIO_RS485(serial_comm, 10),
        pump_relay=DigitalIO_RS485(serial_comm, 11),
        temp_sensor=DigitalIO_RS485(serial_comm, 12),
    )
    logger.info("Runtime context initialized with serial port %s", serial_param.get("port"))
    return RuntimeContext(
        project_dir=project_dir,
        config=config,
        logger=logger,
        log_file_path=log_file_path,
        hardware=hardware,
    )
