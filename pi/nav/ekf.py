"""Pose EKF fusing wheel odometry + IMU yaw-rate (prediction) with GPS (update).

State: [px, py, theta] in the local tangent plane (meters, radians).
- predict(v, omega, dt): differential-drive motion model with Jacobian.
- update_gps(zx, zy, var): corrects position from a GPS fix (in local meters).

Pure Python (no numpy) so it runs and unit-tests anywhere. The GPS measurement
is 2D, so the innovation covariance is a 2x2 - cheap and numerically stable.
"""
from __future__ import annotations

import math


def _mat_mul(a, b):
    rows, inner, cols = len(a), len(b), len(b[0])
    out = [[0.0] * cols for _ in range(rows)]
    for i in range(rows):
        for k in range(inner):
            aik = a[i][k]
            if aik == 0.0:
                continue
            for j in range(cols):
                out[i][j] += aik * b[k][j]
    return out


def _transpose(a):
    return [list(col) for col in zip(*a)]


def _inv2(m):
    det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
    if abs(det) < 1e-12:
        det = 1e-12
    inv = 1.0 / det
    return [[m[1][1] * inv, -m[0][1] * inv], [-m[1][0] * inv, m[0][0] * inv]]


class PoseEKF:
    def __init__(self, q_pos: float = 0.01, q_theta: float = 0.001):
        self.x = [0.0, 0.0, 0.0]  # px, py, theta
        self.P = [[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]]
        self.Q = [[q_pos, 0, 0], [0, q_pos, 0], [0, 0, q_theta]]

    def set_state(self, px: float, py: float, theta: float) -> None:
        self.x = [px, py, theta]

    def predict(self, v: float, omega: float, dt: float) -> None:
        px, py, th = self.x
        self.x = [
            px + v * math.cos(th) * dt,
            py + v * math.sin(th) * dt,
            th + omega * dt,
        ]
        f = [
            [1.0, 0.0, -v * math.sin(th) * dt],
            [0.0, 1.0, v * math.cos(th) * dt],
            [0.0, 0.0, 1.0],
        ]
        # P = F P F^T + Q
        fp = _mat_mul(f, self.P)
        fpft = _mat_mul(fp, _transpose(f))
        self.P = [[fpft[i][j] + self.Q[i][j] for j in range(3)] for i in range(3)]

    def update_gps(self, zx: float, zy: float, var: float = 1.0) -> None:
        # H selects px, py.  y = z - Hx
        yk = [zx - self.x[0], zy - self.x[1]]
        # S = H P H^T + R  (top-left 2x2 of P, plus measurement noise)
        s = [
            [self.P[0][0] + var, self.P[0][1]],
            [self.P[1][0], self.P[1][1] + var],
        ]
        s_inv = _inv2(s)
        # K = P H^T S^-1  -> P[:, :2] (3x2) times S^-1 (2x2)
        pht = [[self.P[i][0], self.P[i][1]] for i in range(3)]  # 3x2
        k = _mat_mul(pht, s_inv)  # 3x2
        # x = x + K y
        for i in range(3):
            self.x[i] += k[i][0] * yk[0] + k[i][1] * yk[1]
        # P = (I - K H) P ; KH is 3x3 with K in the first two columns
        kh = [[k[i][0], k[i][1], 0.0] for i in range(3)]
        ikh = [[(1.0 if i == j else 0.0) - kh[i][j] for j in range(3)] for i in range(3)]
        self.P = _mat_mul(ikh, self.P)

    def set_heading(self, theta: float) -> None:
        """Hard-set heading from an absolute source (e.g. fused IMU yaw)."""
        self.x[2] = theta

    @property
    def pose(self) -> tuple[float, float, float]:
        return (self.x[0], self.x[1], self.x[2])
