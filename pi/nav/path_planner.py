"""Boustrophedon (snake) coverage planner + cross-track guidance.

Generates parallel passes over a rectangular field (in local meters) spaced by
the working width, and provides cross-track-error and target-heading helpers so
the controller can follow the row accurately. All pure functions - unit-testable.
"""
from __future__ import annotations

import math


def boustrophedon(width_m: float, length_m: float, row_spacing_m: float,
                  origin: tuple[float, float] = (0.0, 0.0)) -> list[tuple[float, float]]:
    """Snake waypoints covering a width x length rectangle from `origin`.

    Rows run along +Y (length); successive rows step by row_spacing in +X and
    alternate direction. Returns an ordered list of (x, y) waypoints.
    """
    if row_spacing_m <= 0 or width_m <= 0 or length_m <= 0:
        return []
    ox, oy = origin
    n_rows = int(width_m // row_spacing_m) + 1
    pts: list[tuple[float, float]] = []
    for i in range(n_rows):
        x = ox + i * row_spacing_m
        if i % 2 == 0:
            pts.append((x, oy))
            pts.append((x, oy + length_m))
        else:
            pts.append((x, oy + length_m))
            pts.append((x, oy))
    return pts


def cross_track_error(p_prev: tuple[float, float], p_next: tuple[float, float],
                      p: tuple[float, float]) -> float:
    """Signed perpendicular distance of point p from the line p_prev->p_next.

    Positive = left of the path direction, negative = right. Used to steer the
    rover back onto the row.
    """
    ax, ay = p_prev
    bx, by = p_next
    px, py = p
    dx, dy = bx - ax, by - ay
    seg = math.hypot(dx, dy)
    if seg < 1e-9:
        return math.hypot(px - ax, py - ay)
    # 2D cross product of (B-A) x (P-A) normalized by segment length.
    return ((dx) * (py - ay) - (dy) * (px - ax)) / seg


def target_heading(p: tuple[float, float], goal: tuple[float, float]) -> float:
    """Bearing (radians) from current point p to the goal waypoint."""
    return math.atan2(goal[1] - p[1], goal[0] - p[0])


def heading_error(target: float, current: float) -> float:
    """Smallest signed angle (radians) from current heading to target."""
    err = target - current
    while err > math.pi:
        err -= 2 * math.pi
    while err < -math.pi:
        err += 2 * math.pi
    return err


def reached(p: tuple[float, float], goal: tuple[float, float], tol_m: float = 0.3) -> bool:
    return math.hypot(goal[0] - p[0], goal[1] - p[1]) <= tol_m
