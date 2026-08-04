"""Ultralytics-YOLO TFLite inference backend (Coral Edge TPU compatible).

The training notebooks export YOLOv8n to INT8 .tflite (input 320 or 640) and
compile it for the Edge TPU. Ultralytics' Python API cannot delegate to the
Coral, so this module runs those exports directly through the TFLite
interpreter: preprocess, invoke, dequantize, decode the raw [1, 4+nc, N]
head (cx, cy, w, h + per-class scores), confidence-filter and NMS.

Pure numpy at inference time - no ultralytics/torch needed on the Pi.
numpy/cv2 are imported lazily so the module imports cleanly anywhere.
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ai.tflite_backend import load_interpreter, read_labels

logger = logging.getLogger(__name__)


def _nms(boxes, scores, iou_threshold: float):
    """Greedy class-agnostic NMS. boxes: (N,4) xyxy ndarray. Returns kept idx."""
    import numpy as np

    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = np.maximum(0.0, x2 - x1) * np.maximum(0.0, y2 - y1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size:
        i = order[0]
        keep.append(int(i))
        if order.size == 1:
            break
        rest = order[1:]
        xx1 = np.maximum(x1[i], x1[rest])
        yy1 = np.maximum(y1[i], y1[rest])
        xx2 = np.minimum(x2[i], x2[rest])
        yy2 = np.minimum(y2[i], y2[rest])
        inter = np.maximum(0.0, xx2 - xx1) * np.maximum(0.0, yy2 - yy1)
        iou = inter / (areas[i] + areas[rest] - inter + 1e-9)
        order = rest[iou <= iou_threshold]
    return keep


class YoloTflite:
    """Run an exported YOLO .tflite (optionally *_edgetpu.tflite) detector.

    detect() returns [{label, conf, bbox=(x1, y1, x2, y2)}] in pixel
    coordinates of the original frame - the same schema the ultralytics
    backend produces, so callers can switch backends transparently.
    """

    def __init__(self, model_path: str, labels_path: str | None = None,
                 conf_threshold: float = 0.4, iou_threshold: float = 0.45,
                 use_coral: bool = False):
        self.model_path = model_path
        self.labels_path = labels_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.use_coral = use_coral
        self.interpreter = None
        self.labels: list[str] = []

    def load(self) -> bool:
        self.interpreter = load_interpreter(self.model_path, use_coral=self.use_coral)
        if self.labels_path:
            self.labels = read_labels(self.labels_path)
        return self.interpreter is not None

    # ---- internals ----
    def _preprocess(self, frame):
        """Resize + colour-convert + quantize the frame for the model input."""
        import cv2
        import numpy as np

        inp = self.interpreter.get_input_details()[0]
        _, h, w, _ = inp["shape"]
        img = cv2.resize(frame, (int(w), int(h)))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img01 = img.astype(np.float32) / 255.0

        dtype = inp["dtype"]
        if dtype in (np.uint8, np.int8):
            scale, zero = inp["quantization"]
            if not scale:  # unquantized integer input: assume raw 0-255
                q = img.astype(dtype)
            else:
                info = np.iinfo(dtype)
                q = np.clip(np.round(img01 / scale + zero), info.min, info.max)
                q = q.astype(dtype)
            return np.expand_dims(q, axis=0)
        return np.expand_dims(img01, axis=0)

    def _raw_output(self):
        """Return the dequantized output as float32 (N, 4+nc)."""
        import numpy as np

        out = self.interpreter.get_output_details()[0]
        arr = self.interpreter.get_tensor(out["index"]).astype(np.float32)
        if out["dtype"] in (np.uint8, np.int8):
            scale, zero = out["quantization"]
            arr = (arr - zero) * (scale or 1.0)
        arr = np.squeeze(arr)
        # Exports come as (4+nc, N); tolerate (N, 4+nc) too. When the labels
        # are known, 4+nc disambiguates; otherwise assume N is the larger dim.
        if arr.ndim != 2:
            return None
        channels = 4 + len(self.labels) if self.labels else None
        if channels is not None and arr.shape[1] == channels:
            pass
        elif channels is not None and arr.shape[0] == channels:
            arr = arr.T
        elif arr.shape[0] < arr.shape[1]:
            arr = arr.T
        return arr

    def detect(self, frame) -> list[dict]:
        if self.interpreter is None:
            return []
        import numpy as np

        fh, fw = frame.shape[:2]
        inp = self.interpreter.get_input_details()[0]
        self.interpreter.set_tensor(inp["index"], self._preprocess(frame))
        self.interpreter.invoke()
        arr = self._raw_output()
        if arr is None or arr.shape[1] < 5:
            return []

        boxes_xywh = arr[:, :4]
        class_scores = arr[:, 4:]
        confs = class_scores.max(axis=1)
        cls_ids = class_scores.argmax(axis=1)

        mask = confs >= self.conf_threshold
        if not mask.any():
            return []
        boxes_xywh, confs, cls_ids = boxes_xywh[mask], confs[mask], cls_ids[mask]

        # Ultralytics TFLite exports emit normalized [0,1] coords; fall back
        # to input-pixel coords if values are clearly larger than 1.
        if float(boxes_xywh.max()) > 2.0:
            _, ih, iw, _ = inp["shape"]
            boxes_xywh = boxes_xywh / np.array([iw, ih, iw, ih], dtype=np.float32)

        cx, cy, bw, bh = (boxes_xywh[:, 0], boxes_xywh[:, 1],
                          boxes_xywh[:, 2], boxes_xywh[:, 3])
        boxes = np.stack([
            (cx - bw / 2) * fw, (cy - bh / 2) * fh,
            (cx + bw / 2) * fw, (cy + bh / 2) * fh,
        ], axis=1)
        np.clip(boxes[:, 0::2], 0, fw, out=boxes[:, 0::2])
        np.clip(boxes[:, 1::2], 0, fh, out=boxes[:, 1::2])

        keep = _nms(boxes, confs, self.iou_threshold)
        detections = []
        for i in keep:
            cid = int(cls_ids[i])
            label = self.labels[cid] if cid < len(self.labels) else str(cid)
            detections.append({
                "label": label,
                "conf": float(confs[i]),
                "bbox": tuple(float(v) for v in boxes[i]),
            })
        return detections
