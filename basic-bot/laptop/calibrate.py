#!/usr/bin/env python3
"""AgriRover basic-bot calibration helper.

Reads live telemetry over USB serial and computes the exact calibration
constants to paste into the firmware. It MEASURES values from your hardware -
it never guesses them.

Covers the two constants that depend on your specific parts:
  * Soil moisture   -> MOIST_CAL_MV[] / MOIST_CAL_PCT[]  (firmware/src/sensors.cpp)
  * Battery divider -> VBAT_DIVIDER_RATIO                 (firmware/include/config.h)

(NPK register order and the advanced-bot current/thermal constants need a bench
rig and are covered in docs/hardware-bringup-checklist.md.)

Usage:
    python calibrate.py                     # auto-detect the port
    python calibrate.py --port COM5
    python calibrate.py --only battery
"""
import argparse
import json
import statistics
import sys
import time

import serial
from serial.tools import list_ports

USB_SERIAL_HINTS = ("CP210", "CH340", "CH910", "FTDI", "USB SERIAL", "USB-SERIAL")
DEFAULT_VBAT_RATIO = 10.0 / (39.0 + 10.0)   # 39k/10k divider (matches config.h)


def find_port():
    candidates = list(list_ports.comports())
    for p in candidates:
        desc = f"{p.description} {p.manufacturer or ''}".upper()
        if any(h in desc for h in USB_SERIAL_HINTS):
            return p.device
    if len(candidates) == 1:
        return candidates[0].device
    names = ", ".join(p.device for p in candidates) or "none found"
    sys.exit(f"Could not auto-detect the ESP32 port (ports: {names}). "
             f"Pass it explicitly with --port.")


def collect(ser, field, seconds):
    """Average a telemetry field over a fresh time window. Returns (mean, n)."""
    ser.reset_input_buffer()   # drop anything buffered during the prompt
    deadline = time.time() + seconds
    vals = []
    while time.time() < deadline:
        raw = ser.readline()
        if not raw:
            continue
        line = raw.decode(errors="replace").strip()
        if not line.startswith("TLM "):
            continue
        try:
            t = json.loads(line[4:])
        except json.JSONDecodeError:
            continue
        v = t.get(field)
        if isinstance(v, (int, float)):
            vals.append(float(v))
    if not vals:
        return None, 0
    return statistics.fmean(vals), len(vals)


def prompt(msg):
    try:
        input(msg)
    except (EOFError, KeyboardInterrupt):
        sys.exit("\nAborted.")


def calibrate_moisture(ser, seconds):
    print("\n=== Soil moisture calibration ===")
    print("Capacitive probes read a LOWER voltage when wetter.")
    prompt("1) Hold the probe in DRY AIR (clean and dry), then press Enter...")
    dry_mv, nd = collect(ser, "moist_mv", seconds)
    if dry_mv is None:
        print("  No telemetry received - is the rover streaming TLM? Skipping.")
        return
    print(f"   dry = {dry_mv:.0f} mV  (n={nd})")

    prompt("2) Submerge the probe tip in WATER, then press Enter...")
    wet_mv, nw = collect(ser, "moist_mv", seconds)
    if wet_mv is None:
        print("  No telemetry received. Skipping.")
        return
    print(f"   wet = {wet_mv:.0f} mV  (n={nw})")

    if wet_mv >= dry_mv:
        print("  ! WARNING: wet >= dry, which is backwards for a capacitive probe.")
        print("    Check it is powered from 3.3V (not 5V) and wired to GPIO34.")
        return
    w, d = int(round(wet_mv)), int(round(dry_mv))
    m = int(round((wet_mv + dry_mv) / 2.0))
    print("\n  Paste into firmware/src/sensors.cpp (ascending mV = wet..dry):")
    print(f"  static const float MOIST_CAL_MV[]  = {{ {w}.0f, {m}.0f, {d}.0f }};")
    print("  static const float MOIST_CAL_PCT[] = { 100.0f,  50.0f,   0.0f   };")


def calibrate_battery(ser, seconds, old_ratio):
    print("\n=== Battery divider calibration ===")
    rep, n = collect(ser, "batt_v", seconds)
    if rep is None:
        print("  No telemetry received. Skipping.")
        return
    print(f"   firmware reports batt_v = {rep:.2f} V  (n={n}, ratio={old_ratio:.5f})")
    raw = input("   Measure the pack with a multimeter, enter volts (blank=skip): ").strip()
    if not raw:
        print("   Skipped.")
        return
    try:
        true_v = float(raw)
    except ValueError:
        print("   Not a number. Skipped.")
        return
    if true_v <= 0:
        print("   Must be > 0. Skipped.")
        return
    # batt_v = v_adc / ratio  =>  ratio_new = v_adc / V_true = ratio_old * rep / V_true
    new_ratio = old_ratio * rep / true_v
    err = (rep - true_v) / true_v * 100.0
    print(f"   reported error before fix: {err:+.1f}%")
    print("\n  Paste into firmware/include/config.h:")
    print(f"  #define VBAT_DIVIDER_RATIO  ({new_ratio:.6f}f)   // calibrated {time.strftime('%Y-%m-%d')}")


def main():
    ap = argparse.ArgumentParser(description="AgriRover basic-bot calibration helper")
    ap.add_argument("--port", help="serial port (default: auto-detect)")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--seconds", type=float, default=3.0, help="averaging window per capture")
    ap.add_argument("--vbat-ratio", type=float, default=DEFAULT_VBAT_RATIO,
                    help="current VBAT_DIVIDER_RATIO from config.h")
    ap.add_argument("--only", choices=["moisture", "battery"], help="run just one step")
    args = ap.parse_args()

    port = args.port or find_port()
    print(f"Connecting to {port} @ {args.baud} ...")
    try:
        ser = serial.Serial(port, args.baud, timeout=0.2)
    except serial.SerialException as exc:
        sys.exit(f"Could not open {port}: {exc}")

    time.sleep(0.5)
    probe, _ = collect(ser, "moist_mv", 2.0)
    if probe is None:
        print("! No 'TLM' telemetry seen yet - make sure the firmware is running. "
              "Continuing anyway...")

    try:
        if args.only in (None, "moisture"):
            calibrate_moisture(ser, args.seconds)
        if args.only in (None, "battery"):
            calibrate_battery(ser, args.seconds, args.vbat_ratio)
    finally:
        ser.close()
    print("\nDone. After editing the constants, re-flash: cd ../firmware && pio run -t upload")


if __name__ == "__main__":
    main()
