"""Thermal guardian (FC-02): keep the rover from cooking itself in field heat.

Indian field summers hit 40-45 C ambient and a sealed enclosure in the sun can
reach 60-70 C inside. This module watches three temperatures and decides what
the orchestrator should do:

  * Pi CPU temp   (/sys/class/thermal/thermal_zone0/temp)
  * Battery pack  (10k NTC thermistor -> ADS1115 A2, beta model)
  * Ambient air   (DHT22, supplied by the caller)

The decision logic (``evaluate``) and the NTC conversion (``ntc_temp_c``) are
pure functions, fully unit-testable without hardware. All hardware access is
guarded so this imports and runs (returning safe defaults) on a dev machine
without smbus2 or the sysfs thermal node.

Thresholds (degC):
    CPU  > 75 -> throttle inference fps
    CPU  > 80 -> pause + alert
    pack > 55 -> STOP + disable charging + critical alert
    pack > 65 -> safe shutdown
"""
from __future__ import annotations

import logging
import math

logger = logging.getLogger(__name__)

# ADS1115 channel the pack NTC is wired to (A2; A0/A1 are the motor sensors).
ADS1115_ADDR = 0x48
_REG_CONVERT = 0x00
_REG_CONFIG = 0x01
# Single-shot, +/-4.096V PGA, 128 SPS, single-ended A2.
_CFG_A2 = 0x8000 | 0x6000 | 0x0200 | 0x0100 | 0x0080 | 0x0003

# Thresholds (degC).
CPU_THROTTLE_C = 75.0
CPU_PAUSE_C = 80.0
PACK_STOP_C = 55.0
PACK_SHUTDOWN_C = 65.0

CPU_THERMAL_ZONE = "/sys/class/thermal/thermal_zone0/temp"


def ntc_temp_c(voltage: float, vcc: float = 3.3, series_r: float = 10000.0,
               beta: float = 3950.0, r25: float = 10000.0) -> float:
    """Convert an NTC divider voltage to temperature (degC) via the beta model.

    Wiring assumed: Vcc -- series_r -- (node = ADC) -- NTC -- GND, so the NTC
    resistance is ``R_ntc = series_r * V / (Vcc - V)``. The beta equation then
    gives temperature relative to 25 C (298.15 K) and r25.

    Raises ValueError for non-physical voltages (<=0 or >=vcc) where the divider
    math is undefined.
    """
    if voltage <= 0.0 or voltage >= vcc:
        raise ValueError(f"voltage {voltage} out of range (0, {vcc})")
    r_ntc = series_r * voltage / (vcc - voltage)
    # 1/T = 1/T0 + (1/beta) * ln(R/R25)
    t0 = 298.15  # 25 C in kelvin
    inv_t = 1.0 / t0 + (1.0 / beta) * math.log(r_ntc / r25)
    return 1.0 / inv_t - 273.15


def evaluate(cpu_c: float | None, pack_c: float | None,
             ambient_c: float | None) -> dict:
    """Decide a thermal action from the three temperatures.

    Returns ``{"action": <str>, "reasons": [<str>, ...]}`` where action is the
    most severe of:
        "ok" < "throttle" < "pause" < "stop" < "shutdown"
    Pack temperature dominates (fire risk): pack>65 -> shutdown, pack>55 -> stop
    (and charging must be disabled). CPU>80 -> pause, CPU>75 -> throttle. A
    None reading is ignored (treated as no data for that sensor). Ambient is
    advisory only and never escalates on its own, but is reported in reasons.
    """
    severity = {"ok": 0, "throttle": 1, "pause": 2, "stop": 3, "shutdown": 4}
    action = "ok"
    reasons: list[str] = []

    def escalate(candidate: str, reason: str) -> None:
        nonlocal action
        reasons.append(reason)
        if severity[candidate] > severity[action]:
            action = candidate

    if pack_c is not None:
        if pack_c > PACK_SHUTDOWN_C:
            escalate("shutdown", f"pack {pack_c:.1f}C > {PACK_SHUTDOWN_C:.0f}C")
        elif pack_c > PACK_STOP_C:
            escalate("stop", f"pack {pack_c:.1f}C > {PACK_STOP_C:.0f}C (disable charging)")

    if cpu_c is not None:
        if cpu_c > CPU_PAUSE_C:
            escalate("pause", f"cpu {cpu_c:.1f}C > {CPU_PAUSE_C:.0f}C")
        elif cpu_c > CPU_THROTTLE_C:
            escalate("throttle", f"cpu {cpu_c:.1f}C > {CPU_THROTTLE_C:.0f}C")

    if ambient_c is not None and ambient_c >= 45.0:
        reasons.append(f"ambient {ambient_c:.1f}C high")

    return {"action": action, "reasons": reasons}


def read_cpu_temp_c() -> float | None:
    """Read the Pi CPU temperature from sysfs (guarded). None if unavailable."""
    try:
        with open(CPU_THERMAL_ZONE, "r", encoding="utf-8") as fh:
            return int(fh.read().strip()) / 1000.0
    except (OSError, ValueError) as exc:
        logger.debug("CPU temp unavailable (%s)", exc)
        return None


class ThermalGuardian:
    """Reads CPU + pack NTC + ambient and returns an ``evaluate`` decision.

    Pack NTC is read from ADS1115 A2 via smbus2 single-shot (same pattern as the
    current monitor). All hardware access is guarded.
    """

    def __init__(self, addr: int = ADS1115_ADDR, bus_id: int = 1,
                 vcc: float = 3.3, series_r: float = 10000.0,
                 beta: float = 3950.0, r25: float = 10000.0):
        self.addr = addr
        self.vcc = vcc
        self.series_r = series_r
        self.beta = beta
        self.r25 = r25
        self._bus = None
        try:
            import smbus2

            self._bus = smbus2.SMBus(bus_id)
            logger.info("ThermalGuardian: ADS1115 pack NTC ready at 0x%02X", addr)
        except Exception as exc:
            logger.warning("ThermalGuardian: ADS1115 unavailable (%s); pack temp = None", exc)
            self._bus = None

    def read_pack_temp_c(self) -> float | None:
        """Read pack NTC temperature from ADS1115 A2 (guarded). None if no bus."""
        if self._bus is None:
            return None
        try:
            import time

            cfg = _CFG_A2
            self._bus.write_i2c_block_data(self.addr, _REG_CONFIG, [cfg >> 8, cfg & 0xFF])
            time.sleep(0.009)
            data = self._bus.read_i2c_block_data(self.addr, _REG_CONVERT, 2)
            raw = (data[0] << 8) | data[1]
            if raw >= 0x8000:
                raw -= 0x10000
            voltage = raw * 4.096 / 32768.0
            return ntc_temp_c(voltage, self.vcc, self.series_r, self.beta, self.r25)
        except (OSError, ValueError) as exc:
            logger.debug("ThermalGuardian: pack NTC read failed (%s)", exc)
            return None

    def check(self, ambient_c: float | None = None) -> dict:
        """Read all sensors and return the ``evaluate`` decision dict."""
        cpu_c = read_cpu_temp_c()
        pack_c = self.read_pack_temp_c()
        return evaluate(cpu_c, pack_c, ambient_c)
