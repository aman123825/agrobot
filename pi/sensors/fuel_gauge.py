"""Battery state-of-charge via coulomb counting on the INA219 (BOM #10).

Integrating measured current over time gives a far better SoC estimate than
voltage alone (which sags under load). Voltage is used once at startup to seed
the initial SoC from the LiPo discharge curve.

The CoulombCounter is pure logic (unit-testable); FuelGauge wraps an INA219
read via the pi-ina219 library, guarded so it runs without hardware.
"""
from __future__ import annotations

import logging
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config  # noqa: E402

logger = logging.getLogger(__name__)

# 3S LiPo open-circuit voltage -> approximate SoC (pack volts, percent).
_OCV_CURVE = [
    (12.6, 100), (12.0, 80), (11.7, 60), (11.4, 40), (11.1, 20), (10.5, 5), (9.9, 0)
]


def soc_from_voltage(pack_v: float) -> float:
    """Piecewise-linear SoC% from open-circuit pack voltage."""
    if pack_v >= _OCV_CURVE[0][0]:
        return 100.0
    if pack_v <= _OCV_CURVE[-1][0]:
        return 0.0
    for (v_hi, s_hi), (v_lo, s_lo) in zip(_OCV_CURVE, _OCV_CURVE[1:]):
        if v_lo <= pack_v <= v_hi:
            t = (pack_v - v_lo) / (v_hi - v_lo)
            return s_lo + t * (s_hi - s_lo)
    return 0.0


class CoulombCounter:
    """Tracks consumed mAh and remaining SoC by integrating current."""

    def __init__(self, capacity_mah: float = 2200.0, initial_soc: float = 100.0):
        self.capacity_mah = capacity_mah
        self.consumed_mah = capacity_mah * (1.0 - initial_soc / 100.0)

    def update(self, current_ma: float, dt_s: float) -> None:
        # Positive current = discharge.
        self.consumed_mah += current_ma * (dt_s / 3600.0)
        self.consumed_mah = max(0.0, min(self.capacity_mah, self.consumed_mah))

    @property
    def soc_percent(self) -> float:
        return 100.0 * (1.0 - self.consumed_mah / self.capacity_mah)

    @property
    def remaining_mah(self) -> float:
        return self.capacity_mah - self.consumed_mah


class FuelGauge:
    def __init__(self, capacity_mah: float = 2200.0, shunt_ohms: float = 0.1,
                 max_amps: float = 5.0, addr: int | None = None):
        self.addr = addr if addr is not None else config.I2C_ADDR["ina219"]
        self._ina = None
        self._last_t = time.time()
        try:
            from ina219 import INA219

            self._ina = INA219(shunt_ohms, max_amps, address=self.addr)
            self._ina.configure()
            init_soc = soc_from_voltage(self._ina.voltage())
            logger.info("INA219 fuel gauge ready; seed SoC=%.0f%%", init_soc)
        except Exception as exc:
            logger.warning("INA219 unavailable (%s); SoC by integration only", exc)
            init_soc = 100.0
        self.counter = CoulombCounter(capacity_mah, init_soc)

    def update(self) -> float:
        """Sample current, integrate, return SoC%."""
        now = time.time()
        dt = now - self._last_t
        self._last_t = now
        current_ma = 0.0
        if self._ina is not None:
            try:
                current_ma = self._ina.current()  # mA
            except Exception:
                current_ma = 0.0
        self.counter.update(current_ma, dt)
        return self.counter.soc_percent
