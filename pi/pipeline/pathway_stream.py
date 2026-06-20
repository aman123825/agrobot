"""Pathway real-time stream processing (BOM #102).

Subscribes to MQTT telemetry, applies a 30-second moving average to NPK
readings, flags anomalies (> 2 sigma from the field mean), and joins GPS
coordinates to every reading before handing results to the dashboard.
"""
from __future__ import annotations

# import pathway as pw  # enable once the pipeline is implemented

WINDOW_SECONDS = 30
ANOMALY_SIGMA = 2.0


def build_pipeline():
    """Construct and return the Pathway computation graph.

    Outline:
      1. ingest MQTT (rover/npk, rover/gps) as a streaming table
      2. tumbling/sliding 30s window -> moving average per nutrient
      3. compute field mean/std -> flag |x - mean| > 2*std
      4. join GPS by timestamp -> emit to dashboard sink
    """
    # TODO: implement with pathway primitives.
    raise NotImplementedError


if __name__ == "__main__":
    build_pipeline()
