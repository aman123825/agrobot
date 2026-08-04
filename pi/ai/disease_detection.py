"""Plant disease classification (MobileNetV2 / TFLite).

Trained on PlantVillage (BOM #99): 38 classes across tomato, potato, pepper,
corn, etc. Runs on captured frames from the Pi Camera.

Model files are tried in order (matching training/disease_classification.ipynb
outputs): the Coral-compiled model first, then the INT8 CPU model, then the
float16 CPU fallback, then the legacy filename.
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config

from ai.tflite_backend import load_interpreter, read_labels

logger = logging.getLogger(__name__)

# Tried in order by load(); first loadable file wins.
MODEL_CANDIDATES = (
    "disease_model_quant_edgetpu.tflite",  # notebook output, Coral-compiled
    "disease_model_quant.tflite",          # INT8 pre-compiler (CPU TFLite)
    "disease_model_float16.tflite",        # float16 CPU fallback
    "plantvillage_mobilenetv2.tflite",     # legacy filename
)


class DiseaseClassifier:
    def __init__(self, model_path: str | None = None, labels_path: str | None = None):
        self.model_path = model_path
        self.labels_path = labels_path or f"{config.MODEL_DIR}/plantvillage_labels.txt"
        self.interpreter = None
        self.labels: list[str] = []

    def _candidates(self) -> list[str]:
        if self.model_path:
            return [self.model_path]
        return [os.path.join(config.MODEL_DIR, name) for name in MODEL_CANDIDATES]

    def load(self) -> bool:
        for path in self._candidates():
            if self.model_path is None and not os.path.exists(path):
                continue
            self.interpreter = load_interpreter(path, use_coral=config.USE_CORAL)
            if self.interpreter is not None:
                logger.info("DiseaseClassifier: loaded %s", path)
                break
        self.labels = read_labels(self.labels_path)
        if self.interpreter is not None and not self.labels:
            logger.warning("DiseaseClassifier: no labels file (%s); "
                           "classify() will return raw class indices",
                           self.labels_path)
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
