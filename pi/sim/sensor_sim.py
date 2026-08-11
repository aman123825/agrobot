"""Synthetic sensor telemetry generator.

Produces JSON payloads matching the real MQTT topics published by the ESP32:
    rover/npk    -> {"n": float, "p": float, "k": float, "ph": float, "valid": 1}
    rover/gps    -> {"lat": float, "lng": float, "fix": 1}
    rover/status -> {"battery_v": float, "front_distance_cm": float}

Uses the rover model position to derive GPS coordinates via the same
geo.local_to_latlng helper used by the navigation stack.
"""
from __future__ import annotations

import math
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from nav.geo import local_to_latlng
except ImportError:  # pragma: no cover - standalone testing
    def local_to_latlng(east: float, north: float, lat0: float, lng0: float) -> tuple[float, float]:
        """Fallback if nav.geo is unavailable."""
        _R = 6378137.0
        lat = lat0 + math.degrees(north / _R)
        lng = lng0 + math.degrees(east / (_R * math.cos(math.radians(lat0))))
        return (lat, lng)


# Configurable GPS datum (field origin)
_DEFAULT_LAT0 = float(os.getenv("SIM_LAT0", "28.6139"))
_DEFAULT_LNG0 = float(os.getenv("SIM_LNG0", "77.2090"))


class Obstacle:
    """Simple circular obstacle for ultrasonic simulation."""

    def __init__(self, cx: float, cy: float, radius: float):
        self.cx = cx
        self.cy = cy
        self.radius = radius


class SensorSim:
    """Generates synthetic telemetry from a rover model.

    Parameters:
        lat0, lng0: GPS datum (field origin in WGS84)
        gps_noise_m: standard deviation of GPS position noise (meters)
        battery_start_v: initial battery voltage
        battery_drain_per_step: voltage drop per simulation step
        obstacles: list of Obstacle instances for ultrasonic distance
        anomaly_probability: chance of an NPK anomaly per reading
    """

    def __init__(
        self,
        lat0: float = _DEFAULT_LAT0,
        lng0: float = _DEFAULT_LNG0,
        gps_noise_m: float = 1.5,
        battery_start_v: float = 13.3,  # 4S LiFePO4, freshly charged and rested
        battery_drain_per_step: float = 0.01,
        obstacles: list[Obstacle] | None = None,
        anomaly_probability: float = 0.05,
    ):
        self.lat0 = lat0
        self.lng0 = lng0
        self.gps_noise_m = gps_noise_m
        self.battery_v = battery_start_v
        self.battery_drain_per_step = battery_drain_per_step
        self.obstacles = obstacles or []
        self.anomaly_probability = anomaly_probability
        self._step_count = 0

    # ------------------------------------------------------------------
    # NPK telemetry
    # ------------------------------------------------------------------

    def npk_payload(self) -> dict:
        """Generate a rover/npk payload with realistic nutrient values.

        Normal ranges (mg/kg): N 20-80, P 10-50, K 100-300, pH 5.5-7.5
        Anomalies push values outside these bands.
        """
        is_anomaly = random.random() < self.anomaly_probability

        if is_anomaly:
            n = random.uniform(0, 150)
            p = random.uniform(0, 100)
            k = random.uniform(0, 500)
            ph = random.uniform(3.0, 9.0)
        else:
            n = random.uniform(20, 80)
            p = random.uniform(10, 50)
            k = random.uniform(100, 300)
            ph = random.uniform(5.5, 7.5)

        return {
            "n": round(n, 2),
            "p": round(p, 2),
            "k": round(k, 2),
            "ph": round(ph, 2),
            "valid": 1,
        }

    # ------------------------------------------------------------------
    # GPS telemetry
    # ------------------------------------------------------------------

    def gps_payload(self, x: float, y: float) -> dict:
        """Generate a rover/gps payload from local coordinates.

        Adds Gaussian noise to simulate GPS inaccuracy.
        """
        noisy_x = x + random.gauss(0, self.gps_noise_m)
        noisy_y = y + random.gauss(0, self.gps_noise_m)
        lat, lng = local_to_latlng(noisy_x, noisy_y, self.lat0, self.lng0)
        return {
            "lat": round(lat, 7),
            "lng": round(lng, 7),
            "fix": 1,
        }

    # ------------------------------------------------------------------
    # Status telemetry
    # ------------------------------------------------------------------

    def _front_distance(self, x: float, y: float, theta: float) -> float:
        """Compute simulated ultrasonic distance to nearest obstacle (cm).

        Casts a ray from (x, y) in direction theta and returns distance to
        the nearest obstacle intersection, or 400 cm (max range) if none.
        """
        max_range_cm = 400.0
        min_dist = max_range_cm

        for obs in self.obstacles:
            # Vector from rover to obstacle centre
            dx = obs.cx - x
            dy = obs.cy - y
            # Project onto heading direction
            proj = dx * math.cos(theta) + dy * math.sin(theta)
            if proj <= 0:
                continue  # obstacle is behind
            # Perpendicular distance from ray to centre
            perp = abs(-dx * math.sin(theta) + dy * math.cos(theta))
            if perp < obs.radius:
                # Distance along ray to the obstacle surface
                dist_m = proj - math.sqrt(max(0, obs.radius**2 - perp**2))
                dist_cm = dist_m * 100.0
                if 0 < dist_cm < min_dist:
                    min_dist = dist_cm

        return round(min_dist, 1)

    def status_payload(self, x: float, y: float, theta: float) -> dict:
        """Generate a rover/status payload."""
        self._step_count += 1
        self.battery_v = max(
            10.5, self.battery_v - self.battery_drain_per_step
        )  # floor below the 11.0 V LiFePO4 cutoff so low-battery paths trigger
        front_cm = self._front_distance(x, y, theta)
        return {
            "battery_v": round(self.battery_v, 2),
            "front_distance_cm": front_cm,
        }
