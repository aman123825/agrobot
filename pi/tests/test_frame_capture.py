"""Tests for the active-learning frame capture logic and file writing."""
import json
import os

import numpy as np

from ai.frame_capture import FrameCapture, capture_reason

FRAME = np.zeros((48, 64, 3), dtype=np.uint8)


class TestCaptureReason:
    def test_low_confidence_wins(self):
        dets = [{"label": "person", "conf": 0.4, "bbox": (0, 0, 1, 1)}]
        assert capture_reason(1, dets) == "low_conf"

    def test_confident_detection_not_saved(self):
        dets = [{"label": "person", "conf": 0.95, "bbox": (0, 0, 1, 1)}]
        assert capture_reason(1, dets) is None

    def test_periodic_sample(self):
        assert capture_reason(600, []) == "periodic"
        assert capture_reason(601, []) is None

    def test_periodic_disabled(self):
        assert capture_reason(600, [], every_n=0) is None


class TestFrameCapture:
    def test_saves_image_and_sidecar(self, tmp_path):
        cap = FrameCapture(out_dir=str(tmp_path), min_interval_s=0.0)
        dets = [{"label": "weed", "conf": 0.35, "bbox": (1, 2, 3, 4)}]
        path = cap.consider(FRAME, 7, dets, now=1000.0)
        assert path is not None and os.path.exists(path)
        sidecar = json.load(open(os.path.splitext(path)[0] + ".json",
                                 encoding="utf-8"))
        assert sidecar["reason"] == "low_conf"
        assert sidecar["frame_no"] == 7
        assert sidecar["detections"][0]["bbox"] == [1, 2, 3, 4]

    def test_rate_limited(self, tmp_path):
        cap = FrameCapture(out_dir=str(tmp_path), min_interval_s=5.0)
        dets = [{"label": "weed", "conf": 0.35, "bbox": (1, 2, 3, 4)}]
        assert cap.consider(FRAME, 1, dets, now=1000.0) is not None
        assert cap.consider(FRAME, 2, dets, now=1002.0) is None   # too soon
        assert cap.consider(FRAME, 3, dets, now=1006.0) is not None

    def test_file_cap(self, tmp_path):
        cap = FrameCapture(out_dir=str(tmp_path), min_interval_s=0.0, max_files=1)
        dets = [{"label": "weed", "conf": 0.35, "bbox": (1, 2, 3, 4)}]
        assert cap.consider(FRAME, 1, dets, now=1000.0) is not None
        assert cap.consider(FRAME, 2, dets, now=1001.0) is None   # cap reached

    def test_boring_frame_not_saved(self, tmp_path):
        cap = FrameCapture(out_dir=str(tmp_path), min_interval_s=0.0)
        assert cap.consider(FRAME, 5, [], now=1000.0) is None
        assert os.listdir(tmp_path) == []
