"""On-device inference benchmark (docs/UPGRADES.md §8).

Measures real latency/FPS of each AI stage on THIS device - CPU vs Coral vs
whatever backend actually loaded - so hardware-upgrade decisions rest on
measured numbers, not vendor blogs.

Run on the Pi (or any dev box):

    python pi/ai/benchmark.py               # all stages, synthetic frames
    python pi/ai/benchmark.py --image f.jpg # use a real frame
    python pi/ai/benchmark.py --iters 100

Results are printed and appended to benchmarks.jsonl for tracking across
hardware/model changes.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import statistics
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)


def _make_frame(image_path: str | None):
    if image_path:
        try:
            import cv2

            frame = cv2.imread(image_path)
            if frame is not None:
                return frame
            logger.warning("could not read %s; using synthetic frame", image_path)
        except Exception as exc:
            logger.warning("cv2 unavailable (%s); using synthetic frame", exc)
    import numpy as np

    rng = np.random.default_rng(0)
    return rng.integers(0, 255, size=(480, 640, 3), dtype=np.uint8)


def bench(name: str, fn, frame, iters: int, warmup: int = 3) -> dict | None:
    """Time fn(frame) over `iters` runs. Returns a result record or None."""
    try:
        for _ in range(warmup):
            fn(frame)
        times = []
        for _ in range(iters):
            t0 = time.perf_counter()
            fn(frame)
            times.append(time.perf_counter() - t0)
    except Exception as exc:
        logger.warning("%s: benchmark failed (%s)", name, exc)
        return None
    mean_ms = statistics.fmean(times) * 1000.0
    p95_ms = sorted(times)[int(len(times) * 0.95) - 1] * 1000.0
    return {
        "stage": name,
        "iters": iters,
        "mean_ms": round(mean_ms, 2),
        "p95_ms": round(p95_ms, 2),
        "fps": round(1000.0 / mean_ms, 1) if mean_ms > 0 else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AgriRover AI benchmark")
    parser.add_argument("--iters", type=int, default=50)
    parser.add_argument("--image", type=str, default=None, help="use a real frame")
    parser.add_argument("--out", type=str, default="benchmarks.jsonl")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    from ai.disease_detection import DiseaseClassifier
    from ai.obstacle_detection import ObstacleDetector
    from ai.weed_detection import WeedDetector

    frame = _make_frame(args.image)
    stages = []

    obstacle = ObstacleDetector()
    obstacle.load()
    stages.append((f"obstacle[{obstacle.backend}]", obstacle.detect))

    weed = WeedDetector()
    weed.load()
    stages.append((f"weed[{weed.backend}]", weed.detect))

    disease = DiseaseClassifier()
    disease.load()
    backend = "tflite" if disease.interpreter is not None else None
    stages.append((f"disease[{backend}]", disease.classify))

    results = []
    for name, fn in stages:
        if "[None]" in name:
            print(f"{name:28s}  SKIPPED (no model/backend loaded)")
            continue
        rec = bench(name, fn, frame, args.iters)
        if rec is None:
            continue
        results.append(rec)
        print(f"{name:28s}  mean {rec['mean_ms']:8.2f} ms   "
              f"p95 {rec['p95_ms']:8.2f} ms   {rec['fps']:6.1f} fps")

    if results:
        record = {"t": time.time(), "results": results}
        try:
            with open(args.out, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
            print(f"\nappended to {args.out}")
        except OSError as exc:
            logger.warning("could not write %s (%s)", args.out, exc)
    else:
        print("\nNo stage had a loaded backend - deploy models to models/ "
              "first (see models/README.md).")


if __name__ == "__main__":
    main()
