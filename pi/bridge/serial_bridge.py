"""UART bridge between the Pi (AI decisions) and the ESP32 (real-time control).

Commands are HMAC-signed via security.sign() before transmission so the ESP32
can authenticate them and reject spoofed/replayed traffic (circuit §4.4 /
BOM #107).

Pi -> ESP32:  STOP, RESUME, LEFT, RIGHT, FWD, BACK, DRIVE_STOP, DOSE,
              PUMP_DISABLE, PUMP_ENABLE, PAUSE_IRRIGATION, RESUME_IRRIGATION
ESP32 -> Pi:  ACK <cmd>, NAK ..., and telemetry over MQTT
"""
from __future__ import annotations

import logging
import os
import sys

import serial

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import security

logger = logging.getLogger(__name__)

DEFAULT_PORT = os.getenv("ESP32_SERIAL", "/dev/ttyUSB0")
DEFAULT_BAUD = 115200


class SerialBridge:
    def __init__(self, port: str = DEFAULT_PORT, baud: int = DEFAULT_BAUD):
        self.port = port
        self.baud = baud
        self._ser: serial.Serial | None = None
        if not security.is_configured():
            logger.warning(
                "AGRO_LINK_KEY not set: commands will be unsigned and the ESP32 "
                "will reject them. Set AGRO_LINK_KEY to match the firmware."
            )

    def open(self) -> None:
        self._ser = serial.Serial(self.port, self.baud, timeout=0.1)

    def send(self, command: str) -> None:
        """Sign (if a key is configured) and transmit a command."""
        assert self._ser, "call open() first"
        payload = security.sign(command) if security.is_configured() else command
        self._ser.write(f"{payload}\n".encode())

    def read_line(self) -> str | None:
        """Read one ACK/NAK/telemetry line from the ESP32, if available."""
        assert self._ser, "call open() first"
        line = self._ser.readline().decode(errors="ignore").strip()
        return line or None

    def close(self) -> None:
        if self._ser:
            self._ser.close()
