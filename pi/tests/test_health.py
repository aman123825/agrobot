"""Tests for the field-health telemetry module (farmer-needs §2.2 Monitoring)."""
import json
from collections import namedtuple

from monitor.health import (HealthMonitor, decode_throttled, evaluate_status)

Usage = namedtuple("Usage", "total used free")


def make_monitor(tmp_path, thermal: str | None = None,
                 vcgencmd: dict | None = None, free_frac: float = 0.5,
                 meminfo: str | None = None, **kwargs) -> HealthMonitor:
    """HealthMonitor with every hardware probe faked (runs on Windows)."""
    zone = tmp_path / "thermal_zone0_temp"
    if thermal is not None:
        zone.write_text(thermal)
    mem = tmp_path / "meminfo"
    if meminfo is not None:
        mem.write_text(meminfo)
    responses = vcgencmd or {}

    def run_cmd(args):
        return responses.get(args[-1])

    total = 32_000_000_000
    free = int(total * free_frac)

    def disk_usage(_path):
        return Usage(total, total - free, free)

    return HealthMonitor(thermal_zone=str(zone), meminfo_path=str(mem),
                         disk_path=str(tmp_path),
                         boot_file=str(tmp_path / "boots.json"),
                         run_cmd=run_cmd, disk_usage=disk_usage, **kwargs)


class TestDecodeThrottled:
    def test_all_clear(self):
        flags = decode_throttled(0x0)
        assert flags["raw"] == 0
        assert not any(v for k, v in flags.items() if k != "raw")

    def test_undervoltage_and_throttled_with_history(self):
        # 0x50005 = classic weak-supply Pi: bits 0, 2, 16, 18.
        flags = decode_throttled(0x50005)
        assert flags["undervoltage_now"] and flags["throttled_now"]
        assert flags["undervoltage_occurred"] and flags["throttled_occurred"]
        assert not flags["freq_capped_now"]
        assert not flags["soft_temp_limit_now"]
        assert not flags["freq_capped_occurred"]

    def test_undervoltage_now_only(self):
        flags = decode_throttled(0x1)
        assert flags["undervoltage_now"]
        assert not flags["undervoltage_occurred"]
        assert not flags["throttled_now"]

    def test_occurred_only(self):
        # Latched history but nothing happening right now.
        flags = decode_throttled(0x50000)
        assert flags["undervoltage_occurred"] and flags["throttled_occurred"]
        assert not flags["undervoltage_now"] and not flags["throttled_now"]


class TestEvaluateStatus:
    def test_all_nominal_ok(self):
        assert evaluate_status(45.0, 60.0, decode_throttled(0x0)) == "ok"

    def test_no_data_is_ok(self):
        assert evaluate_status(None, None, None) == "ok"

    def test_temp_thresholds(self):
        assert evaluate_status(69.9, 60.0, None) == "ok"
        assert evaluate_status(70.0, 60.0, None) == "warn"
        assert evaluate_status(79.9, 60.0, None) == "warn"
        assert evaluate_status(80.0, 60.0, None) == "critical"

    def test_disk_thresholds(self):
        assert evaluate_status(45.0, 20.0, None) == "ok"
        assert evaluate_status(45.0, 15.0, None) == "warn"
        assert evaluate_status(45.0, 8.0, None) == "critical"

    def test_undervoltage_now_is_critical(self):
        assert evaluate_status(45.0, 60.0, decode_throttled(0x1)) == "critical"

    def test_throttled_now_is_critical(self):
        assert evaluate_status(45.0, 60.0, decode_throttled(0x4)) == "critical"

    def test_occurred_only_is_warn(self):
        assert evaluate_status(45.0, 60.0, decode_throttled(0x50000)) == "warn"

    def test_worst_wins(self):
        # Warn temp + critical undervoltage -> critical.
        assert evaluate_status(72.0, 60.0, decode_throttled(0x1)) == "critical"


