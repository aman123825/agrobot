"""Field-health telemetry (docs/farmer-needs-and-durability.md §2.2 "Monitoring").

"Log CPU temp, undervoltage flags, SD health, reboot counts -> the
dashboard/WhatsApp summary. Predict failures instead of discovering them."

HealthMonitor samples the Pi's own vitals - CPU temperature, the vcgencmd
undervoltage/throttling bitmask, SD-card free space (the practical proxy for
SD health without vendor tools), memory pressure, load average and a persisted
reboot counter - into one flat dict the orchestrator publishes over MQTT and
the alerter turns into a WhatsApp/Telegram one-liner. Rising CPU temps,
latched undervoltage flags and a climbing boot count are the early warnings of
the §2.1 failure ranking (SD corruption, brownouts, heat), seen *before* the
rover dies mid-season.

Stdlib-only and dependency-injected (sysfs path, command runner, disk_usage,
boot-counter file) so it imports, runs and unit-tests cleanly on a Windows dev
box: every probe degrades to None off-Pi. No MQTT/network imports here - the
orchestrator owns publishing.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)

CPU_THERMAL_ZONE = "/sys/class/thermal/thermal_zone0/temp"
MEMINFO_PATH = "/proc/meminfo"
DEFAULT_BOOT_FILE = "~/.agrirover_boots"

# vcgencmd get_throttled bit layout: bits 0-3 = happening NOW, bits 16-19 =
# has OCCURRED since boot (latched). Same order in both nibbles.
_FLAG_NAMES = ("undervoltage", "freq_capped", "throttled", "soft_temp_limit")
THROTTLED_BITS: dict[int, str] = {
    **{bit: f"{name}_now" for bit, name in enumerate(_FLAG_NAMES)},
    **{bit + 16: f"{name}_occurred" for bit, name in enumerate(_FLAG_NAMES)},
}

_SEVERITY = {"ok": 0, "warn": 1, "critical": 2}

# Boot-counter files already incremented by this process (double-increment
# guard: constructing two HealthMonitors must not count two "boots").
_boot_counted: set[str] = set()


def decode_throttled(mask: int) -> dict:
    """Decode the ``vcgencmd get_throttled`` hex bitmask into named booleans.

    Pure function. Returns the eight flags of THROTTLED_BITS plus the raw
    mask, e.g. 0x50005 -> undervoltage_now, throttled_now and both their
    occurred-since-boot latches set.
    """
    out = {name: bool(mask & (1 << bit)) for bit, name in THROTTLED_BITS.items()}
    out["raw"] = mask
    return out


def evaluate_status(cpu_temp_c: float | None, disk_free_pct: float | None,
                    throttled: dict | None, *,
                    warn_temp_c: float = 70.0, critical_temp_c: float = 80.0,
                    warn_disk_free_pct: float = 20.0,
                    critical_disk_free_pct: float = 10.0) -> str:
    """Overall health severity: "ok" < "warn" < "critical".

    critical: CPU >= critical_temp_c, disk free < critical_disk_free_pct,
              or undervoltage/throttling happening NOW.
    warn:     CPU >= warn_temp_c, disk free < warn_disk_free_pct, freq cap or
              soft temp limit active, or any occurred-since-boot latch.
    None readings (off-Pi / probe failed) are treated as no data.
    """
    status = "ok"

    def escalate(candidate: str) -> None:
        nonlocal status
        if _SEVERITY[candidate] > _SEVERITY[status]:
            status = candidate

    if cpu_temp_c is not None:
        if cpu_temp_c >= critical_temp_c:
            escalate("critical")
        elif cpu_temp_c >= warn_temp_c:
            escalate("warn")

    if disk_free_pct is not None:
        if disk_free_pct < critical_disk_free_pct:
            escalate("critical")
        elif disk_free_pct < warn_disk_free_pct:
            escalate("warn")

    if throttled:
        if throttled.get("undervoltage_now") or throttled.get("throttled_now"):
            escalate("critical")
        elif (throttled.get("freq_capped_now")
              or throttled.get("soft_temp_limit_now")
              or any(throttled.get(f"{n}_occurred") for n in _FLAG_NAMES)):
            escalate("warn")

    return status


def run_command(args: list[str], timeout_s: float = 2.0) -> str | None:
    """Run a command, return stripped stdout, or None on any failure."""
    try:
        proc = subprocess.run(args, capture_output=True, text=True,
                              timeout=timeout_s)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        logger.debug("command %s unavailable (%s)", args[0], exc)
    return None


def _read_boot_state(path: str) -> dict:
    """Read the persisted boot-counter file (JSON, legacy plain int, or {})."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read().strip()
    except OSError:
        return {}
    try:
        state = json.loads(text)
        if isinstance(state, dict):
            return state
    except ValueError:
        pass
    try:
        return {"count": int(text)}
    except ValueError:
        return {}


