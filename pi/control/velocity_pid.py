"""Closed-loop velocity control.

A per-side PID converts a target velocity (mm/s) + measured encoder velocity
into a motor PWM duty (-255..255), which the orchestrator sends to the ESP32 as
`SETPWM <left> <right>`. This replaces open-loop PWM with true velocity control
for straight rows and repeatable seed-drop spacing.

Pure logic (no hardware), so it is fully unit-testable on a host.
"""
from __future__ import annotations


class PID:
    def __init__(self, kp: float, ki: float, kd: float, out_limit: float = 255.0,
                 i_limit: float = 200.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.out_limit = out_limit
        self.i_limit = i_limit
        self._i = 0.0
        self._prev_err = 0.0

    def reset(self) -> None:
        self._i = 0.0
        self._prev_err = 0.0

    @staticmethod
    def _clamp(v: float, lo: float, hi: float) -> float:
        return lo if v < lo else min(v, hi)

    def update(self, target: float, measured: float, dt: float) -> float:
        if dt <= 0:
            return 0.0
        err = target - measured
        self._i = self._clamp(self._i + err * dt, -self.i_limit, self.i_limit)
        d = (err - self._prev_err) / dt
        self._prev_err = err
        out = self.kp * err + self.ki * self._i + self.kd * d
        return self._clamp(out, -self.out_limit, self.out_limit)


class DiffDriveController:
    """Holds one PID per side and produces a SETPWM command string."""

    def __init__(self, kp: float = 0.6, ki: float = 0.8, kd: float = 0.02):
        self.left = PID(kp, ki, kd)
        self.right = PID(kp, ki, kd)

    def reset(self) -> None:
        self.left.reset()
        self.right.reset()

    def compute(self, target_l: float, target_r: float,
                meas_l: float, meas_r: float, dt: float) -> tuple[int, int]:
        pwm_l = int(round(self.left.update(target_l, meas_l, dt)))
        pwm_r = int(round(self.right.update(target_r, meas_r, dt)))
        return (pwm_l, pwm_r)

    def command(self, target_l: float, target_r: float,
                meas_l: float, meas_r: float, dt: float) -> str:
        pwm_l, pwm_r = self.compute(target_l, target_r, meas_l, meas_r, dt)
        return f"SETPWM {pwm_l} {pwm_r}"
