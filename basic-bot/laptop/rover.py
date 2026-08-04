#!/usr/bin/env python3
"""AgriRover basic-bot laptop console: Tkinter GUI + live telemetry.

Usage:
    python rover.py                     # auto-detect the serial port
    python rover.py --port COM5         # explicit port (Windows)
    python rover.py --cam-url http://192.168.4.2/   # ESP32-CAM on rover WiFi
"""
import argparse
import csv
import json
import sys
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import ttk

import serial
from serial.tools import list_ports

USB_SERIAL_HINTS = ("CP210", "CH340", "CH910", "FTDI", "USB SERIAL", "USB-SERIAL")

CSV_FIELDS = [
    "time_iso", "up_ms", "state", "batt_v", "batt_pct", "moist_pct", "moist_mv",
    "air_c", "air_rh", "dist_l", "dist_c", "dist_r", "chip_c",
    "npk_valid", "n", "p", "k", "ph", "ec", "soil_c", "soil_moist",
]


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


class RoverConsole:
    def __init__(self, port, baud, log_path=None, on_telemetry=None):
        self.ser = serial.Serial(port, baud, timeout=0.2)
        self.running = True
        self.on_telemetry = on_telemetry
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

    def _read_loop(self):
        while self.running:
            try:
                raw = self.ser.readline()
            except (serial.SerialException, OSError):
                if self.on_telemetry:
                    self.on_telemetry("[serial] connection lost")
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
                if self.on_telemetry:
                    self.on_telemetry(f"[rover] {line}")

    def _handle_tlm(self, payload):
        try:
            t = json.loads(payload)
        except json.JSONDecodeError:
            return
        npk = t.get("npk")
        npk_str = (f"N/P/K {npk['n']}/{npk['p']}/{npk['k']} pH {npk['ph']}" if npk else "npk --")
        dl = f"{t.get('dist_l', 0):.0f}" if t.get("dist_l") is not None else "--"
        dc = f"{t.get('dist_c', 0):.0f}" if t.get("dist_c") is not None else "--"
        dr = f"{t.get('dist_r', 0):.0f}" if t.get("dist_r") is not None else "--"
        air = f"{t.get('air_c', 0):.0f}C" if t.get("air_c") is not None else "--"
        
        msg = (f"[TLM] {t.get('state','?'):8s} "
               f"batt {t.get('batt_v', 0):.2f}V ({t.get('batt_pct', 0):.0f}%)  "
               f"moist {t.get('moist_pct', 0):.0f}%  air {air}  "
               f"dist L{dl}/C{dc}/R{dr}cm  {npk_str}")
               
        if self.on_telemetry:
            self.on_telemetry(msg)

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
        except:
            pass
        self.ser.close()
        if self.csv_file:
            self.csv_file.close()


