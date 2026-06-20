"""ROS 2 node that subscribes to /cmd_vel and drives the rover motors.

Converts geometry_msgs/Twist (linear.x, angular.z) to differential-drive
left/right wheel PWM values using the same kinematic model as
pi/sim/rover_model.py, then transmits HMAC-signed serial commands to the
ESP32 via the same protocol as pi/bridge/serial_bridge.py.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import os
import sys
import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Guard ROS 2 imports for py_compile compatibility.
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import Twist

    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False

# Guard pyserial (may not be installed in all environments).
try:
    import serial

    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

logger = logging.getLogger(__name__)

# Security constants (mirrors pi/security.py)
_LINK_KEY = os.getenv("AGRO_LINK_KEY", "").encode()
_TRUNC_HEX = 32
_COUNTER_PATH = os.getenv(
    "AGRO_COUNTER_FILE", os.path.expanduser("~/.agrorover_counter")
)
_counter_lock = threading.Lock()


def _next_counter() -> int:
    """Monotonic counter matching pi/security.py protocol."""
    with _counter_lock:
        last = 0
        try:
            with open(_COUNTER_PATH, encoding="utf-8") as fh:
                last = int(fh.read().strip() or "0")
        except (OSError, ValueError):
            last = 0
        nxt = max(last + 1, int(time.time() * 1000))
        try:
            tmp = f"{_COUNTER_PATH}.tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(str(nxt))
            os.replace(tmp, _COUNTER_PATH)
        except OSError:
            pass
        return nxt


def _sign_command(command: str) -> str:
    """Sign a command using HMAC-SHA256 (matches firmware secure_link)."""
    if not _LINK_KEY:
        return command
    counter = _next_counter()
    msg = f"v1|{counter}|{command}"
    tag = hmac.new(_LINK_KEY, msg.encode(), hashlib.sha256).hexdigest()[:_TRUNC_HEX]
    return f"{msg}|{tag}"


if HAS_ROS2:

    class DriveSubscriberNode(Node):  # type: ignore[misc]
        """Subscribes to /cmd_vel and drives the rover via serial."""

        def __init__(self) -> None:
            super().__init__("drive_subscriber")

            # Declare parameters
            self.declare_parameter("serial_port", "/dev/ttyUSB0")
            self.declare_parameter("wheel_separation", 0.30)
            self.declare_parameter("max_speed", 0.5)
            self.declare_parameter("serial_baud", 115200)

            self._serial_port = (
                self.get_parameter("serial_port")
                .get_parameter_value()
                .string_value
            )
            self._wheel_sep = (
                self.get_parameter("wheel_separation")
                .get_parameter_value()
                .double_value
            )
            self._max_speed = (
                self.get_parameter("max_speed")
                .get_parameter_value()
                .double_value
            )
            baud = (
                self.get_parameter("serial_baud")
                .get_parameter_value()
                .integer_value
            )

            # Serial connection
            self._ser = None
            if HAS_SERIAL:
                try:
                    self._ser = serial.Serial(self._serial_port, baud, timeout=0.1)
                    self.get_logger().info(
                        f"Serial connected: {self._serial_port} @ {baud}"
                    )
                except Exception as exc:
                    self.get_logger().warning(f"Serial open failed: {exc}")
            else:
                self.get_logger().warning(
                    "pyserial not available; drive commands will not be sent"
                )

            # Subscribe to /cmd_vel
            self._sub = self.create_subscription(
                Twist, "/cmd_vel", self._cmd_vel_callback, 10
            )

        def _cmd_vel_callback(self, msg: Twist) -> None:
            """Convert Twist to differential drive PWM and send via serial."""
            linear_x = msg.linear.x
            angular_z = msg.angular.z

            # Differential drive kinematics
            v_left = linear_x - angular_z * self._wheel_sep / 2.0
            v_right = linear_x + angular_z * self._wheel_sep / 2.0

            # Map speed to PWM (0-255)
            pwm_left = int(
                max(0, min(255, abs(v_left) / self._max_speed * 255))
            )
            pwm_right = int(
                max(0, min(255, abs(v_right) / self._max_speed * 255))
            )

            # Determine direction
            dir_left = "F" if v_left >= 0 else "B"
            dir_right = "F" if v_right >= 0 else "B"

            command = f"DRIVE:{dir_left}{pwm_left},{dir_right}{pwm_right}"
            self._send_command(command)

        def _send_command(self, command: str) -> None:
            """Sign and transmit a command over serial."""
            payload = _sign_command(command)
            if self._ser is not None:
                try:
                    self._ser.write(f"{payload}\n".encode())
                except Exception as exc:
                    self.get_logger().error(f"Serial write failed: {exc}")
            else:
                self.get_logger().debug(
                    f"Command (no serial): {payload}"
                )

        def destroy_node(self) -> None:
            """Close serial on shutdown."""
            if self._ser is not None:
                self._ser.close()
            super().destroy_node()


def main(args=None) -> None:
    """Entry point for the drive_subscriber node."""
    if not HAS_ROS2:
        logger.error("rclpy is not installed; cannot run drive_subscriber node")
        sys.exit(1)
    rclpy.init(args=args)
    node = DriveSubscriberNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
