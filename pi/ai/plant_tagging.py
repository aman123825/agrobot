"""Geo-tag a detected plant from its image position + rover pose.

Because the final fix is visual (the camera sees the actual plant), this
localizes plants to ~10-20 cm relative even though the Neo-6M absolute fix is
~1 m. Uses a pinhole camera + flat-ground assumption.

The geometry helpers are pure functions, unit-testable on a host.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from nav.geo import local_to_latlng


class CameraGeometry:
    def __init__(self, height_m: float = 0.30, pitch_deg: float = 15.0,
                 hfov_deg: float = 160.0, vfov_deg: float = 100.0):
        self.height_m = height_m       # lens height above ground
        self.pitch_deg = pitch_deg     # downward tilt below horizontal
        self.hfov_deg = hfov_deg
        self.vfov_deg = vfov_deg


def pixel_to_ground(u: float, v: float, img_w: int, img_h: int,
                    geom: CameraGeometry) -> tuple[float, float] | None:
    """Project image pixel (u,v) to ground offset (forward_m, lateral_m).

    Returns None if the ray points at/above the horizon (no ground hit).
    +lateral = to the camera's right.
    """
    ang_x = (u / img_w - 0.5) * geom.hfov_deg          # left/right angle (deg)
    ang_y = (v / img_h - 0.5) * geom.vfov_deg          # +down as v increases
    depression_deg = geom.pitch_deg + ang_y
    if depression_deg <= 0.5:
        return None                                     # near/above horizon
    forward = geom.height_m / math.tan(math.radians(depression_deg))
    lateral = forward * math.tan(math.radians(ang_x))
    return (forward, lateral)


def tag_plant(bbox: tuple[float, float, float, float], img_w: int, img_h: int,
              geom: CameraGeometry, rover_pose: tuple[float, float, float],
              datum: tuple[float, float]) -> tuple[float, float] | None:
    """Return (lat, lng) of a detection bbox, or None if not on the ground."""
    x1, y1, x2, y2 = bbox
    u = (x1 + x2) / 2.0
    v = max(y1, y2)                 # bottom of the box ~ where the plant meets soil
    ground = pixel_to_ground(u, v, img_w, img_h, geom)
    if ground is None:
        return None
    forward, lateral = ground
    px, py, theta = rover_pose
    # Camera frame -> world (rover heading theta; lateral is +right = -90 deg).
    wx = px + forward * math.cos(theta) + lateral * math.cos(theta - math.pi / 2)
    wy = py + forward * math.sin(theta) + lateral * math.sin(theta - math.pi / 2)
    return local_to_latlng(wx, wy, datum[0], datum[1])
