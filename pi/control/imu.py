"""MPU6050 IMU read + tilt-halt logic (circuit / BOM #36).

Provides roll/pitch from the accelerometer and a tilt check. If the rover
pitches/rolls beyond the safe limits, the orchestrator sends EVT_TILT_HALT to
the ESP32. I2C is guarded so this runs (returning zeros) without hardware.
"""
from __future__ import annotations

import logging
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)

PITCH_LIMIT_DEG = 20.0
ROLL_LIMIT_DEG = 15.0

_PWR_MGMT_1 = 0x6B
_ACCEL_XOUT_H = 0x3B


def roll_pitch_from_accel(ax: float, ay: float, az: float) -> tuple[float, float]:
    """Compute (roll, pitch) in degrees from accelerometer components."""
    roll = math.degrees(math.atan2(ay, math.sqrt(ax * ax + az * az)))
    pitch = math.degrees(math.atan2(-ax, math.sqrt(ay * ay + az * az)))
    return (roll, pitch)


def is_tilt_unsafe(roll: float, pitch: float) -> bool:
    return abs(pitch) > PITCH_LIMIT_DEG or abs(roll) > ROLL_LIMIT_DEG


class MPU6050:
    def __init__(self, addr: int | None = None, bus_id: int = 1):
        self.addr = addr if addr is not None else config.I2C_ADDR["mpu6050"]
        self._bus = None
        try:
            import smbus2

            self._bus = smbus2.SMBus(bus_id)
            self._bus.write_byte_data(self.addr, _PWR_MGMT_1, 0)  # wake
            logger.info("MPU6050 ready at 0x%02X", self.addr)
        except Exception as exc:
            logger.warning("MPU6050 unavailable (%s); tilt always safe", exc)
            self._bus = None

    def _read_word(self, reg: int) -> int:
        hi = self._bus.read_byte_data(self.addr, reg)
        lo = self._bus.read_byte_data(self.addr, reg + 1)
        val = (hi << 8) | lo
        return val - 65536 if val >= 0x8000 else val

    def read_accel_g(self) -> tuple[float, float, float]:
        if self._bus is None:
            return (0.0, 0.0, 1.0)  # level
        scale = 16384.0  # +/-2g default
        ax = self._read_word(_ACCEL_XOUT_H) / scale
        ay = self._read_word(_ACCEL_XOUT_H + 2) / scale
        az = self._read_word(_ACCEL_XOUT_H + 4) / scale
        return (ax, ay, az)

    def roll_pitch(self) -> tuple[float, float]:
        return roll_pitch_from_accel(*self.read_accel_g())

    def tilt_unsafe(self) -> bool:
        return is_tilt_unsafe(*self.roll_pitch())
