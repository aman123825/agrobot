"""Optional InfluxDB time-series writer for historical telemetry trends.

Guarded: if influxdb-client isn't installed or env vars aren't set, writes are
no-ops, so the rest of the stack runs without it.

Env: INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


class InfluxWriter:
    def __init__(self):
        self._write_api = None
        self._bucket = os.getenv("INFLUX_BUCKET", "agrorover")
        url = os.getenv("INFLUX_URL", "")
        token = os.getenv("INFLUX_TOKEN", "")
        org = os.getenv("INFLUX_ORG", "")
        if not url or not token:
            logger.info("InfluxDB not configured; time-series writes disabled")
            return
        try:
            from influxdb_client import InfluxDBClient
            from influxdb_client.client.write_api import SYNCHRONOUS

            client = InfluxDBClient(url=url, token=token, org=org)
            self._write_api = client.write_api(write_options=SYNCHRONOUS)
            self._org = org
            logger.info("InfluxDB writer ready (%s)", url)
        except Exception as exc:
            logger.warning("InfluxDB unavailable (%s)", exc)
            self._write_api = None

    def write(self, measurement: str, fields: dict, tags: dict | None = None) -> None:
        if self._write_api is None:
            return
        try:
            from influxdb_client import Point

            point = Point(measurement)
            for k, v in (tags or {}).items():
                point = point.tag(k, v)
            for k, v in fields.items():
                point = point.field(k, v)
            self._write_api.write(bucket=self._bucket, org=self._org, record=point)
        except Exception as exc:
            logger.warning("Influx write failed (%s)", exc)
