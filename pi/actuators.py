"""Pi-side actuator control via the PCF8574 I2C expander (circuit §5.3).

Expander outputs (active-LOW relays):
    P0 -> grass-cutter relay (12V 775 motor)
    P1 -> misting / herbicide relay
    P2 -> seed-sower servo enable
The I2C access is guarded so this imports and runs (as no-ops) on a machine
without smbus2 or the hardware present.
"""
from __future__ import annotations

import logging
import os
import sys
import time

sys.path.append(os.path.dirname(__file__))
import config

logger = logging.getLogger(__name__)

PIN_GRASS_CUTTER = 0
PIN_MISTING = 1
PIN_SEED_SERVO = 2


class Pcf8574:
    def __init__(self, addr: int | None = None, bus_id: int = 1):
        self.addr = addr if addr is not None else config.I2C_ADDR["pcf8574"]
        self._state = 0xFF  # all outputs HIGH == all active-LOW relays OFF
        self._bus = None
        try:
            import smbus2

            self._bus = smbus2.SMBus(bus_id)
            self._bus.write_byte(self.addr, self._state)
            logger.info("PCF8574 ready at 0x%02X", self.addr)
        except Exception as exc:
            logger.warning("PCF8574 unavailable (%s); actuator calls are no-ops", exc)
            self._bus = None

    def _flush(self) -> None:
        if self._bus is not None:
            self._bus.write_byte(self.addr, self._state)

    def set_pin(self, pin: int, on: bool) -> None:
        """Drive an active-LOW relay: on -> pin LOW, off -> pin HIGH."""
        if on:
            self._state &= ~(1 << pin)
        else:
            self._state |= 1 << pin
        self._flush()

    # ---- convenience ----
    def spray(self, duration_s: float = 0.6) -> None:
        self.set_pin(PIN_MISTING, True)
        time.sleep(duration_s)
        self.set_pin(PIN_MISTING, False)

    def grass_cutter(self, on: bool) -> None:
        self.set_pin(PIN_GRASS_CUTTER, on)

    def all_off(self) -> None:
        self._state = 0xFF
        self._flush()
