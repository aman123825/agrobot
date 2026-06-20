"""UART bridge between the Pi (AI decisions) and the ESP32 (real-time control).

Pi -> ESP32:  STOP, RESUME, LEFT, RIGHT, SPRAY_ON, SPRAY_OFF,
              PAUSE_IRRIGATION, EVT_TILT_HALT, PUMP_DISABLE
ESP32 -> Pi:  sensor_ack, gps_coords, battery_pct, mode_status, velocity
See circuit §4.4 / BOM #107.
"""
from __future__ import annotations

import serial

import config


class SerialBridge:
    def __init__(self, port: str = config.SERIAL_PORT, baud: int = config.SERIAL_BAUD):
        self.port = port
        self.baud = baud
        self._ser: serial.Serial | None = None

    def open(self) -> None:
        self._ser = serial.Serial(self.port, self.baud, timeout=0.1)

    def send(self, command: str) -> None:
        """Send a newline-terminated command to the ESP32."""
        assert self._ser, "call open() first"
        self._ser.write(f"{command}\n".encode())

    def read_line(self) -> str | None:
        """Read one telemetry line from the ESP32, if available."""
        assert self._ser, "call open() first"
        line = self._ser.readline().decode(errors="ignore").strip()
        return line or None

    def close(self) -> None:
        if self._ser:
            self._ser.close()
