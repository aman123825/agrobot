"""Wheel-encoder pulse counting -> per-side velocity (mm/s).

Counts Hall-encoder pulses on the Pi GPIOs (left=BCM17, right=BCM27 per the
updated circuit), and converts pulse rate to linear velocity using the wheel
geometry. RPi.GPIO is imported lazily/guarded so this module runs (returning
zero velocity) on a dev machine without the hardware.
"""
from __future__ import annotations

import logging
import os
import sys
import threading
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)

# Wheel geometry (circuit / BOM): 65 mm wheels, 20-pole encoder disc.
WHEEL_DIAMETER_MM = 65.0
PULSES_PER_REV = 20
MM_PER_PULSE = (3.141592653589793 * WHEEL_DIAMETER_MM) / PULSES_PER_REV


class Encoders:
    def __init__(self, pin_left: int | None = None, pin_right: int | None = None):
        self.pin_left = pin_left if pin_left is not None else config.GPIO["encoder_left"]
        self.pin_right = pin_right if pin_right is not None else config.GPIO["encoder_right"]
        self._counts = {"left": 0, "right": 0}
        self._last = {"left": (0, 0.0), "right": (0, 0.0)}  # (count, t) at last sample
        self._lock = threading.Lock()
        self._gpio = None

    def start(self) -> bool:
        try:
            from RPi import GPIO

            self._gpio = GPIO
            GPIO.setmode(GPIO.BCM)
            for side, pin in (("left", self.pin_left), ("right", self.pin_right)):
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(
                    pin, GPIO.RISING, callback=self._make_cb(side)
                )
            now = time.time()
            self._last = {"left": (0, now), "right": (0, now)}
            logger.info("Encoders started (L=BCM%s R=BCM%s)", self.pin_left, self.pin_right)
            return True
        except Exception as exc:
            logger.warning("Encoders unavailable (%s); velocity = 0", exc)
            self._gpio = None
            return False

    def _make_cb(self, side: str):
        def _cb(_channel):
            with self._lock:
                self._counts[side] += 1
        return _cb

    def velocity_mm_s(self) -> tuple[float, float]:
        """Per-side linear velocity since the previous call (left, right)."""
        now = time.time()
        out = []
        with self._lock:
            for side in ("left", "right"):
                count = self._counts[side]
                last_count, last_t = self._last[side]
                dt = now - last_t
                pulses = count - last_count
                v = (pulses * MM_PER_PULSE / dt) if dt > 0 else 0.0
                self._last[side] = (count, now)
                out.append(v)
        return (out[0], out[1])

    def stop(self) -> None:
        if self._gpio is not None:
            try:
                self._gpio.cleanup([self.pin_left, self.pin_right])
            except Exception:
                pass
