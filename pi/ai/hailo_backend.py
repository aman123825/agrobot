"""Hailo-8 / Hailo-8L YOLO inference backend (Raspberry Pi 5 + AI HAT+).

Primary edge-AI path for the production platform (docs/accelerator-alternatives.md
Tier B): a Pi 5 with the 26-TOPS Hailo-8 AI HAT+ replaces the Pi 4 + Coral. The
Colab notebooks train the same YOLOv8/26n; export adds one stage
(`.pt -> ONNX -> Hailo Dataflow Compiler -> .hef`). This module runs the compiled
`.hef` through the HailoRT Python API and returns the SAME detection dicts as
`ai/yolo_tflite.py`, so `obstacle_detection.py` / `weed_detection.py` and the
orchestrator switch backends transparently.

Design mirrors `yolo_tflite.py`:
  * detect() -> [{label, conf, bbox=(x1,y1,x2,y2)}] in original-frame pixels.
  * The YOLOv8 raw head decode + NMS is identical (accelerator-independent), so
    we reuse `_nms` and the same (cx,cy,w,h + per-class score) math.

`hailo_platform` (HailoRT) and cv2/numpy are imported lazily and guarded, so the
module imports cleanly on any machine; `load()` returns False when the runtime or
hardware is absent and callers fall back to the Coral/CPU TFLite path.

NOTE: This path requires on-device validation on the Pi 5 + Hailo-8. The decode
contract is hardware-independent and unit-tested via the shared TFLite decode;
the HailoRT I/O below follows the documented InferVStreams pipeline and must be
smoke-tested against a real `.hef` before field use.
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ai.tflite_backend import read_labels
from ai.yolo_tflite import _nms

logger = logging.getLogger(__name__)


class HailoYolo:
    """Run an exported YOLO `.hef` detector on a Hailo device.

    Same public surface as `ai.yolo_tflite.YoloTflite`: construct with the model
    path + labels, call `load()`, then `detect(frame)`.
    """

    def __init__(self, model_path: str, labels_path: str | None = None,
                 conf_threshold: float = 0.4, iou_threshold: float = 0.45):
        self.model_path = model_path
        self.labels_path = labels_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.labels: list[str] = []
        # HailoRT handles (populated by load()).
        self._hef = None
        self._target = None
        self._network_group = None
        self._network_group_params = None
        self._input_vstreams_params = None
        self._output_vstreams_params = None
        self._input_shape = None  # (h, w) the .hef expects

    def load(self) -> bool:
        """Configure the Hailo device with the .hef. True if a device came up."""
        if not os.path.exists(self.model_path):
            return False
        try:
            from hailo_platform import (  # type: ignore
                HEF,
                ConfigureParams,
                HailoStreamInterface,
                InputVStreamParams,
                OutputVStreamParams,
                VDevice,
            )
        except Exception as exc:  # HailoRT not installed (e.g. dev laptop)
            logger.info("HailoRT unavailable (%s); Hailo backend disabled", exc)
            return False

        try:
            self._hef = HEF(self.model_path)
            self._target = VDevice()
            configure_params = ConfigureParams.create_from_hef(
                self._hef, interface=HailoStreamInterface.PCIe)
            self._network_group = self._target.configure(
                self._hef, configure_params)[0]
            self._network_group_params = self._network_group.create_params()
            self._input_vstreams_params = InputVStreamParams.make(
                self._network_group)
            self._output_vstreams_params = OutputVStreamParams.make(
                self._network_group)

            in_info = self._hef.get_input_vstream_infos()[0]
            # HailoRT shape is (height, width, channels).
            self._input_shape = (int(in_info.shape[0]), int(in_info.shape[1]))

            if self.labels_path:
                self.labels = read_labels(self.labels_path)
            logger.info("HailoYolo: device ready (%s, input=%s)",
                        self.model_path, self._input_shape)
            return True
        except Exception as exc:
            logger.warning("HailoYolo: failed to configure %s (%s)",
                           self.model_path, exc)
            self._target = None
            return False

    def _preprocess(self, frame):
        """Resize + BGR->RGB to the model's input, as uint8 NHWC (Hailo native)."""
        import cv2
        import numpy as np

        h, w = self._input_shape
        img = cv2.resize(frame, (w, h))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return np.expand_dims(img.astype(np.uint8), axis=0)

    def _raw_output(self, results):
        """Normalize the HailoRT output dict to a float32 (N, 4+nc) array.

        Hailo returns a dict keyed by output-stream name. For a single-head
        YOLOv8 export there is one entry; we squeeze it and orient it the same
        way `yolo_tflite._raw_output` does.
        """
        import numpy as np

        arr = next(iter(results.values())) if isinstance(results, dict) else results
        arr = np.asarray(arr, dtype=np.float32)
        arr = np.squeeze(arr)
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
        """Return [{label, conf, bbox=(x1,y1,x2,y2)}] in original-frame pixels."""
        if self._target is None or self._network_group is None:
            return []
        import numpy as np
        from hailo_platform import InferVStreams  # type: ignore

        fh, fw = frame.shape[:2]
        model_in = self._preprocess(frame)
        in_info = self._hef.get_input_vstream_infos()[0]

        try:
            with InferVStreams(self._network_group,
                               self._input_vstreams_params,
                               self._output_vstreams_params) as infer_pipeline:
                with self._network_group.activate(self._network_group_params):
                    results = infer_pipeline.infer({in_info.name: model_in})
        except Exception as exc:
            logger.warning("HailoYolo: inference failed (%s)", exc)
            return []

        arr = self._raw_output(results)
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

        # Ultralytics exports emit normalized [0,1]; fall back to input-pixel.
        if float(boxes_xywh.max()) > 2.0:
            ih, iw = self._input_shape
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
