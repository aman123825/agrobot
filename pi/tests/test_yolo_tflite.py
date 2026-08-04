"""Tests for the YOLO TFLite decode path with a fake interpreter."""
import numpy as np

from ai.yolo_tflite import YoloTflite, _nms

LABELS = ["person", "vehicle", "animal", "rock", "stump", "fence", "ditch"]


class FakeInterp:
    """Minimal TFLite-interpreter stand-in: (1, 4+nc, N) float output."""

    out_dtype = np.float32
    out_quant = (0.0, 0)

    def get_input_details(self):
        return [{"shape": np.array([1, 320, 320, 3]), "dtype": np.uint8,
                 "quantization": (1 / 255.0, 0), "index": 0}]

    def get_output_details(self):
        return [{"dtype": self.out_dtype, "quantization": self.out_quant,
                 "index": 1}]

    def set_tensor(self, index, value):
        self.value = value

    def invoke(self):
        pass

    def get_tensor(self, index):
        out = np.zeros((1, 11, 3), dtype=np.float32)
        out[0, :4, 0] = [0.5, 0.5, 0.2, 0.4]; out[0, 4, 0] = 0.95   # person
        out[0, :4, 1] = [0.51, 0.5, 0.2, 0.4]; out[0, 4, 1] = 0.90  # duplicate
        out[0, :4, 2] = [0.1, 0.1, 0.05, 0.05]; out[0, 6, 2] = 0.10 # weak
        return out


class FakeInt8(FakeInterp):
    out_dtype = np.int8
    out_quant = (0.005, -128)

    def get_tensor(self, index):
        f = FakeInterp.get_tensor(self, index)
        return np.clip(np.round(f / 0.005 - 128), -128, 127).astype(np.int8)


def make_detector(interp):
    det = YoloTflite("fake.tflite", conf_threshold=0.4)
    det.interpreter = interp
    det.labels = list(LABELS)
    det._preprocess = lambda frame: np.zeros((1, 320, 320, 3), dtype=np.uint8)
    return det


FRAME = np.zeros((480, 640, 3), dtype=np.uint8)


class TestNms:
    def test_suppresses_overlap_keeps_distant(self):
        boxes = np.array([[0, 0, 100, 100], [5, 5, 105, 105],
                          [300, 300, 400, 400]], dtype=np.float32)
        scores = np.array([0.9, 0.8, 0.7], dtype=np.float32)
        assert _nms(boxes, scores, 0.45) == [0, 2]

    def test_single_box(self):
        boxes = np.array([[0, 0, 10, 10]], dtype=np.float32)
        assert _nms(boxes, np.array([0.5], dtype=np.float32), 0.45) == [0]


class TestDecode:
    def test_float_output(self):
        dets = make_detector(FakeInterp()).detect(FRAME)
        assert len(dets) == 1  # NMS killed the dup; threshold killed the weak
        det = dets[0]
        assert det["label"] == "person"
        assert abs(det["conf"] - 0.95) < 1e-6
        x1, y1, x2, y2 = det["bbox"]
        assert abs(x1 - 0.4 * 640) < 1 and abs(y2 - 0.7 * 480) < 1

    def test_int8_output_dequantized(self):
        dets = make_detector(FakeInt8()).detect(FRAME)
        assert len(dets) == 1 and dets[0]["label"] == "person"
        assert abs(dets[0]["conf"] - 0.95) < 0.01

    def test_no_interpreter_returns_empty(self):
        det = YoloTflite("missing.tflite")
        assert det.detect(FRAME) == []

    def test_unknown_class_id_falls_back_to_index_string(self):
        # Without labels, orientation relies on N > 4+nc (true for real
        # models: N=2100/8400), so this fake uses 20 anchors.
        class WideFake(FakeInterp):
            def get_tensor(self, index):
                out = np.zeros((1, 11, 20), dtype=np.float32)
                out[0, :4, 0] = [0.5, 0.5, 0.2, 0.4]
                out[0, 4, 0] = 0.95
                return out

        det = make_detector(WideFake())
        det.labels = []  # no labels file -> class id as string
        dets = det.detect(FRAME)
        assert dets and dets[0]["label"] == "0"


class TestWeedFilter:
    def test_negatives_never_trigger_spray(self):
        from ai.weed_detection import WeedDetector

        det = WeedDetector()
        det.backend = "tflite"

        class OnlyNegatives:
            def detect(self, frame):
                return [{"label": "negatives", "conf": 0.9, "bbox": (0, 0, 9, 9)}]

        det.model = OnlyNegatives()
        assert det.detect(FRAME) is False
        assert det.detect_best(FRAME) is None

    def test_best_weed_wins(self):
        from ai.weed_detection import WeedDetector

        det = WeedDetector()
        det.backend = "tflite"

        class Mixed:
            def detect(self, frame):
                return [
                    {"label": "negatives", "conf": 0.99, "bbox": (0, 0, 9, 9)},
                    {"label": "lantana", "conf": 0.6, "bbox": (20, 20, 60, 60)},
                    {"label": "parthenium", "conf": 0.8, "bbox": (30, 30, 80, 80)},
                ]

        det.model = Mixed()
        bbox, conf = det.detect_best(FRAME)
        assert conf == 0.8 and bbox == (30, 30, 80, 80)
