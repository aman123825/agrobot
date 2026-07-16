#!/usr/bin/env python3
"""AgriRover basic-bot laptop console: keyboard teleop + live telemetry.

The ESP32 is connected over USB. Hold a movement key to drive - the firmware's
dead-man timer stops the motors when you release it (OS key auto-repeat keeps
the command refreshed while held).

Usage:
    python rover.py                     # auto-detect the serial port
    python rover.py --port COM5        # explicit port (Windows)
    python rover.py --port /dev/ttyUSB0 --log telemetry.csv

Keys:
    w/s/a/d  forward / back / spin left / spin right (hold to drive)
    space    stop motors
    x        EMERGENCY HALT (latched)     r  resume after halt
    f        run dosing sequence          u  toggle pump disable
    + / -    speed up / down              t  request telemetry now
    h        help                         q  quit
"""
import argparse
import csv
import json
import sys
import threading
import time

import serial
from serial.tools import list_ports

USB_SERIAL_HINTS = ("CP210", "CH340", "CH910", "FTDI", "USB SERIAL", "USB-SERIAL")

CSV_FIELDS = [
    "time_iso", "up_ms", "state", "batt_v", "batt_pct", "moist_pct", "moist_mv",
    "air_c", "air_rh", "dist_l", "dist_c", "dist_r", "chip_c",
    "npk_valid", "n", "p", "k", "ph", "ec", "soil_c", "soil_moist",
]


def find_port():
    """Pick the first port that looks like a USB-serial adapter."""
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


class Getch:
    """Non-blocking single-key reader (Windows + POSIX)."""

    def __init__(self):
        self.windows = sys.platform == "win32"
        if not self.windows:
            import termios
            import tty
            self._termios = termios
            self._fd = sys.stdin.fileno()
            self._saved = termios.tcgetattr(self._fd)
            tty.setcbreak(self._fd)

    def get(self, timeout=0.05):
        """Return one char, or None if nothing pressed within timeout."""
        if self.windows:
            import msvcrt
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if msvcrt.kbhit():
                    return msvcrt.getwch()
                time.sleep(0.005)
            return None
        import select
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        return sys.stdin.read(1) if r else None

    def restore(self):
        if not self.windows:
            self._termios.tcsetattr(self._fd, self._termios.TCSADRAIN, self._saved)


class RoverConsole:
    def __init__(self, port, baud, log_path=None):
        self.ser = serial.Serial(port, baud, timeout=0.2)
        self.running = True
        self.csv_writer = None
        self.csv_file = None
        if log_path:
            self.csv_file = open(log_path, "a", newline="")
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=CSV_FIELDS)
            if self.csv_file.tell() == 0:
                self.csv_writer.writeheader()
        self.reader = threading.Thread(target=self._read_loop, daemon=True)
        self.reader.start()

    def send(self, cmd):
        self.ser.write((cmd + "\n").encode())

    # ---- incoming lines ----
    def _read_loop(self):
        while self.running:
            try:
                raw = self.ser.readline()
            except (serial.SerialException, OSError):
                print("\n[serial] connection lost")
                self.running = False
                return
            if not raw:
                continue
            line = raw.decode(errors="replace").strip()
            if not line:
                continue
            if line.startswith("TLM "):
                self._handle_tlm(line[4:])
            else:
                print(f"[rover] {line}")

    def _handle_tlm(self, payload):
        try:
            t = json.loads(payload)
        except json.JSONDecodeError:
            print(f"[rover] bad TLM: {payload}")
            return
        npk = t.get("npk")
        npk_str = (f"N/P/K {npk['n']}/{npk['p']}/{npk['k']} pH {npk['ph']}"
                   if npk else "npk --")
        dl = t.get("dist_l")
        dc = t.get("dist_c")
        dr = t.get("dist_r")
        dl_s = f"{dl:.0f}" if dl is not None else "--"
        dc_s = f"{dc:.0f}" if dc is not None else "--"
        dr_s = f"{dr:.0f}" if dr is not None else "--"
        air = t.get("air_c")
        air_str = f"{air:.0f}C" if air is not None else "--"
        print(f"[TLM] {t.get('state','?'):8s} "
              f"batt {t.get('batt_v', 0):.2f}V ({t.get('batt_pct', 0):.0f}%)  "
              f"moist {t.get('moist_pct', 0):.0f}%  air {air_str}  "
              f"dist L{dl_s}/C{dc_s}/R{dr_s}cm  {npk_str}")
        if self.csv_writer:
            row = {
                "time_iso": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "up_ms": t.get("up_ms"), "state": t.get("state"),
                "batt_v": t.get("batt_v"), "batt_pct": t.get("batt_pct"),
                "moist_pct": t.get("moist_pct"), "moist_mv": t.get("moist_mv"),
                "air_c": t.get("air_c"), "air_rh": t.get("air_rh"),
                "dist_l": t.get("dist_l"), "dist_c": t.get("dist_c"),
                "dist_r": t.get("dist_r"), "chip_c": t.get("chip_c"),
                "npk_valid": bool(npk),
            }
            if npk:
                row.update({"n": npk.get("n"), "p": npk.get("p"), "k": npk.get("k"),
                            "ph": npk.get("ph"), "ec": npk.get("ec"),
                            "soil_c": npk.get("soil_c"),
                            "soil_moist": npk.get("soil_moist")})
            self.csv_writer.writerow(row)
            self.csv_file.flush()

    def close(self):
        self.running = False
        try:
            self.send("DRIVE_STOP")
            time.sleep(0.1)
        except (serial.SerialException, OSError):
            pass
        self.ser.close()
        if self.csv_file:
            self.csv_file.close()


def main():
    ap = argparse.ArgumentParser(description="AgriRover basic-bot console")
    ap.add_argument("--port", help="serial port (default: auto-detect)")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--log", help="append telemetry to this CSV file")
    args = ap.parse_args()

    port = args.port or find_port()
    print(f"Connecting to {port} @ {args.baud} ... (h = help, q = quit)")
    console = RoverConsole(port, args.baud, args.log)

    speed = 180
    pump_disabled = False
    keymap = {
        "w": "FWD", "s": "BACK", "a": "LEFT", "d": "RIGHT",
        " ": "DRIVE_STOP", "x": "STOP", "r": "RESUME",
        "f": "DOSE", "t": "STATUS", "p": "PING",
    }

    getch = Getch()
    try:
        while console.running:
            key = getch.get()
            if key is None:
                continue
            key = key.lower()
            if key == "q":
                break
            if key == "h":
                print(__doc__)
            elif key in ("+", "="):
                speed = min(255, speed + 15)
                console.send(f"SPEED {speed}")
                print(f"[you] speed -> {speed}")
            elif key == "-":
                speed = max(60, speed - 15)
                console.send(f"SPEED {speed}")
                print(f"[you] speed -> {speed}")
            elif key == "u":
                pump_disabled = not pump_disabled
                console.send("PUMP_DISABLE" if pump_disabled else "PUMP_ENABLE")
            elif key in keymap:
                console.send(keymap[key])
    except KeyboardInterrupt:
        pass
    finally:
        getch.restore()
        console.close()
        print("\nBye - motors stopped.")


if __name__ == "__main__":
    main()