class TestBootCounter:
    def test_first_boot_creates_file(self, tmp_path):
        mon = make_monitor(tmp_path)
        assert mon.boot_count == 1
        state = json.loads((tmp_path / "boots.json").read_text())
        assert state["count"] == 1
        assert state["last_boot"] > 0

    def test_increments_existing_count(self, tmp_path):
        (tmp_path / "boots.json").write_text(
            json.dumps({"count": 4, "last_boot": 123.0}))
        mon = make_monitor(tmp_path)
        assert mon.boot_count == 5

    def test_double_increment_guard_same_process(self, tmp_path):
        first = make_monitor(tmp_path)
        second = make_monitor(tmp_path)
        assert first.boot_count == 1
        assert second.boot_count == 1
        assert json.loads((tmp_path / "boots.json").read_text())["count"] == 1

    def test_last_boot_timestamp_recorded(self, tmp_path):
        mon = make_monitor(tmp_path)
        assert mon.last_boot is not None and mon.last_boot > 0
        assert mon.sample()["last_boot"] == mon.last_boot


class TestSample:
    def test_runs_on_windows_with_everything_missing(self, tmp_path):
        # No thermal file, no vcgencmd, no meminfo: Nones, not crashes.
        mon = make_monitor(tmp_path)
        data = mon.sample()
        assert data["cpu_temp_c"] is None
        assert data["undervoltage_now"] is None
        assert data["mem_total_kb"] is None
        assert data["status"] == "ok"
        assert data["boot_count"] == 1

    def test_sysfs_temp_wins(self, tmp_path):
        mon = make_monitor(tmp_path, thermal="71500\n",
                           vcgencmd={"measure_temp": "temp=48.3'C"})
        data = mon.sample()
        assert data["cpu_temp_c"] == 71.5
        assert data["status"] == "warn"

    def test_vcgencmd_temp_fallback(self, tmp_path):
        mon = make_monitor(tmp_path,
                           vcgencmd={"measure_temp": "temp=48.3'C",
                                     "get_throttled": "throttled=0x0"})
        data = mon.sample()
        assert data["cpu_temp_c"] == 48.3
        assert data["throttled_raw"] == 0
        assert data["status"] == "ok"

    def test_undervoltage_now_goes_critical(self, tmp_path):
        mon = make_monitor(tmp_path,
                           vcgencmd={"get_throttled": "throttled=0x50005"})
        data = mon.sample()
        assert data["undervoltage_now"] is True
        assert data["status"] == "critical"

    def test_low_disk_reported(self, tmp_path):
        mon = make_monitor(tmp_path, free_frac=0.05)
        data = mon.sample()
        assert data["disk_free_pct"] == 5.0
        assert data["disk_total_bytes"] == 32_000_000_000
        assert data["status"] == "critical"

    def test_meminfo_parsed(self, tmp_path):
        mon = make_monitor(tmp_path, meminfo=(
            "MemTotal:        3882924 kB\n"
            "MemFree:          150000 kB\n"
            "MemAvailable:    1941462 kB\n"))
        data = mon.sample()
        assert data["mem_total_kb"] == 3882924
        assert data["mem_available_kb"] == 1941462
        assert data["mem_used_pct"] == 50.0


class TestFormatAlert:
    def test_none_when_ok(self, tmp_path):
        mon = make_monitor(tmp_path)
        data = mon.sample()
        assert data["status"] == "ok"
        assert mon.format_alert(data) is None

    def test_message_when_critical(self, tmp_path):
        mon = make_monitor(tmp_path, thermal="82000\n",
                           vcgencmd={"get_throttled": "throttled=0x50005"})
        data = mon.sample()
        msg = mon.format_alert(data)
        assert msg is not None
        assert "CRITICAL" in msg
        assert "UNDERVOLTAGE" in msg
        assert "82.0C" in msg

    def test_message_when_disk_warn(self, tmp_path):
        mon = make_monitor(tmp_path, free_frac=0.15)
        data = mon.sample()
        msg = mon.format_alert(data)
        assert msg is not None
        assert "WARN" in msg and "15% free" in msg
