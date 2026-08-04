"""Obstacle detection (YOLOv8n) with Hailo-8 / Coral Edge TPU acceleration.

Runs ~130-160 fps on the Pi 5 + Hailo-8 AI HAT+ (primary platform), ~30 fps on
the Pi 4 + Coral fallback, ~3 fps CPU-only (BOM #41, #97). When an obstacle is
detected within the stop distance, the orchestrator forwards STOP to the ESP32.

Backends, tried in order of the model-file candidates below:
  * .hef     -> ai/hailo_backend.py (HailoRT, Pi 5 + Hailo-8 AI HAT+) - primary
               production platform (docs/accelerator-alternatives.md Tier B).
  * .tflite  -> ai/yolo_tflite.py (TFLite interpreter, Edge TPU delegate when
                available) - Coral/CPU fallback; matches the
                training/obstacle_detection.ipynb export names.
  * .pt      -> ultralytics (desktop debugging / legacy weights).

Heavy imports are lazy and guarded so this module imports cleanly even on a
machine without the model stack installed; `load()` reports whether a real
backend came up.
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config

from ai.yolo_tflite import YoloTflite

logger = logging.getLogger(__name__)

# Tried in order by load(); first loadable file wins.
MODEL_CANDIDATES = (
    "obstacle_model.hef",                   # Pi 5 + Hailo-8 (primary platform)
    "obstacle_model_quant_edgetpu.tflite",  # Coral-compiled (fallback)
    "obstacle_model_quant.tflite",          # INT8 pre-compiler (CPU TFLite)
    "yolov8n_obstacle.pt",                  # legacy ultralytics weights
)
LABELS_FILE = "obstacle_labels.txt"         # person, vehicle, animal, ...


class ObstacleDetector:
    def __init__(
        self,
        model_path: str | None = None,
        use_coral: bool = config.USE_CORAL,
        stop_distance_mm: float = 400.0,
        conf_threshold: float = 0.40,
    ):
        self.model_path = model_path
        self.use_coral = use_coral
        self.stop_distance_mm = stop_distance_mm
        self.conf_threshold = conf_threshold
        self.model = None
        self.backend: str | None = None

    def _candidates(self) -> list[str]:
        if self.model_path:
            return [self.model_path]
        return [os.path.join(config.MODEL_DIR, name) for name in MODEL_CANDIDATES]

    def load(self) -> bool:
        """Load the first available model. True if a usable backend came up."""
        for path in self._candidates():
            if self.model_path is None and not os.path.exists(path):
                continue
            if path.endswith(".hef"):
                if not config.USE_HAILO:
                    continue
                from ai.hailo_backend import HailoYolo

                hef = HailoYolo(
                    path,
                    labels_path=os.path.join(config.MODEL_DIR, LABELS_FILE),
                    conf_threshold=self.conf_threshold,
                )
                if hef.load():
                    self.model = hef
                    self.backend = "hailo"
                    logger.info("ObstacleDetector: Hailo backend ready (%s)", path)
                    return True
                continue
            if path.endswith(".tflite"):
                tfl = YoloTflite(
                    path,
                    labels_path=os.path.join(config.MODEL_DIR, LABELS_FILE),
                    conf_threshold=self.conf_threshold,
                    use_coral=self.use_coral,
                )
                if tfl.load():
                    self.model = tfl
                    self.backend = "tflite"
                    logger.info("ObstacleDetector: TFLite backend ready (%s)", path)
                    return True
                continue
            try:
                from ultralytics import YOLO

                self.model = YOLO(path)
                self.backend = "ultralytics"
                logger.info("ObstacleDetector: ultralytics backend ready (%s)", path)
                return True
            except Exception as exc:  # model/lib missing -> try next candidate
                logger.warning("ObstacleDetector: %s failed (%s)", path, exc)
        logger.warning("ObstacleDetector: no backend; detect() returns []")
        self.model = None
        self.backend = None
        return False

    def detect(self, frame, distance_mm: float | None = None) -> list[dict]:
        """Return [{label, conf, bbox=(x1,y1,x2,y2), distance_mm}] for the frame.

        `distance_mm` (from the VL53L1X ToF, circuit §4) is attached to every
        detection so the caller can reason in real-world distance.
        """
        if self.model is None:
            return []
        if self.backend in ("tflite", "hailo"):
            detections = [dict(det, distance_mm=distance_mm)
                          for det in self.model.detect(frame)]
            return detections
        detections: list[dict] = []
        results = self.model(frame, verbose=False)
        for res in results:
            boxes = getattr(res, "boxes", None) or []
            for box in boxes:
                conf = float(box.conf[0]) if box.conf is not None else 0.0
                if conf < self.conf_threshold:
                    continue
                cls_id = int(box.cls[0]) if box.cls is not None else -1
                label = res.names.get(cls_id, str(cls_id)) if hasattr(res, "names") else str(cls_id)
                xyxy = [float(v) for v in box.xyxy[0]]
                detections.append(
                    {
                        "label": label,
                        "conf": conf,
                        "bbox": tuple(xyxy),
                        "distance_mm": distance_mm,
                    }
                )
        return detections

    def should_stop(self, detections: list[dict]) -> bool:
        """Decide whether to command a STOP.

        Stop if any detection is closer than the stop distance, or - when ToF
        distance is unknown - if any obstacle is detected at all (fail-safe).
        """
        for det in detections:
            dist = det.get("distance_mm")
            if dist is None or dist < self.stop_distance_mm:
                return True
        return False
