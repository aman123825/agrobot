"""Weed detection (EfficientDet-Lite / YOLOv8n).

Trained on DeepWeeds (BOM #100). A positive detection triggers spot-spraying:
the Pi sends SPRAY_ON to the ESP32, which fires the misting relay, then
SPRAY_OFF - targeted application instead of blanket spraying.
"""
from __future__ import annotations

import config


class WeedDetector:
    def __init__(self, model_path: str | None = None, conf_threshold: float = 0.5):
        self.model_path = model_path or f"{config.MODEL_DIR}/deepweeds_yolov8n.tflite"
        self.conf_threshold = conf_threshold
        self.model = None

    def load(self) -> None:
        # TODO: load model (Coral delegate if available).
        raise NotImplementedError

    def detect(self, frame) -> bool:
        """Return True if a weed is detected above the confidence threshold."""
        # TODO: run inference; return whether to trigger the sprayer.
        raise NotImplementedError