class HealthMonitor:
    """Samples Pi vitals into one flat dict; predicts failure, not autopsy."""

    def __init__(self,
                 thermal_zone: str = CPU_THERMAL_ZONE,
                 meminfo_path: str = MEMINFO_PATH,
                 disk_path: str = "/",
                 boot_file: str = DEFAULT_BOOT_FILE,
                 run_cmd: Callable[[list[str]], str | None] = run_command,
                 disk_usage: Callable = shutil.disk_usage,
                 warn_temp_c: float = 70.0,
                 critical_temp_c: float = 80.0,
                 warn_disk_free_pct: float = 20.0,
                 critical_disk_free_pct: float = 10.0):
        self.thermal_zone = thermal_zone
        self.meminfo_path = meminfo_path
        self.disk_path = disk_path
        self.run_cmd = run_cmd
        self.disk_usage = disk_usage
        self.warn_temp_c = warn_temp_c
        self.critical_temp_c = critical_temp_c
        self.warn_disk_free_pct = warn_disk_free_pct
        self.critical_disk_free_pct = critical_disk_free_pct
        self.boot_file = os.path.abspath(os.path.expanduser(boot_file))
        self.boot_count, self.last_boot = self._count_boot()

    # --- reboot counter (persisted; one increment per process) ---

    def _count_boot(self) -> tuple[int, float | None]:
        state = _read_boot_state(self.boot_file)
        prior = int(state.get("count", 0))
        if self.boot_file in _boot_counted:
            # Same process already counted this boot; report, don't re-count.
            last = state.get("last_boot")
            return prior, float(last) if last is not None else None
        count, last_boot = prior + 1, time.time()
        try:
            with open(self.boot_file, "w", encoding="utf-8") as fh:
                json.dump({"count": count, "last_boot": last_boot}, fh)
        except OSError as exc:
            logger.warning("boot counter not persisted (%s)", exc)
        _boot_counted.add(self.boot_file)
        logger.info("boot #%d recorded (%s)", count, self.boot_file)
        return count, last_boot

    # --- probes (each degrades to None off-Pi) ---

    def read_cpu_temp_c(self) -> float | None:
        """CPU temperature: sysfs thermal zone, else vcgencmd, else None."""
        try:
            with open(self.thermal_zone, "r", encoding="utf-8") as fh:
                return int(fh.read().strip()) / 1000.0
        except (OSError, ValueError):
            pass
        out = self.run_cmd(["vcgencmd", "measure_temp"])  # "temp=48.3'C"
        if out:
            try:
                return float(out.split("=")[1].split("'")[0])
            except (IndexError, ValueError):
                pass
        return None

    def read_throttled(self) -> dict | None:
        """Decoded ``vcgencmd get_throttled`` flags, or None off-Pi."""
        out = self.run_cmd(["vcgencmd", "get_throttled"])  # "throttled=0x50005"
        if not out:
            return None
        try:
            mask = int(out.split("=")[1], 16)
        except (IndexError, ValueError):
            return None
        return decode_throttled(mask)

    def read_disk(self) -> dict:
        """Free %, total and used bytes for disk_path (SD card root on the Pi)."""
        try:
            usage = self.disk_usage(self.disk_path)
        except OSError as exc:
            logger.debug("disk usage unavailable (%s)", exc)
            return {"disk_total_bytes": None, "disk_used_bytes": None,
                    "disk_free_pct": None}
        free_pct = 100.0 * usage.free / usage.total if usage.total else 0.0
        return {"disk_total_bytes": usage.total, "disk_used_bytes": usage.used,
                "disk_free_pct": round(free_pct, 1)}

    def read_memory(self) -> dict:
        """MemTotal/MemAvailable (kB) + used% from /proc/meminfo, None off-Pi."""
        info: dict[str, int] = {}
        try:
            with open(self.meminfo_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0].endswith(":"):
                        info[parts[0][:-1]] = int(parts[1])
        except (OSError, ValueError):
            pass
        total, avail = info.get("MemTotal"), info.get("MemAvailable")
        if total and avail is not None:
            return {"mem_total_kb": total, "mem_available_kb": avail,
                    "mem_used_pct": round(100.0 * (1.0 - avail / total), 1)}
        return {"mem_total_kb": None, "mem_available_kb": None,
                "mem_used_pct": None}

    def read_load(self) -> float | None:
        """1-minute load average; None where unsupported (Windows)."""
        try:
            return round(os.getloadavg()[0], 2)
        except (AttributeError, OSError):
            return None

    # --- the one call the orchestrator makes ---

    def sample(self) -> dict:
        """One flat dict of all vitals + overall ``status`` (ok/warn/critical)."""
        throttled = self.read_throttled()
        data: dict = {"t": round(time.time(), 1),
                      "cpu_temp_c": self.read_cpu_temp_c()}
        if throttled is not None:
            data.update({k: v for k, v in throttled.items() if k != "raw"})
            data["throttled_raw"] = throttled["raw"]
        else:
            data.update({name: None for name in THROTTLED_BITS.values()})
            data["throttled_raw"] = None
        data.update(self.read_disk())
        data.update(self.read_memory())
        data["load_1min"] = self.read_load()
        data["boot_count"] = self.boot_count
        data["last_boot"] = self.last_boot
        data["status"] = evaluate_status(
            data["cpu_temp_c"], data["disk_free_pct"], throttled,
            warn_temp_c=self.warn_temp_c,
            critical_temp_c=self.critical_temp_c,
            warn_disk_free_pct=self.warn_disk_free_pct,
            critical_disk_free_pct=self.critical_disk_free_pct)
        return data

    def format_alert(self, sample: dict) -> str | None:
        """Telegram/WhatsApp one-liner when status != "ok", else None."""
        status = sample.get("status", "ok")
        if status == "ok":
            return None
        reasons: list[str] = []
        if sample.get("undervoltage_now"):
            reasons.append("UNDERVOLTAGE now - check battery/cable")
        if sample.get("throttled_now"):
            reasons.append("CPU throttled now")
        if sample.get("freq_capped_now"):
            reasons.append("CPU freq capped")
        if sample.get("soft_temp_limit_now"):
            reasons.append("soft temp limit active")
        cpu = sample.get("cpu_temp_c")
        if cpu is not None and cpu >= self.warn_temp_c:
            reasons.append(f"CPU {cpu:.1f}C")
        disk = sample.get("disk_free_pct")
        if disk is not None and disk < self.warn_disk_free_pct:
            reasons.append(f"SD card {disk:.0f}% free")
        occurred = [n for n in _FLAG_NAMES
                    if sample.get(f"{n}_occurred") and not sample.get(f"{n}_now")]
        if occurred:
            reasons.append("since boot: " + ", ".join(occurred))
        if not reasons:
            reasons.append("degraded")
        return (f"AgriRover health {status.upper()} "
                f"(boot #{sample.get('boot_count', '?')}): "
                + "; ".join(reasons))
