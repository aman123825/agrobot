"""Per-plant database with health history tracking.

Stores a persistent JSON file mapping plant IDs to GPS positions and
observation histories. Uses spatial clustering to match new detections to
existing plants -- if a detection falls within a configurable tolerance of an
existing plant, it is added as a new observation; otherwise a new plant record
is created.

Thread-safe: all public methods acquire a lock so the orchestrator and pipeline
can access concurrently. Pure stdlib (json persistence, no SQLite).
"""
from __future__ import annotations

import json
import logging
import math
import os
import threading
import time
import uuid

logger = logging.getLogger(__name__)

# Default spatial tolerance in meters (~0.5 m works well with vision-tagged
# positions from plant_tagging.py which localize to ~10-20 cm).
DEFAULT_TOLERANCE_M = 0.5

# WGS84 mean radius for haversine approximation.
_EARTH_R = 6378137.0


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Approximate great-circle distance in meters between two lat/lng pairs."""
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return _EARTH_R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class PlantDB:
    """JSON-backed per-plant health history database.

    Data structure on disk::

        {
          "plants": {
            "<plant_id>": {
              "lat": float,
              "lng": float,
              "created": float (epoch),
              "observations": [
                {
                  "ts": float (epoch),
                  "disease_class": str,
                  "confidence": float,
                  "npk": {"n": float, "p": float, "k": float} | null,
                  "soil_moisture": float | null,
                  "notes": str
                },
                ...
              ]
            }
          }
        }
    """

    def __init__(self, path: str = "plant_db.json",
                 tolerance_m: float = DEFAULT_TOLERANCE_M,
                 flush_interval_s: float = 30.0):
        self.path = path
        self.tolerance_m = tolerance_m
        self.flush_interval_s = flush_interval_s
        self._lock = threading.Lock()
        self._dirty = False
        self._last_flush = 0.0
        self._plants: dict[str, dict] = {}
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load plant database from disk if it exists."""
        if not os.path.exists(self.path):
            logger.info("PlantDB: no existing file at %s; starting fresh", self.path)
            return
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self._plants = data.get("plants", {})
            logger.info("PlantDB: loaded %d plants from %s", len(self._plants), self.path)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("PlantDB: failed to load %s (%s); starting fresh", self.path, exc)
            self._plants = {}

    def flush(self) -> None:
        """Write current state to disk (unconditionally)."""
        with self._lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        """Internal flush (caller holds lock)."""
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"plants": self._plants}, fh, separators=(",", ":"))
            os.replace(tmp, self.path)
            self._dirty = False
            self._last_flush = time.time()
        except OSError as exc:
            logger.warning("PlantDB: flush failed (%s)", exc)

    def _maybe_flush(self) -> None:
        """Flush if dirty and enough time has elapsed (caller holds lock)."""
        if self._dirty and (time.time() - self._last_flush) >= self.flush_interval_s:
            self._flush_locked()

    # ------------------------------------------------------------------
    # Spatial lookup
    # ------------------------------------------------------------------

    def _find_nearest(self, lat: float, lng: float) -> tuple[str | None, float]:
        """Find nearest plant within tolerance. Returns (plant_id, distance_m).

        Returns (None, inf) if no plant is within tolerance.
        """
        best_id: str | None = None
        best_dist = float("inf")
        for pid, rec in self._plants.items():
            d = _haversine_m(lat, lng, rec["lat"], rec["lng"])
            if d < best_dist:
                best_dist = d
                best_id = pid
        if best_dist <= self.tolerance_m:
            return (best_id, best_dist)
        return (None, best_dist)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def record_observation(
        self,
        lat: float,
        lng: float,
        disease_class: str = "unknown",
        confidence: float = 0.0,
        npk: dict[str, float] | None = None,
        soil_moisture: float | None = None,
        notes: str = "",
    ) -> str:
        """Record a plant observation, matching or creating a plant record.

        Returns the plant_id (existing or new).
        """
        with self._lock:
            pid, dist = self._find_nearest(lat, lng)
            if pid is None:
                # New plant
                pid = "P-" + uuid.uuid4().hex[:8]
                self._plants[pid] = {
                    "lat": lat,
                    "lng": lng,
                    "created": time.time(),
                    "observations": [],
                }
                logger.info("PlantDB: new plant %s at (%.6f, %.6f)", pid, lat, lng)
            else:
                logger.debug("PlantDB: matched %s (%.2f m away)", pid, dist)

            obs = {
                "ts": time.time(),
                "disease_class": disease_class,
                "confidence": round(confidence, 4),
                "npk": npk,
                "soil_moisture": soil_moisture,
                "notes": notes,
            }
            self._plants[pid]["observations"].append(obs)
            self._dirty = True
            self._maybe_flush()
            return pid

    def get_plant(self, plant_id: str) -> dict | None:
        """Return a copy of a single plant record, or None."""
        with self._lock:
            rec = self._plants.get(plant_id)
            return json.loads(json.dumps(rec)) if rec else None

    def get_all_plants(self) -> dict[str, dict]:
        """Return a deep copy of all plant records."""
        with self._lock:
            return json.loads(json.dumps(self._plants))

    @property
    def plant_count(self) -> int:
        """Number of tracked plants."""
        with self._lock:
            return len(self._plants)

    def recent_observations(self, limit: int = 20) -> list[dict]:
        """Return the most recent observations across all plants (newest first)."""
        with self._lock:
            all_obs: list[dict] = []
            for pid, rec in self._plants.items():
                for obs in rec["observations"]:
                    all_obs.append({"plant_id": pid, "lat": rec["lat"],
                                    "lng": rec["lng"], **obs})
            all_obs.sort(key=lambda o: o["ts"], reverse=True)
            return all_obs[:limit]

    def health_trend(self, plant_id: str) -> list[dict]:
        """Return chronological observations for a plant (for trend display)."""
        with self._lock:
            rec = self._plants.get(plant_id)
            if rec is None:
                return []
            return list(rec["observations"])

    def close(self) -> None:
        """Flush any pending writes."""
        with self._lock:
            if self._dirty:
                self._flush_locked()
        logger.info("PlantDB: closed (%d plants)", len(self._plants))
