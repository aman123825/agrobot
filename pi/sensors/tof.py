"""VL53L1X time-of-flight distance reader (circuit §4.1, I2C 0x29).

Gives the orchestrator a real forward distance so obstacle stops use the
400 mm stop rule instead of the fail-safe "stop on any detection", and so the
aimed-spray path gets target depth.

Tries the Pimoroni ``VL53L1X`` package first, then Adafruit's
``adafruit_vl53l1x``. Both imports are guarded so this runs (returning None)
on a machine without the hardware or drivers.
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)


class TofSensor:
    def __init__(self, addr: int | None = None, bus_id: int = 1):
        self.addr = addr if addr is not None else config.I2C_ADDR["vl53l1x"]
        self.bus_id = bus_id
        self.backend: str | None = None
        self._dev = None

    def start(self) -> bool:
        """Open the sensor and start ranging. True if a backend came up."""
        try:
            import VL53L1X  # Pimoroni driver

            dev = VL53L1X.VL53L1X(i2c_bus=self.bus_id, i2c_address=self.addr)
            dev.open()
            dev.start_ranging(2)  # 2 = medium range (~3 m), good for 400 mm rule
            self._dev = dev
            self.backend = "pimoroni"
            logger.info("VL53L1X ready (pimoroni, 0x%02X)", self.addr)
            return True
        except Exception:
            pass
        try:
            import adafruit_vl53l1x
            import board
            import busio

            i2c = busio.I2C(board.SCL, board.SDA)
            dev = adafruit_vl53l1x.VL53L1X(i2c, address=self.addr)
            dev.start_ranging()
            self._dev = dev
            self.backend = "adafruit"
            logger.info("VL53L1X ready (adafruit, 0x%02X)", self.addr)
            return True
        except Exception as exc:
            logger.warning("VL53L1X unavailable (%s); distance = None", exc)
            self._dev = None
            self.backend = None
            return False

    def read_mm(self) -> float | None:
        """Latest distance in mm, or None when no sensor / no valid reading."""
        if self._dev is None:
            return None
        try:
            if self.backend == "pimoroni":
                mm = float(self._dev.get_distance())
                return mm if mm > 0 else None
            # adafruit: .distance is in cm, None until data_ready
            cm = self._dev.distance
            return float(cm) * 10.0 if cm else None
        except Exception:
            return None

    def stop(self) -> None:
        if self._dev is None:
            return
        try:
            if self.backend == "pimoroni":
                self._dev.stop_ranging()
                self._dev.close()
            else:
                self._dev.stop_ranging()
        except Exception:
            pass
        self._dev = None
        self.backend = None
