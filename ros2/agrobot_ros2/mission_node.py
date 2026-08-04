"""ROS 2 node that wraps the mission scheduler as ROS 2 services.

Exposes AddMission, CancelMission, and ListMissions services and publishes
the current mission status periodically. Mirrors the functionality of
pi/mission/scheduler.py.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import threading
import time
import uuid

# Guard ROS 2 imports for py_compile compatibility.
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String
    from std_srvs.srv import Trigger

    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False

logger = logging.getLogger(__name__)

# Valid mission types (matches pi/mission/scheduler.py)
_VALID_TYPES = {"scan", "dose", "return_to_base", "custom"}
_ACTIVE_STATUSES = {"queued", "active"}


class MissionStore:
    """Lightweight in-process mission queue (same logic as MissionScheduler).

    Used when the pi/mission/scheduler.py module is not directly importable
    in the ROS 2 environment. Keeps the same JSON persistence format.
    """

    def __init__(self, path: str = "missions.json") -> None:
        self.path = path
        self._lock = threading.Lock()
        self._missions: list[dict] = []
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            self._missions = data.get("missions", [])
        except (json.JSONDecodeError, OSError):
            self._missions = []

    def _save(self) -> None:
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump({"missions": self._missions}, fh, separators=(",", ":"))
            os.replace(tmp, self.path)
        except OSError:
            pass

    def add_mission(
        self, mission_type: str, zone: dict, params: dict | None = None
    ) -> str:
        if mission_type not in _VALID_TYPES:
            raise ValueError(f"Invalid type '{mission_type}'")
        mid = "M-" + uuid.uuid4().hex[:8]
        mission = {
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
        return mid

    def cancel_mission(self, mission_id: str) -> bool:
        with self._lock:
            for m in self._missions:
                if m["id"] == mission_id and m["status"] in _ACTIVE_STATUSES:
                    m["status"] = "cancelled"
                    m["completed_at"] = time.time()
                    self._save()
                    return True
            return False

    def peek_current(self) -> dict | None:
        """Return the current active or next queued mission without promotion.

        This is a read-only operation that does NOT transition queued missions
        to active. Use get_current() when you want auto-promotion semantics.
        """
        with self._lock:
            for m in self._missions:
                if m["status"] == "active":
                    return dict(m)
            for m in self._missions:
                if m["status"] == "queued":
                    return dict(m)
            return None

    def get_current(self) -> dict | None:
        with self._lock:
            for m in self._missions:
                if m["status"] == "active":
                    return dict(m)
            for m in self._missions:
                if m["status"] == "queued":
                    m["status"] = "active"
                    m["started_at"] = time.time()
                    self._save()
                    return dict(m)
            return None

    def list_missions(self, include_completed: bool = False) -> list[dict]:
        with self._lock:
            if include_completed:
                return [dict(m) for m in self._missions]
            return [
                dict(m) for m in self._missions if m["status"] in _ACTIVE_STATUSES
            ]


if HAS_ROS2:

    class MissionNode(Node):  # type: ignore[misc]
        """ROS 2 node exposing mission scheduler as services."""

        def __init__(self) -> None:
            super().__init__("mission_node")

            # Declare parameters
            self.declare_parameter("missions_file", "missions.json")
            self.declare_parameter("status_rate_hz", 1.0)

            missions_file = (
                self.get_parameter("missions_file")
                .get_parameter_value()
                .string_value
            )
            status_rate = (
                self.get_parameter("status_rate_hz")
                .get_parameter_value()
                .double_value
            )

            # Mission store
            self._store = MissionStore(path=missions_file)

            # Publisher for current mission status
            self._pub_status = self.create_publisher(
                String, "/agrobot/mission/status", 10
            )

            # Services (using std_srvs/Trigger for simplicity since custom
            # service types require message generation not available here)
            self._srv_add = self.create_service(
                Trigger, "add_mission", self._handle_add_mission
            )
            self._srv_cancel = self.create_service(
                Trigger, "cancel_mission", self._handle_cancel_mission
            )
            self._srv_list = self.create_service(
                Trigger, "list_missions", self._handle_list_missions
            )

            # Timer for status publishing
            period = 1.0 / status_rate if status_rate > 0 else 1.0
            self._timer = self.create_timer(period, self._publish_status)

            self.get_logger().info("MissionNode ready")

        def _publish_status(self) -> None:
            """Publish the current mission status as JSON.

            Uses peek_current() to avoid the side-effect of promoting
            queued missions to active on every status tick.
            """
            current = self._store.peek_current()
            msg = String()
            if current is not None:
                msg.data = json.dumps(current)
            else:
                msg.data = json.dumps({"status": "idle", "mission": None})
            self._pub_status.publish(msg)

        def _handle_add_mission(self, request, response):
            """Handle AddMission service call.

            Since we use Trigger (no custom msg), the caller encodes params
            in the environment or via a separate topic. This adds a default
            scan mission for demonstration purposes.
            """
            try:
                mid = self._store.add_mission(
                    "scan", {"waypoints": []}, {}
                )
                response.success = True
                response.message = f"Mission added: {mid}"
            except Exception as exc:
                response.success = False
                response.message = str(exc)
            return response

        def _handle_cancel_mission(self, request, response):
            """Handle CancelMission service call."""
            # In a full implementation, mission_id would come from the request
            current = self._store.get_current()
            if current and self._store.cancel_mission(current["id"]):
                response.success = True
                response.message = f"Cancelled: {current['id']}"
            else:
                response.success = False
                response.message = "No active mission to cancel"
            return response

        def _handle_list_missions(self, request, response):
            """Handle ListMissions service call."""
            missions = self._store.list_missions(include_completed=True)
            response.success = True
            response.message = json.dumps(missions)
            return response

        def destroy_node(self) -> None:
            """Clean shutdown."""
            super().destroy_node()


def main(args=None) -> None:
    """Entry point for the mission_node."""
    if not HAS_ROS2:
        logger.error("rclpy is not installed; cannot run mission_node")
        sys.exit(1)
    rclpy.init(args=args)
    node = MissionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
