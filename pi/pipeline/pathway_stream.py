"""Real-time NPK stream processing (BOM #102).

Subscribes to MQTT telemetry, keeps a 30-second moving average per nutrient,
flags anomalies (> 2 sigma from the rolling field mean), joins the latest GPS
fix to every reading, appends to a dated CSV, and pushes Telegram alerts on
anomalies.

This is a self-contained implementation (paho-mqtt + stdlib) so it runs on the
Pi without extra services. A Pathway-native version can replace `StreamProcessor`
later; the MQTT contract and CSV schema stay the same.
"""
from __future__ import annotations

import csv
import json
import logging
import os
import statistics
import sys
import time
from collections import deque
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config
from bridge.mqtt_client import MqttClient

logger = logging.getLogger(__name__)

WINDOW_SECONDS = 30
ANOMALY_SIGMA = 2.0
NUTRIENTS = ("n", "p", "k", "ph")


class StreamProcessor:
    def __init__(self, alert_fn=None, csv_dir: str = "."):
        self.alert_fn = alert_fn
        self.csv_dir = csv_dir
        # per-nutrient rolling window of (timestamp, value)
        self._windows = {key: deque() for key in NUTRIENTS}
        self._last_gps = {"lat": 0.0, "lng": 0.0, "fix": 0}
        self._mqtt = MqttClient()

    # ---- MQTT handlers ----
    def _on_gps(self, payload: str) -> None:
        try:
            self._last_gps = json.loads(payload)
        except json.JSONDecodeError:
            logger.warning("bad GPS payload: %s", payload)

    def _on_npk(self, payload: str) -> None:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            logger.warning("bad NPK payload: %s", payload)
            return
        if not data.get("valid", 1):
            return
        now = time.time()
        row = self._process(now, data)
        self._write_csv(row)
        self._maybe_alert(row)

    # ---- core windowed stats ----
    def _process(self, now: float, data: dict) -> dict:
        row = {
            "timestamp": datetime.fromtimestamp(now, tz=timezone.utc).isoformat(),
            "lat": self._last_gps.get("lat", 0.0),
            "lng": self._last_gps.get("lng", 0.0),
            "gps_fix": self._last_gps.get("fix", 0),
        }
        for key in NUTRIENTS:
            value = float(data.get(key, 0.0))
            window = self._windows[key]
            window.append((now, value))
            cutoff = now - WINDOW_SECONDS
            while window and window[0][0] < cutoff:
                window.popleft()

            values = [v for _, v in window]
            mean = statistics.fmean(values) if values else value
            std = statistics.pstdev(values) if len(values) > 1 else 0.0
            is_anom = std > 0 and abs(value - mean) > ANOMALY_SIGMA * std

            row[key] = value
            row[f"{key}_avg30s"] = round(mean, 3)
            row[f"{key}_anomaly"] = int(is_anom)
        return row

    def _write_csv(self, row: dict) -> None:
        date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        path = os.path.join(self.csv_dir, f"field_log_{date}.csv")
        exists = os.path.exists(path)
        with open(path, "a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
            if not exists:
                writer.writeheader()
            writer.writerow(row)

    def _maybe_alert(self, row: dict) -> None:
        flagged = [k for k in NUTRIENTS if row.get(f"{k}_anomaly")]
        if flagged and self.alert_fn:
            lat, lng = row["lat"], row["lng"]
            msg = (
                f"Soil anomaly: {', '.join(flagged).upper()} "
                f"at GPS {lat:.5f}, {lng:.5f}"
            )
            try:
                self.alert_fn(msg)
            except Exception as exc:
                logger.warning("alert failed: %s", exc)

    # ---- lifecycle ----
    def run(self) -> None:
        self._mqtt.connect()
        self._mqtt.subscribe(config.TOPICS["gps"], self._on_gps)
        self._mqtt.subscribe(config.TOPICS["npk"], self._on_npk)
        logger.info("StreamProcessor running (window=%ss, sigma=%s)", WINDOW_SECONDS, ANOMALY_SIGMA)
        self._mqtt.loop_forever()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    try:
        from alerts.telegram_bot import send_alert
    except Exception:
        send_alert = None
    StreamProcessor(alert_fn=send_alert).run()


if __name__ == "__main__":
    main()
