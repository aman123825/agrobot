"""Plant disease classification (MobileNetV2 / TFLite).

Trained on PlantVillage (BOM #99): 38 classes across tomato, potato, pepper,
corn, etc. Runs on captured frames from the Pi Camera.
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config  # noqa: E402
from ai.tflite_backend import load_interpreter, read_labels  # noqa: E402

logger = logging.getLogger(__name__)


class DiseaseClassifier:
    def __init__(self, model_path: str | None = None, labels_path: str | None = None):
        self.model_path = model_path or f"{config.MODEL_DIR}/plantvillage_mobilenetv2.tflite"
        self.labels_path = labels_path or f"{config.MODEL_DIR}/plantvillage_labels.txt"
        self.interpreter = None
        self.labels: list[str] = []

    def load(self) -> bool:
        self.interpreter = load_interpreter(self.model_path, use_coral=config.USE_CORAL)
        self.labels = read_labels(self.labels_path)
        return self.interpreter is not None

    def _preprocess(self, frame):
        import cv2
        import numpy as np

        inp = self.interpreter.get_input_details()[0]
        _, h, w, _ = inp["shape"]
        img = cv2.resize(frame, (int(w), int(h)))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if inp["dtype"] == np.uint8:
            return np.expand_dims(img.astype(np.uint8), axis=0)
        return np.expand_dims(img.astype(np.float32) / 255.0, axis=0)

    def classify(self, frame) -> tuple[str, float]:
        """Return (class_name, confidence). ('unknown', 0.0) if no backend."""
        if self.interpreter is None:
            return ("unknown", 0.0)
        import numpy as np

        inp = self.interpreter.get_input_details()[0]
        out = self.interpreter.get_output_details()[0]
        self.interpreter.set_tensor(inp["index"], self._preprocess(frame))
        self.interpreter.invoke()
        scores = self.interpreter.get_tensor(out["index"])[0].astype(np.float32)

        if out["dtype"] == np.uint8:  # dequantize
            scale, zero = out["quantization"]
            scores = (scores - zero) * (scale or 1.0)

        idx = int(np.argmax(scores))
        total = float(np.sum(scores)) or 1.0
        conf = float(scores[idx]) / total
        label = self.labels[idx] if idx < len(self.labels) else str(idx)
        return (label, conf)
