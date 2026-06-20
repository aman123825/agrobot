"""Obstacle detection (YOLOv8n) with optional Coral Edge TPU acceleration.

Runs ~30 fps on Coral vs ~3 fps CPU-only (BOM #41, #97). When an obstacle is
detected within the stop distance, the caller forwards a STOP command to the
ESP32 over the serial bridge.
"""
from __future__ import annotations

import config


class ObstacleDetector:
    def __init__(self, model_path: str | None = None, use_coral: bool = config.USE_CORAL):
        self.model_path = model_path or f"{config.MODEL_DIR}/yolov8n_obstacle.tflite"
        self.use_coral = use_coral
        self.model = None  # lazy-loaded

    def load(self) -> None:
        """Load the YOLOv8n model, delegating to the Edge TPU if available."""
        # TODO: from ultralytics import YOLO; or tflite_runtime.Interpreter with
        # the libedgetpu delegate when self.use_coral is True.
        raise NotImplementedError

    def detect(self, frame):
        """Return a list of detections [{label, conf, bbox, distance_mm}].

        Distance is fused with the VL53L1X ToF reading (circuit §4 / BOM #38)
        for a 3D obstacle profile.
        """
        # TODO: run inference, parse boxes, attach ToF distance.
        raise NotImplementedError
