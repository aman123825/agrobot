"""ROS 2 node that runs AI detection on camera images.

Subscribes to sensor_msgs/Image, runs obstacle and weed detection (matching
the pi/ai/ module patterns), and publishes detection results as boolean flags
and a detection count.
"""
from __future__ import annotations

import logging
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Guard ROS 2 imports for py_compile compatibility.
try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from std_msgs.msg import Bool, Int32

    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False

logger = logging.getLogger(__name__)


if HAS_ROS2:

    class AiDetectionNode(Node):  # type: ignore[misc]
        """Processes camera images for obstacle and weed detection."""

        def __init__(self) -> None:
            super().__init__("ai_node")

            # Declare parameters
            self.declare_parameter("model_dir", "models")
            self.declare_parameter("use_coral", True)
            self.declare_parameter("confidence_threshold", 0.5)

            self._model_dir = (
                self.get_parameter("model_dir")
                .get_parameter_value()
                .string_value
            )
            self._use_coral = (
                self.get_parameter("use_coral")
                .get_parameter_value()
                .bool_value
            )
            self._threshold = (
                self.get_parameter("confidence_threshold")
                .get_parameter_value()
                .double_value
            )

            # Publishers
            self._pub_obstacle = self.create_publisher(
                Bool, "/agrobot/obstacle_detected", 10
            )
            self._pub_weed = self.create_publisher(
                Bool, "/agrobot/weed_detected", 10
            )
            self._pub_count = self.create_publisher(
                Int32, "/agrobot/detection_count", 10
            )

            # Subscriber for camera images
            self._sub_image = self.create_subscription(
                Image,
                "/agrobot/camera/image_raw",
                self._image_callback,
                10,
            )

            # Detection state
            self._detection_count = 0
            self._models_loaded = False
            self._load_models()

        def _load_models(self) -> None:
            """Attempt to load detection models (pi/ai/ pattern)."""
            try:
                # Add pi directory to path for imports if available
                pi_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "pi",
                )
                if os.path.isdir(pi_path) and pi_path not in sys.path:
                    sys.path.insert(0, pi_path)

                # Attempt to import detection modules
                from ai import obstacle_detection, weed_detection  # noqa: F401

                self._models_loaded = True
                self.get_logger().info("AI models loaded successfully")
            except ImportError as exc:
                self._models_loaded = False
                self.get_logger().warning(
                    f"AI modules not available ({exc}); detection disabled"
                )

        def _image_callback(self, msg: Image) -> None:
            """Process an incoming camera image for detections."""
            obstacle_detected = False
            weed_detected = False

            if self._models_loaded:
                try:
                    from ai import obstacle_detection, weed_detection

                    # Convert ROS Image to numpy-like data
                    # (In production, use cv_bridge; here we pass raw bytes)
                    image_data = bytes(msg.data)
                    width = msg.width
                    height = msg.height

                    # Run obstacle detection
                    obstacle_result = obstacle_detection.detect(
                        image_data, width, height
                    )
                    obstacle_detected = bool(obstacle_result)

                    # Run weed detection
                    weed_result = weed_detection.detect(image_data, width, height)
                    weed_detected = bool(weed_result)

                    if obstacle_detected or weed_detected:
                        self._detection_count += 1

                except Exception as exc:
                    self.get_logger().debug(f"Detection error: {exc}")

            # Publish results
            obstacle_msg = Bool()
            obstacle_msg.data = obstacle_detected
            self._pub_obstacle.publish(obstacle_msg)

            weed_msg = Bool()
            weed_msg.data = weed_detected
            self._pub_weed.publish(weed_msg)

            count_msg = Int32()
            count_msg.data = self._detection_count
            self._pub_count.publish(count_msg)


def main(args=None) -> None:
    """Entry point for the ai_node."""
    if not HAS_ROS2:
        logger.error("rclpy is not installed; cannot run ai_node")
        return
    rclpy.init(args=args)
    node = AiDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
