"""Motor current + stall detection via ADS1115 (I2C ADC) + ACS712 sensors.

Neither the ESP32 (ADC1 fully used) nor the Pi (no native ADC) has free analog
inputs, so an ADS1115 16-bit I2C ADC reads two ACS712-30A hall current sensors
(one per motor side). Sustained over-current => stall => the orchestrator sends
STOP and a Telegram alert.

I2C is read directly via smbus2 (guarded). The conversion + stall logic are
pure functions, fully unit-testable without hardware.
"""
from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)

ADS1115_ADDR = 0x48
_REG_CONVERT = 0x00
_REG_CONFIG = 0x01

# ACS712-30A: 66 mV/A, centered at Vcc/2 (2.5 V at a 5 V supply).
ACS712_SENS_V_PER_A = 0.066
ACS712_OFFSET_V = 2.5

# Single-shot, +/-4.096V PGA, 128 SPS. MUX per channel ORed in.
_CFG_BASE = 0x8000 | 0x0200 | 0x0100 | 0x0080 | 0x0003
_MUX_SINGLE = {0: 0x4000, 1: 0x5000, 2: 0x6000, 3: 0x7000}


def acs712_amps(voltage: float, offset_v: float = ACS712_OFFSET_V,
                sens: float = ACS712_SENS_V_PER_A) -> float:
    """Convert an ACS712 output voltage to current (amps)."""
    return (voltage - offset_v) / sens


class StallDetector:
    """Flags a stall when |current| stays above a threshold for a hold time."""

    def __init__(self, threshold_a: float = 3.0, hold_s: float = 0.8):
        self.threshold_a = threshold_a
        self.hold_s = hold_s
        self._since: float | None = None

    def update(self, current_a: float, now: float) -> bool:
        if abs(current_a) >= self.threshold_a:
            if self._since is None:
                self._since = now
            return (now - self._since) >= self.hold_s
        self._since = None
        return False


class CurrentMonitor:
    def __init__(self, addr: int = ADS1115_ADDR, bus_id: int = 1,
                 stall_threshold_a: float = 3.0):
        self.addr = addr
        self._bus = None
        self.stall_left = StallDetector(stall_threshold_a)
        self.stall_right = StallDetector(stall_threshold_a)
        try:
            import smbus2

            self._bus = smbus2.SMBus(bus_id)
            logger.info("ADS1115 current monitor ready at 0x%02X", addr)
        except Exception as exc:
            logger.warning("ADS1115 unavailable (%s); current = 0", exc)
            self._bus = None

    def _read_voltage(self, channel: int) -> float:
        if self._bus is None:
            return ACS712_OFFSET_V  # reads as zero current
        cfg = _CFG_BASE | _MUX_SINGLE[channel]
        self._bus.write_i2c_block_data(self.addr, _REG_CONFIG, [cfg >> 8, cfg & 0xFF])
        time.sleep(0.009)
        data = self._bus.read_i2c_block_data(self.addr, _REG_CONVERT, 2)
        raw = (data[0] << 8) | data[1]
        if raw >= 0x8000:
            raw -= 0x10000
        return raw * 4.096 / 32768.0  # PGA = +/-4.096 V

    def currents(self) -> tuple[float, float]:
        """(left_amps, right_amps)."""
        return (acs712_amps(self._read_voltage(0)), acs712_amps(self._read_voltage(1)))

    def check_stall(self, now: float | None = None) -> bool:
        now = now if now is not None else time.time()
        cl, cr = self.currents()
        return self.stall_left.update(cl, now) or self.stall_right.update(cr, now)
