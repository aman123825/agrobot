"""Weed detection (YOLOv8n / Ultralytics).

Trained on DeepWeeds (BOM #100). A positive detection triggers spot-spraying:
the orchestrator fires the misting relay (Pi PCF8574) for a short burst -
targeted application instead of blanket spraying.
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config  # noqa: E402

logger = logging.getLogger(__name__)


class WeedDetector:
    def __init__(self, model_path: str | None = None, conf_threshold: float = 0.5):
        self.model_path = model_path or f"{config.MODEL_DIR}/deepweeds_yolov8n.pt"
        self.conf_threshold = conf_threshold
        self.model = None
        self.backend: str | None = None

    def load(self) -> bool:
        try:
            from ultralytics import YOLO

            self.model = YOLO(self.model_path)
            self.backend = "ultralytics"
            logger.info("WeedDetector: ultralytics backend ready (%s)", self.model_path)
            return True
        except Exception as exc:
            logger.warning("WeedDetector: no backend (%s); detect() returns False", exc)
            self.model = None
            self.backend = None
            return False

    def detect(self, frame) -> bool:
        """Return True if a weed is detected above the confidence threshold."""
        if self.model is None:
            return False
        results = self.model(frame, verbose=False)
        for res in results:
            boxes = getattr(res, "boxes", None) or []
            for box in boxes:
                conf = float(box.conf[0]) if box.conf is not None else 0.0
                if conf >= self.conf_threshold:
                    return True
        return False

    def detect_best(self, frame):
        """Return (bbox, conf) for the highest-confidence weed, or None.

        bbox is (x1, y1, x2, y2) in pixels. Used by the aimed-spray path
        (FC-01) so the nozzle can be pointed at the weed before firing. Falls
        back to None when no backend or no detection clears the threshold.
        """
        if self.model is None:
            return None
        best = None
        best_conf = self.conf_threshold
        results = self.model(frame, verbose=False)
        for res in results:
            boxes = getattr(res, "boxes", None) or []
            for box in boxes:
                conf = float(box.conf[0]) if box.conf is not None else 0.0
                if conf >= best_conf:
                    try:
                        xyxy = box.xyxy[0]
                        bbox = (float(xyxy[0]), float(xyxy[1]),
                                float(xyxy[2]), float(xyxy[3]))
                    except (AttributeError, IndexError, TypeError):
                        continue
                    best = (bbox, conf)
                    best_conf = conf
        return best
