"""Mission scheduler: queue and persist field missions with state tracking.

Provides an ordered queue of missions (scan, dose, return-to-base, custom)
that is persisted to a JSON file. The orchestrator queries get_current() each
loop to know what to execute, and calls advance()/fail_current() to progress.

Thread-safe: all public methods acquire a lock so the dashboard and orchestrator
can access concurrently. Pure stdlib (json persistence, no external deps).
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid

logger = logging.getLogger(__name__)

_VALID_TYPES = {"scan", "dose", "return_to_base", "custom"}
_ACTIVE_STATUSES = {"queued", "active"}


def within_operating_window(now_hour: int, start_hour: int, end_hour: int) -> bool:
    """Return True if ``now_hour`` falls inside the [start_hour, end_hour) window.

    Hours are 0-23. Handles windows that wrap past midnight (e.g. cool-hours
    22..6 means 22,23,0,1,..,5). A degenerate window where start == end is
    treated as "always allowed" (a full 24h window), which is the default
    behaviour when no cool-hours restriction is configured.
    """
    start_hour %= 24
    end_hour %= 24
    now_hour %= 24
    if start_hour == end_hour:
        return True  # full-day window / no restriction
    if start_hour < end_hour:
        return start_hour <= now_hour < end_hour
    # Wrapping window (crosses midnight).
    return now_hour >= start_hour or now_hour < end_hour


class MissionScheduler:
    """JSON-backed mission queue with lifecycle management.

    Mission dict structure::

        {
            "id": "M-<uuid_hex_8>",
            "type": "scan" | "dose" | "return_to_base" | "custom",
            "zone": {"waypoints": [...]} | {"bounds": (...)},
            "status": "queued" | "active" | "completed" | "cancelled" | "failed",
            "params": {...},
            "created_at": float (epoch),
            "started_at": float | None,
            "completed_at": float | None,
            "error": str | None
        }
    """

    def __init__(self, path: str = "missions.json", max_history: int = 100,
                 operating_window: tuple[int, int] | None = None):
        self.path = path
        self.max_history = max_history
        # Optional cool-hours window (start_hour, end_hour) in 0-23. When set,
        # a queued mission is only promoted to active inside this window (FC-02
        # cool-hours-only mode). None = always allowed.
        self.operating_window = operating_window
        self._lock = threading.Lock()
        self._missions: list[dict] = []
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load mission queue from disk if file exists."""
        if not os.path.exists(self.path):
            logger.info("MissionScheduler: no file at %s; starting fresh", self.path)
            return
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self._missions = data.get("missions", [])
            logger.info(
                "MissionScheduler: loaded %d missions from %s",
                len(self._missions), self.path,
            )
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                "MissionScheduler: failed to load %s (%s); starting fresh",
                self.path, exc,
            )
            self._missions = []

    def _save(self) -> None:
        """Atomically persist current state to disk (caller holds lock).

        Before writing, trims completed/failed/cancelled missions beyond
        max_history to prevent unbounded file growth on long-running systems.
        Keeps the most recent finished missions (by completed_at).
        """
        self._prune_history()
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"missions": self._missions}, fh, separators=(",", ":"))
            os.replace(tmp, self.path)
        except OSError as exc:
            logger.warning("MissionScheduler: save failed (%s)", exc)

    def _prune_history(self) -> None:
        """Remove oldest completed/failed/cancelled missions beyond max_history."""
        terminal = {"completed", "failed", "cancelled"}
        finished = [m for m in self._missions if m["status"] in terminal]
        if len(finished) <= self.max_history:
            return
        # Sort by completed_at descending; keep the most recent max_history
        finished.sort(key=lambda m: m.get("completed_at") or 0, reverse=True)
        keep_ids = {m["id"] for m in finished[: self.max_history]}
        self._missions = [
            m
            for m in self._missions
            if m["status"] not in terminal or m["id"] in keep_ids
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_mission(
        self,
        mission_type: str,
        zone: dict,
        params: dict | None = None,
    ) -> str:
        """Create a new mission and append to queue. Returns the mission ID."""
        if mission_type not in _VALID_TYPES:
            raise ValueError(
                f"Invalid mission type '{mission_type}'; expected one of {_VALID_TYPES}"
            )
        mid = "M-" + uuid.uuid4().hex[:8]
        mission: dict = {
            "id": mid,
            "type": mission_type,
            "zone": zone,
            "status": "queued",
            "params": params or {},
            "created_at": time.time(),
            "started_at": None,
            "completed_at": None,
            "error": None,
        }
        with self._lock:
            self._missions.append(mission)
            self._save()
        logger.info("MissionScheduler: added mission %s (type=%s)", mid, mission_type)
        return mid

    def cancel_mission(self, mission_id: str) -> bool:
        """Cancel a mission if it is queued or active. Returns True if cancelled."""
        with self._lock:
            for m in self._missions:
                if m["id"] == mission_id and m["status"] in _ACTIVE_STATUSES:
                    m["status"] = "cancelled"
                    m["completed_at"] = time.time()
                    self._save()
                    logger.info("MissionScheduler: cancelled %s", mission_id)
                    return True
            return False

    def is_operating_now(self, now_hour: int | None = None) -> bool:
        """True if a queued mission may start now per the cool-hours window.

        Always True when no operating_window is configured. ``now_hour`` may be
        supplied for testing; otherwise the local hour is used.
        """
        if self.operating_window is None:
            return True
        if now_hour is None:
            now_hour = time.localtime().tm_hour
        start_hour, end_hour = self.operating_window
        return within_operating_window(now_hour, start_hour, end_hour)

    def get_current(self) -> dict | None:
        """Return the current active mission, promoting queued if needed.

        Returns None if the queue has no actionable mission. A queued mission is
        only promoted to active when inside the cool-hours operating window
        (FC-02); an already-active mission keeps running regardless.
        """
        with self._lock:
            # First look for an already-active mission
            for m in self._missions:
                if m["status"] == "active":
                    return dict(m)
            # Refuse to start new work outside the cool-hours window.
            if not self.is_operating_now():
                return None
            # Promote the first queued mission to active
            for m in self._missions:
                if m["status"] == "queued":
                    m["status"] = "active"
                    m["started_at"] = time.time()
                    self._save()
                    logger.info("MissionScheduler: activated %s", m["id"])
                    return dict(m)
            return None

    def advance(self) -> None:
        """Mark the current active mission as completed."""
        with self._lock:
            for m in self._missions:
                if m["status"] == "active":
                    m["status"] = "completed"
                    m["completed_at"] = time.time()
                    self._save()
                    logger.info("MissionScheduler: completed %s", m["id"])
                    return

    def fail_current(self, reason: str = "") -> None:
        """Mark the current active mission as failed."""
        with self._lock:
            for m in self._missions:
                if m["status"] == "active":
                    m["status"] = "failed"
                    m["completed_at"] = time.time()
                    m["error"] = reason
                    self._save()
                    logger.info("MissionScheduler: failed %s (%s)", m["id"], reason)
                    return

    def list_missions(self, include_completed: bool = False) -> list[dict]:
        """Return a copy of the mission queue.

        By default only queued/active missions are returned.  Set
        include_completed=True to include completed, cancelled, and failed.
        """
        with self._lock:
            if include_completed:
                return [dict(m) for m in self._missions]
            return [
                dict(m) for m in self._missions
                if m["status"] in _ACTIVE_STATUSES
            ]
