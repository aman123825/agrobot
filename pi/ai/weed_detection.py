"""Weed detection (YOLOv8n, DeepWeeds 9 classes).

Trained on DeepWeeds (BOM #100). A positive detection triggers spot-spraying:
the orchestrator fires the misting relay (Pi PCF8574) for a short burst -
targeted application instead of blanket spraying.

Backends, tried in order of the model-file candidates below:
  * .tflite  -> ai/yolo_tflite.py (TFLite interpreter, Edge TPU delegate when
                available) - matches the training/weed_detection.ipynb export.
  * .pt      -> ultralytics (desktop debugging / legacy weights).

The corrected training notebook uses bounding-box classes ``crop`` and
``weed``.  ``crop`` (plus legacy DeepWeeds ``negative(s)`` labels) is ignored,
so the sprayer fires only for the positive ``weed`` class.
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
    "weed_model.hef",                   # Pi 5 + Hailo-8 (primary platform)
    "weed_model_quant_edgetpu.tflite",  # Coral-compiled (fallback)
    "weed_model_quant.tflite",          # INT8 pre-compiler (CPU TFLite)
    "deepweeds_yolov8n.pt",             # legacy ultralytics weights
)
LABELS_FILE = "weed_labels.txt"         # crop, weed (current notebook)
IGNORE_LABELS = {"crop", "negative", "negatives"}


class WeedDetector:
    def __init__(self, model_path: str | None = None, conf_threshold: float = 0.5,
                 use_coral: bool = config.USE_CORAL):
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.use_coral = use_coral
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
                    logger.info("WeedDetector: Hailo backend ready (%s)", path)
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
                    logger.info("WeedDetector: TFLite backend ready (%s)", path)
                    return True
                continue
            try:
                from ultralytics import YOLO

                self.model = YOLO(path)
                self.backend = "ultralytics"
                logger.info("WeedDetector: ultralytics backend ready (%s)", path)
                return True
            except Exception as exc:
                logger.warning("WeedDetector: %s failed (%s)", path, exc)
        logger.warning("WeedDetector: no backend; detect() returns False")
        self.model = None
        self.backend = None
        return False

    def _detections(self, frame) -> list[dict]:
        """[{label, conf, bbox}] above threshold, weeds only (no negatives)."""
        if self.model is None:
            return []
        if self.backend in ("tflite", "hailo"):
            return [d for d in self.model.detect(frame)
                    if d["label"].lower() not in IGNORE_LABELS]
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
                if label.lower() in IGNORE_LABELS:
                    continue
                try:
                    xyxy = box.xyxy[0]
                    bbox = (float(xyxy[0]), float(xyxy[1]),
                            float(xyxy[2]), float(xyxy[3]))
                except (AttributeError, IndexError, TypeError):
                    continue
                detections.append({"label": label, "conf": conf, "bbox": bbox})
        return detections

    def detect(self, frame) -> bool:
        """Return True if a weed is detected above the confidence threshold."""
        return bool(self._detections(frame))

    def detect_best(self, frame):
        """Return (bbox, conf) for the highest-confidence weed, or None.

        bbox is (x1, y1, x2, y2) in pixels. Used by the aimed-spray path
        (FC-01) so the nozzle can be pointed at the weed before firing. Falls
        back to None when no backend or no detection clears the threshold.
        """
        detections = self._detections(frame)
        if not detections:
            return None
        best = max(detections, key=lambda d: d["conf"])
        return (best["bbox"], best["conf"])
