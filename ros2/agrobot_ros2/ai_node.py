"""ROS 2 node that runs AI detection on camera images.

Subscribes to sensor_msgs/Image, runs obstacle and weed detection (matching
the pi/ai/ module patterns), and publishes detection results as boolean flags
and a detection count.
"""
from __future__ import annotations

import logging
import os
import sys

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
            """Load detection models using the pi/ai/ detector classes."""
            self._obstacle = None
            self._weed = None
            try:
                pi_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    "pi",
                )
                if os.path.isdir(pi_path) and pi_path not in sys.path:
                    sys.path.insert(0, pi_path)

                from ai.obstacle_detection import ObstacleDetector
                from ai.weed_detection import WeedDetector

                self._obstacle = ObstacleDetector(use_coral=self._use_coral)
                self._weed = WeedDetector(conf_threshold=self._threshold)
                self._obstacle.load()
                self._weed.load()
                self._models_loaded = True
                self.get_logger().info("AI detector classes initialized")
            except ImportError as exc:
                self._models_loaded = False
                self.get_logger().warning(
                    f"AI modules not available ({exc}); detection disabled"
                )

        def _image_callback(self, msg: Image) -> None:
            """Process an incoming camera image for detections."""
            obstacle_detected = False
            weed_detected = False

            if self._models_loaded and self._obstacle is not None:
                try:
                    import numpy as np

                    # Reconstruct an HxWxC frame from the ROS Image buffer.
                    flat = np.frombuffer(bytes(msg.data), dtype=np.uint8)
                    px = msg.width * msg.height
                    channels = (flat.size // px) if px else 0
                    if px and channels:
                        frame = flat.reshape((msg.height, msg.width, channels))
                        dets = self._obstacle.detect(frame)
                        obstacle_detected = self._obstacle.should_stop(dets)
                        weed_detected = self._weed.detect(frame)
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
        sys.exit(1)
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
