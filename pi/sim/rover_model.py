"""Differential-drive kinematic model for the simulated rover.

Tracks (x, y, theta) pose in a local tangent plane (meters / radians) and
accepts the same commands the real ESP32 firmware processes. Configurable
Gaussian noise on motion for realism.
"""
from __future__ import annotations

import math
import random


# Default physical parameters
_WHEEL_SEPARATION = 0.30  # meters between wheel centres
_MAX_SPEED = 0.5  # m/s at full PWM (255)
_DEFAULT_PWM = 180  # PWM used for open-loop FWD/BACK/LEFT/RIGHT


class RoverSim:
    """Simulated differential-drive rover.

    Attributes:
        x, y: position in the local plane (meters)
        theta: heading (radians, 0 = east, pi/2 = north)
        v_left, v_right: current wheel velocities (m/s)
    """

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        theta: float = 0.0,
        noise_linear: float = 0.01,
        noise_angular: float = 0.005,
        wheel_sep: float = _WHEEL_SEPARATION,
        max_speed: float = _MAX_SPEED,
    ):
        self.x = x
        self.y = y
        self.theta = theta
        self.v_left = 0.0
        self.v_right = 0.0
        self.noise_linear = noise_linear
        self.noise_angular = noise_angular
        self.wheel_sep = wheel_sep
        self.max_speed = max_speed
        self._default_pwm = _DEFAULT_PWM

    @property
    def pose(self) -> tuple[float, float, float]:
        """Current (x, y, theta)."""
        return (self.x, self.y, self.theta)

    # ------------------------------------------------------------------
    # PWM to velocity conversion
    # ------------------------------------------------------------------

    def _pwm_to_vel(self, pwm: int) -> float:
        """Map a PWM value (-255..255) to a wheel velocity (m/s)."""
        clamped = max(-255, min(255, pwm))
        return (clamped / 255.0) * self.max_speed

    # ------------------------------------------------------------------
    # Command processing
    # ------------------------------------------------------------------

    def apply_command(self, cmd: str) -> None:
        """Apply a command string (same vocabulary as the ESP32 firmware)."""
        parts = cmd.strip().split()
        if not parts:
            return
        verb = parts[0].upper()

        if verb == "SETPWM" and len(parts) >= 3:
            self.v_left = self._pwm_to_vel(int(parts[1]))
            self.v_right = self._pwm_to_vel(int(parts[2]))
        elif verb == "FWD":
            self.v_left = self._pwm_to_vel(self._default_pwm)
            self.v_right = self._pwm_to_vel(self._default_pwm)
        elif verb == "BACK":
            self.v_left = self._pwm_to_vel(-self._default_pwm)
            self.v_right = self._pwm_to_vel(-self._default_pwm)
        elif verb == "LEFT":
            self.v_left = self._pwm_to_vel(-self._default_pwm)
            self.v_right = self._pwm_to_vel(self._default_pwm)
        elif verb == "RIGHT":
            self.v_left = self._pwm_to_vel(self._default_pwm)
            self.v_right = self._pwm_to_vel(-self._default_pwm)
        elif verb in ("STOP", "DRIVE_STOP"):
            self.v_left = 0.0
            self.v_right = 0.0
        elif verb == "RESUME":
            # Resume just re-enables motion; keep last velocities or default fwd
            if self.v_left == 0.0 and self.v_right == 0.0:
                self.v_left = self._pwm_to_vel(self._default_pwm)
                self.v_right = self._pwm_to_vel(self._default_pwm)
        elif verb in ("DOSE", "PING", "PUMP_DISABLE", "PUMP_ENABLE",
                      "PAUSE_IRRIGATION", "RESUME_IRRIGATION"):
            # These commands do not affect motion
            pass
        # Unknown commands are silently ignored (matches firmware behaviour)

    # ------------------------------------------------------------------
    # Physics step
    # ------------------------------------------------------------------

    def step(self, dt: float) -> None:
        """Advance the simulation by dt seconds using diff-drive kinematics.

        v = (v_left + v_right) / 2
        omega = (v_right - v_left) / wheel_sep
        x += v * cos(theta) * dt
        y += v * sin(theta) * dt
        theta += omega * dt
        """
        v = (self.v_left + self.v_right) / 2.0
        omega = (self.v_right - self.v_left) / self.wheel_sep

        # Add noise
        if self.noise_linear > 0:
            v += random.gauss(0, self.noise_linear)
        if self.noise_angular > 0:
            omega += random.gauss(0, self.noise_angular)

        self.x += v * math.cos(self.theta) * dt
        self.y += v * math.sin(self.theta) * dt
        self.theta += omega * dt

        # Normalize theta to [-pi, pi]
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))