class App:
    def __init__(self, root, port, baud, log, cam_url="http://192.168.4.2/"):
        self.root = root
        self.root.title(f"AgriRover Console - {port}")
        self.root.geometry("800x600")
        
        self.console = RoverConsole(port, baud, log, self.on_telemetry)
        
        self.speed = 180
        self.pump_disabled = False
        self.cam_url = cam_url
        
        # Drive-command tracking. We drive on real KeyPress/KeyRelease rather
        # than relying on the OS key auto-repeat, so holding a key gives smooth,
        # continuous motion. (The old 0.2s repeat window stuttered, and if the
        # OS key-repeat delay was long it could send no drive command at all.)
        self.held_dirs = set()        # direction commands currently held down
        self._pending_release = {}    # after() ids, to debounce OS auto-repeat
        self.mouse_cmd = None         # set while a D-pad button is held
        self.last_sent_cmd = None
        
        self._build_ui()
        
        # Keyboard teleop: press to start moving, release to stop.
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.focus_set()
        
        # Start command loop
        self.send_commands_loop()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Telemetry Display
        self.text_area = tk.Text(main_frame, height=20, bg="black", fg="lime", font=("Consolas", 10), state=tk.DISABLED)
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Control Frame
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.pack(fill=tk.X)
        
        # D-PAD
        dpad = ttk.Frame(ctrl_frame)
        dpad.pack(side=tk.LEFT, padx=20)
        
        btn_w = tk.Label(dpad, text="W (Forward)", width=12, height=2, relief="raised", bg="lightgray")
        btn_w.grid(row=0, column=1, padx=2, pady=2)
        btn_a = tk.Label(dpad, text="A (Left)", width=12, height=2, relief="raised", bg="lightgray")
        btn_a.grid(row=1, column=0, padx=2, pady=2)
        btn_s = tk.Label(dpad, text="S (Back)", width=12, height=2, relief="raised", bg="lightgray")
        btn_s.grid(row=1, column=1, padx=2, pady=2)
        btn_d = tk.Label(dpad, text="D (Right)", width=12, height=2, relief="raised", bg="lightgray")
        btn_d.grid(row=1, column=2, padx=2, pady=2)
        
        self._bind_btn(btn_w, "FWD")
        self._bind_btn(btn_s, "BACK")
        self._bind_btn(btn_a, "LEFT")
        self._bind_btn(btn_d, "RIGHT")
        
        # Action Buttons
        act_frame = ttk.Frame(ctrl_frame)
        act_frame.pack(side=tk.LEFT, padx=50)
        
        btn_stop = tk.Button(act_frame, text="STOP (Space)", width=15, height=2, bg="red", fg="white", command=self.stop)
        btn_stop.pack(pady=2)
        
        btn_dose = tk.Button(act_frame, text="DOSE (F)", width=15, height=2, bg="blue", fg="white", command=lambda: self.console.send("DOSE"))
        btn_dose.pack(pady=2)
        
        btn_cam = tk.Button(act_frame, text="Camera (C)", width=15, height=2, bg="green", fg="white", command=self.open_camera)
        btn_cam.pack(pady=2)
        
        # Speed controls
        spd_frame = ttk.Frame(ctrl_frame)
        spd_frame.pack(side=tk.RIGHT, padx=20)
        
        self.lbl_speed = ttk.Label(spd_frame, text=f"Speed: {self.speed}", font=("Arial", 14, "bold"))
        self.lbl_speed.pack(pady=5)
        
        ttk.Button(spd_frame, text="Speed UP (+)", command=self.speed_up).pack(fill=tk.X)
        ttk.Button(spd_frame, text="Speed DOWN (-)", command=self.speed_down).pack(fill=tk.X)

    def _bind_btn(self, btn, cmd):
        def on_press(e):
            e.widget.config(bg="gray", relief="sunken")
            self.set_mouse_cmd(cmd)
        def on_release(e):
            e.widget.config(bg="lightgray", relief="raised")
            self.set_mouse_cmd(None)
        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)

    def set_mouse_cmd(self, cmd):
        self.mouse_cmd = cmd
        if not cmd:
            self.console.send("DRIVE_STOP")

    def speed_up(self):
        self.speed = min(255, self.speed + 15)
        self.console.send(f"SPEED {self.speed}")
        self.lbl_speed.config(text=f"Speed: {self.speed}")
        
    def speed_down(self):
        self.speed = max(60, self.speed - 15)
        self.console.send(f"SPEED {self.speed}")
        self.lbl_speed.config(text=f"Speed: {self.speed}")

    def stop(self):
        # Release any held direction and stop the motors immediately.
        self.held_dirs.clear()
        self.console.send("DRIVE_STOP")

    def toggle_pump(self):
        self.pump_disabled = not self.pump_disabled
        self.console.send("PUMP_DISABLE" if self.pump_disabled else "PUMP_ENABLE")

    def open_camera(self):
        # Opens the ESP32-CAM stream. The CAM joins the DevKit's
        # "AgriRover-Control" network at static IP 192.168.4.2.
        self.on_telemetry(f"[camera] opening {self.cam_url}")
        webbrowser.open(self.cam_url)

    # Movement keys (WASD + arrow keys) -> drive commands.
    DIR_KEYS = {
        'w': 'FWD',   'up': 'FWD',
        's': 'BACK',  'down': 'BACK',
        'a': 'LEFT',  'left': 'LEFT',
        'd': 'RIGHT', 'right': 'RIGHT',
    }

    def on_key_press(self, event):
        k = event.keysym.lower()
        if k in self.DIR_KEYS:
            cmd = self.DIR_KEYS[k]
            # Cancel a pending release: while a key is physically held the OS
            # can emit release+press pairs (auto-repeat); cancelling keeps us
            # driving instead of stuttering.
            aid = self._pending_release.pop(cmd, None)
            if aid is not None:
                self.root.after_cancel(aid)
            self.held_dirs.add(cmd)
            return
        # Discrete actions (idempotent, so auto-repeat re-firing is harmless).
        if k == 'space':
            self.stop()
        elif k == 'x':
            self.held_dirs.clear()
            self.console.send("STOP")        # latched emergency halt
        elif k == 'r':
            self.console.send("RESUME")      # clear the latched halt
        elif k == 'f':
            self.console.send("DOSE")
        elif k == 'u':
            self.toggle_pump()
        elif k == 't':
            self.console.send("STATUS")
        elif k == 'c':
            self.open_camera()
        elif k in ('plus', 'equal', 'kp_add'):
            self.speed_up()
        elif k in ('minus', 'kp_subtract'):
            self.speed_down()
        elif k == 'q':
            self.close()

    def on_key_release(self, event):
        k = event.keysym.lower()
        if k in self.DIR_KEYS:
            cmd = self.DIR_KEYS[k]
            # Defer the stop briefly; a matching KeyPress within the window
            # (auto-repeat) cancels it, so a held key keeps driving smoothly.
            self._pending_release[cmd] = self.root.after(
                60, lambda c=cmd: self.held_dirs.discard(c))

    def send_commands_loop(self):
        cmd = self.mouse_cmd
        
        # No mouse command? Use the highest-priority held keyboard direction.
        if not cmd and self.held_dirs:
            for c in ('FWD', 'BACK', 'LEFT', 'RIGHT'):
                if c in self.held_dirs:
                    cmd = c
                    break
            
        if cmd:
            self.console.send(cmd)
            self.last_sent_cmd = cmd
        else:
            if self.last_sent_cmd:
                self.console.send("DRIVE_STOP")
                self.last_sent_cmd = None
                
        self.root.after(100, self.send_commands_loop)

    def on_telemetry(self, msg):
        def append():
            self.text_area.config(state=tk.NORMAL)
            self.text_area.insert(tk.END, msg + "\n")
            self.text_area.see(tk.END)
            # Keep only last 100 lines
            lines = int(self.text_area.index('end-1c').split('.')[0])
            if lines > 100:
                self.text_area.delete("1.0", f"{lines-100}.0")
            self.text_area.config(state=tk.DISABLED)
        self.root.after(0, append)

    def close(self):
        self.console.close()
        self.root.destroy()


def main():
    ap = argparse.ArgumentParser(description="AgriRover basic-bot console")
    ap.add_argument("--port", help="serial port (default: auto-detect)")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--log", help="append telemetry to this CSV file")
    ap.add_argument("--cam-url", default="http://192.168.4.2/",
                    help="ESP32-CAM URL on AgriRover-Control (default: 192.168.4.2)")
    args = ap.parse_args()

    port = args.port or find_port()
    
    root = tk.Tk()
    app = App(root, port, args.baud, args.log, args.cam_url)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()


if __name__ == "__main__":
    main()
