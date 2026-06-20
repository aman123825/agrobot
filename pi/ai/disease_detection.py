"""Plant disease classification (MobileNetV2 / TFLite).

Trained on PlantVillage (BOM #99): 38 classes across tomato, potato, pepper,
corn, etc. Runs on captured 1080p frames from the Pi Camera.
"""
from __future__ import annotations

import config


class DiseaseClassifier:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or f"{config.MODEL_DIR}/plantvillage_mobilenetv2.tflite"
        self.interpreter = None

    def load(self) -> None:
        # TODO: load TFLite interpreter (CPU or Coral delegate).
        raise NotImplementedError

    def classify(self, frame):
        """Return (class_name, confidence) for the dominant leaf in frame."""
        # TODO: preprocess (resize/normalize via OpenCV) then invoke interpreter.
        raise NotImplementedError
