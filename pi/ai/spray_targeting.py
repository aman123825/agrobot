"""Vision-guided aimed-spray targeting (FC-01).

Weeds grow in raised beds at variable height, so a fixed nozzle cannot reach
them. The camera + YOLOv8n already give the weed's bounding box; this module
converts that box (plus camera field-of-view and optional ToF depth) into the
pan/tilt angles that point the misting nozzle at the weed.

``aim_angles`` is a pure function, fully unit-testable without hardware.

Convention:
  * pan  > 0 -> aim to the camera's right; pan  < 0 -> left.
  * tilt > 0 -> aim downward (below the optical axis); tilt < 0 -> upward.
  * (0, 0) means the nozzle points straight along the optical axis.
Angles are clamped to a mechanical limit (default +/-80 deg) so a servo is
never commanded past its safe travel.
"""
from __future__ import annotations

PAN_LIMIT_DEG = 80.0
TILT_LIMIT_DEG = 80.0


def _clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def aim_angles(bbox: tuple[float, float, float, float], img_w: int, img_h: int,
               hfov_deg: float, vfov_deg: float,
               depth_m: float | None = None,
               pan_limit_deg: float = PAN_LIMIT_DEG,
               tilt_limit_deg: float = TILT_LIMIT_DEG) -> tuple[float, float]:
    """Return (pan_deg, tilt_deg) to point the nozzle at a detection bbox.

    Args:
        bbox: (x1, y1, x2, y2) pixel corners of the detection.
        img_w, img_h: frame size in pixels (must be > 0).
        hfov_deg, vfov_deg: camera horizontal / vertical field of view.
        depth_m: optional ToF distance to the target. It does not change the
            *angle* to the target centroid under a pinhole model, but it is
            accepted so callers can pass it (and future parallax/offset
            corrections can use it); a non-positive depth is ignored.
        pan_limit_deg, tilt_limit_deg: mechanical clamp for the servos.

    The target point is the horizontal centre of the box and its vertical
    centre. The pixel offset from the image centre is scaled by the per-pixel
    angular resolution (fov / dimension).
    """
    if img_w <= 0 or img_h <= 0:
        raise ValueError("img_w and img_h must be positive")
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2.0
    cy = (y1 + y2) / 2.0
    # Normalised offset from image centre, range about [-0.5, 0.5].
    norm_x = cx / img_w - 0.5
    norm_y = cy / img_h - 0.5
    pan = norm_x * hfov_deg          # +right
    tilt = norm_y * vfov_deg         # +down (v grows downward)
    # depth is currently advisory under the pinhole model; ignore bad values.
    if depth_m is not None and depth_m <= 0:
        depth_m = None
    return (_clamp(pan, pan_limit_deg), _clamp(tilt, tilt_limit_deg))


class SprayTargeter:
    """Stateful helper that turns detections into aim angles for a frame.

    Holds the camera geometry so the orchestrator only passes a bbox + optional
    depth. Pure/host-safe: no hardware here (the servo driver lives in
    ``pi/control/servo_pwm.py``).
    """

    def __init__(self, img_w: int = 640, img_h: int = 480,
                 hfov_deg: float = 160.0, vfov_deg: float = 100.0,
                 pan_limit_deg: float = PAN_LIMIT_DEG,
                 tilt_limit_deg: float = TILT_LIMIT_DEG):
        self.img_w = img_w
        self.img_h = img_h
        self.hfov_deg = hfov_deg
        self.vfov_deg = vfov_deg
        self.pan_limit_deg = pan_limit_deg
        self.tilt_limit_deg = tilt_limit_deg
        self.last_aim: tuple[float, float] = (0.0, 0.0)

    def aim(self, bbox: tuple[float, float, float, float],
            depth_m: float | None = None) -> tuple[float, float]:
        """Compute (pan_deg, tilt_deg) for a detection and remember it."""
        self.last_aim = aim_angles(
            bbox, self.img_w, self.img_h, self.hfov_deg, self.vfov_deg,
            depth_m=depth_m, pan_limit_deg=self.pan_limit_deg,
            tilt_limit_deg=self.tilt_limit_deg,
        )
        return self.last_aim

    def aim_from_geometry(self, bbox, img_w, img_h, hfov_deg, vfov_deg,
                          depth_m=None):
        """Stateless convenience wrapper around ``aim_angles``."""
        return aim_angles(bbox, img_w, img_h, hfov_deg, vfov_deg,
                          depth_m=depth_m, pan_limit_deg=self.pan_limit_deg,
                          tilt_limit_deg=self.tilt_limit_deg)
