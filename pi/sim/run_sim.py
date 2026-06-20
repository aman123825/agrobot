#!/usr/bin/env python3
"""Standalone simulation runner for the AgroBot rover.

Instantiates the rover model and sensor simulation, runs for N steps, and
prints state/telemetry each step. Optionally sends signed commands to exercise
the serial_sim path.

Usage:
    AGRO_LINK_KEY=<hex_key> python3 sim/run_sim.py --steps 10 --dt 0.1 --verbose
"""
from __future__ import annotations

import argparse
import hashlib
import hmac as hmac_mod
import json
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sim.rover_model import RoverSim  # noqa: E402
from sim.sensor_sim import SensorSim, Obstacle  # noqa: E402
from sim.serial_sim import SimSerial  # noqa: E402

_KEY = os.getenv("AGRO_LINK_KEY", "").encode()
_TRUNC_HEX = 32


def _sign(command: str, counter: int) -> str:
    """Create a signed envelope for a command."""
    msg = f"v1|{counter}|{command}"
    tag = hmac_mod.new(_KEY, msg.encode(), hashlib.sha256).hexdigest()[:_TRUNC_HEX]
    return f"{msg}|{tag}"


def _demo_commands() -> list[str]:
    """Return a sequence of commands to exercise the rover."""
    return ["FWD", "FWD", "LEFT", "FWD", "SETPWM 200 150", "STOP", "PING", "DOSE", "RESUME", "FWD"]


def main() -> None:
    parser = argparse.ArgumentParser(description="AgroBot simulation runner")
    parser.add_argument("--steps", type=int, default=10, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.1, help="Time step in seconds")
    parser.add_argument("--verbose", action="store_true", help="Print detailed output each step")
    args = parser.parse_args()

    # Set up rover and sensors
    rover = RoverSim(noise_linear=0.005, noise_angular=0.002)
    obstacles = [Obstacle(cx=3.0, cy=0.5, radius=0.3)]
    sensors = SensorSim(obstacles=obstacles)
    serial = SimSerial(rover=rover)
    serial.open()

    commands = _demo_commands()
    counter = int(time.time() * 1000)

    print(f"=== AgroBot Simulation: {args.steps} steps, dt={args.dt}s ===")
    print()

    for i in range(args.steps):
        # Pick a command (cycle through demo commands)
        cmd = commands[i % len(commands)]
        counter += 1
        envelope = _sign(cmd, counter)

        # Send via simulated serial
        serial.write(f"{envelope}\n".encode())
        response = serial.readline().decode(errors="ignore").strip()

        # Advance physics
        rover.step(args.dt)

        # Generate telemetry
        x, y, theta = rover.pose
        npk = sensors.npk_payload()
        gps = sensors.gps_payload(x, y)
        status = sensors.status_payload(x, y, theta)

        if args.verbose:
            print(f"--- Step {i + 1}/{args.steps} ---")
            print(f"  Command:  {cmd}")
            print(f"  Response: {response}")
            print(f"  Pose:     x={x:.4f} y={y:.4f} theta={theta:.4f} rad")
            print(f"  Velocity: left={rover.v_left:.3f} right={rover.v_right:.3f} m/s")
            print(f"  NPK:      {json.dumps(npk)}")
            print(f"  GPS:      {json.dumps(gps)}")
            print(f"  Status:   {json.dumps(status)}")
            print()
        else:
            print(f"[{i + 1:3d}] cmd={cmd:<16s} pose=({x:.3f}, {y:.3f}, {theta:.3f})")

    serial.close()
    print("=== Simulation complete ===")


if __name__ == "__main__":
    main()
