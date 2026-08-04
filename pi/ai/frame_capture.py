"""Active-learning frame capture (docs/UPGRADES.md §8).

Field accuracy comes from retraining on the rover's own footage. This module
saves the frames worth labelling - detections the models were *unsure* about
(confidence inside a low-confidence band) plus a sparse periodic sample - each
with a JSON sidecar of the detections, ready for re-annotation
(Roboflow/CVAT) and fine-tuning.

Rate-limited and file-capped so it can run unattended for a whole mission
without filling the SD card. Images are written with cv2 when available,
falling back to numpy `.npy`; the decision logic is pure and unit-testable.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config

logger = logging.getLogger(__name__)

LOW_CONF_BAND = (0.25, 0.55)   # "model was unsure" - the gold for retraining


def capture_reason(frame_no: int, detections: list[dict],
                   every_n: int = 600,
                   low_conf: tuple[float, float] = LOW_CONF_BAND) -> str | None:
    """Why this frame is worth saving, or None.

    'low_conf'  - any detection confidence inside the low-confidence band.
    'periodic'  - every Nth frame, as an unbiased sample of the field.
    """
    lo, hi = low_conf
    for det in detections:
        conf = float(det.get("conf", 0.0))
        if lo <= conf <= hi:
            return "low_conf"
    if every_n > 0 and frame_no % every_n == 0:
        return "periodic"
    return None


class FrameCapture:
    def __init__(self, out_dir: str | None = None, every_n: int = 600,
                 low_conf: tuple[float, float] = LOW_CONF_BAND,
                 min_interval_s: float = 5.0, max_files: int = 2000):
        self.out_dir = out_dir or config.CAPTURE_DIR
        self.every_n = every_n
        self.low_conf = low_conf
        self.min_interval_s = min_interval_s
        self.max_files = max_files
        self._last_save = 0.0
        self._count: int | None = None  # lazy; counted on first save attempt

    def _file_count(self) -> int:
        if self._count is None:
            try:
                self._count = sum(1 for n in os.listdir(self.out_dir)
                                  if n.endswith((".jpg", ".npy")))
            except OSError:
                self._count = 0
        return self._count

    def _write_image(self, frame, path_base: str) -> str | None:
        try:
            import cv2

            path = path_base + ".jpg"
            if cv2.imwrite(path, frame):
                return path
        except Exception:
            pass
        try:
            import numpy as np

            path = path_base + ".npy"
            np.save(path, frame)
            return path
        except Exception as exc:
            logger.warning("frame capture failed (%s)", exc)
            return None

    def consider(self, frame, frame_no: int, detections: list[dict],
                 now: float | None = None) -> str | None:
        """Save the frame if it's worth labelling. Returns the path or None."""
        reason = capture_reason(frame_no, detections, self.every_n, self.low_conf)
        if reason is None:
            return None
        now = time.time() if now is None else now
        if now - self._last_save < self.min_interval_s:
            return None
        if self._file_count() >= self.max_files:
            return None

        try:
            os.makedirs(self.out_dir, exist_ok=True)
        except OSError as exc:
            logger.warning("capture dir unavailable (%s)", exc)
            return None
        base = os.path.join(self.out_dir, f"cap_{int(now)}_{frame_no}_{reason}")
        path = self._write_image(frame, base)
        if path is None:
            return None
        sidecar = {
            "t": now,
            "frame_no": frame_no,
            "reason": reason,
            "detections": [
                {"label": d.get("label"), "conf": d.get("conf"),
                 "bbox": list(d.get("bbox", ()))}
                for d in detections
            ],
        }
        try:
            with open(base + ".json", "w", encoding="utf-8") as fh:
                json.dump(sidecar, fh)
        except OSError:
            pass
        self._last_save = now
        self._count = self._file_count() + 1
        logger.info("captured %s (%s, %d detections)", path, reason, len(detections))
        return path
