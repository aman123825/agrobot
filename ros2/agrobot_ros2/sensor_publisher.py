"""ROS 2 node that bridges MQTT sensor telemetry to standard ROS 2 topics.

Connects to the same MQTT broker as pi/bridge/mqtt_client.py and republishes
sensor data (GPS, temperature, velocity, odometry, NPK) as typed ROS 2
messages so downstream ROS navigation and monitoring stacks can consume them.
"""
from __future__ import annotations

import json
import logging
import math
import os
import sys
import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Guard all ROS 2 imports so py_compile passes without rclpy installed.
try:
    import rclpy
    from rclpy.node import Node
    from geometry_msgs.msg import TwistStamped
    from nav_msgs.msg import Odometry
    from sensor_msgs.msg import NavSatFix, Temperature
    from std_msgs.msg import Float32MultiArray

    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False

# Guard paho-mqtt (may not be installed in all environments).
try:
    import paho.mqtt.client as mqtt

    HAS_MQTT = True
except ImportError:
    HAS_MQTT = False

logger = logging.getLogger(__name__)

# Default MQTT configuration (mirrors pi/config.py)
_MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
_MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
_ROVER_ID = os.getenv("ROVER_ID", "rover01")


def _topic(suffix: str) -> str:
    """Build an MQTT topic string for this rover."""
    return f"rover/{_ROVER_ID}/{suffix}"


if HAS_ROS2:

    class SensorPublisherNode(Node):  # type: ignore[misc]
        """Publishes MQTT sensor data as ROS 2 messages."""

        def __init__(self) -> None:
            super().__init__("sensor_publisher")

            # Declare parameters
            self.declare_parameter("mqtt_host", _MQTT_HOST)
            self.declare_parameter("mqtt_port", _MQTT_PORT)
            self.declare_parameter("rover_id", _ROVER_ID)
            self.declare_parameter("publish_rate_hz", 10.0)

            mqtt_host = (
                self.get_parameter("mqtt_host").get_parameter_value().string_value
            )
            mqtt_port = (
                self.get_parameter("mqtt_port")
                .get_parameter_value()
                .integer_value
            )
            rover_id = (
                self.get_parameter("rover_id").get_parameter_value().string_value
            )
            publish_rate = (
                self.get_parameter("publish_rate_hz")
                .get_parameter_value()
                .double_value
            )

            # Publishers
            self._pub_gps = self.create_publisher(NavSatFix, "/agrobot/gps", 10)
            self._pub_temp = self.create_publisher(
                Temperature, "/agrobot/temperature", 10
            )
            self._pub_vel = self.create_publisher(
                TwistStamped, "/agrobot/velocity", 10
            )
            self._pub_odom = self.create_publisher(Odometry, "/agrobot/odom", 10)
            self._pub_npk = self.create_publisher(
                Float32MultiArray, "/agrobot/npk", 10
            )

            # Latest data cache (written by MQTT thread, read by timer)
            self._lock = threading.Lock()
            self._gps_data: dict | None = None
            self._temp_data: dict | None = None
            self._vel_data: dict | None = None
            self._odom_data: dict | None = None
            self._npk_data: dict | None = None

            # MQTT setup
            if HAS_MQTT:
                self._mqtt = mqtt.Client()
                self._mqtt.on_message = self._on_mqtt_message
                try:
                    self._mqtt.connect(mqtt_host, mqtt_port)
                    self._mqtt.subscribe(f"rover/{rover_id}/#")
                    self._mqtt.loop_start()
                    self.get_logger().info(
                        f"Connected to MQTT at {mqtt_host}:{mqtt_port}"
                    )
                except Exception as exc:
                    self.get_logger().warning(f"MQTT connection failed: {exc}")
            else:
                self.get_logger().warning(
                    "paho-mqtt not available; sensor data will not be received"
                )

            # Timer callback to publish cached data
            period = 1.0 / publish_rate if publish_rate > 0 else 0.1
            self._timer = self.create_timer(period, self._timer_callback)

        def _on_mqtt_message(self, _client, _userdata, msg) -> None:
            """Handle incoming MQTT messages and cache parsed data."""
            try:
                payload = json.loads(msg.payload.decode(errors="ignore"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return

            topic = msg.topic
            with self._lock:
                if topic.endswith("/gps"):
                    self._gps_data = payload
                elif topic.endswith("/temperature"):
                    self._temp_data = payload
                elif topic.endswith("/velocity"):
                    self._vel_data = payload
                elif topic.endswith("/odom"):
                    self._odom_data = payload
                elif topic.endswith("/npk"):
                    self._npk_data = payload

        def _timer_callback(self) -> None:
            """Publish cached sensor data as ROS 2 messages."""
            now = self.get_clock().now().to_msg()

            with self._lock:
                gps = self._gps_data
                temp = self._temp_data
                vel = self._vel_data
                odom = self._odom_data
                npk = self._npk_data

            if gps is not None:
                msg = NavSatFix()
                msg.header.stamp = now
                msg.header.frame_id = "gps_link"
                msg.latitude = float(gps.get("lat", 0.0))
                msg.longitude = float(gps.get("lon", 0.0))
                msg.altitude = float(gps.get("alt", 0.0))
                self._pub_gps.publish(msg)

            if temp is not None:
                msg = Temperature()
                msg.header.stamp = now
                msg.header.frame_id = "base_link"
                msg.temperature = float(temp.get("celsius", 0.0))
                msg.variance = 0.0
                self._pub_temp.publish(msg)

            if vel is not None:
                msg = TwistStamped()
                msg.header.stamp = now
                msg.header.frame_id = "base_link"
                msg.twist.linear.x = float(vel.get("linear_x", 0.0))
                msg.twist.angular.z = float(vel.get("angular_z", 0.0))
                self._pub_vel.publish(msg)

            if odom is not None:
                msg = Odometry()
                msg.header.stamp = now
                msg.header.frame_id = "odom"
                msg.child_frame_id = "base_link"
                msg.pose.pose.position.x = float(odom.get("x", 0.0))
                msg.pose.pose.position.y = float(odom.get("y", 0.0))
                yaw = float(odom.get("yaw", 0.0))
                msg.pose.pose.orientation.z = math.sin(yaw / 2.0)
                msg.pose.pose.orientation.w = math.cos(yaw / 2.0)
                msg.twist.twist.linear.x = float(odom.get("vx", 0.0))
                msg.twist.twist.angular.z = float(odom.get("wz", 0.0))
                self._pub_odom.publish(msg)

            if npk is not None:
                msg = Float32MultiArray()
                msg.data = [
                    float(npk.get("n", 0.0)),
                    float(npk.get("p", 0.0)),
                    float(npk.get("k", 0.0)),
                ]
                self._pub_npk.publish(msg)

        def destroy_node(self) -> None:
            """Clean up MQTT on shutdown."""
            if HAS_MQTT and hasattr(self, "_mqtt"):
                self._mqtt.loop_stop()
                self._mqtt.disconnect()
            super().destroy_node()


def main(args=None) -> None:
    """Entry point for the sensor_publisher node."""
    if not HAS_ROS2:
        logger.error("rclpy is not installed; cannot run sensor_publisher node")
        sys.exit(1)
    rclpy.init(args=args)
    node = SensorPublisherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
