"""ROS 2 launch file for all AgroBot nodes.

Starts sensor_publisher, drive_subscriber, ai_node, and mission_node
with configurable parameters loaded from config/params.yaml.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Guard launch imports for py_compile compatibility.
try:
    from launch import LaunchDescription
    from launch.actions import DeclareLaunchArgument
    from launch.substitutions import LaunchConfiguration
    from launch_ros.actions import Node

    HAS_LAUNCH = True
except ImportError:
    HAS_LAUNCH = False


def generate_launch_description():
    """Generate the launch description for all AgroBot ROS 2 nodes."""
    if not HAS_LAUNCH:
        raise RuntimeError("launch_ros is not installed")

    # Path to default parameters file
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_params = os.path.join(pkg_dir, "config", "params.yaml")

    # Declare launch arguments
    params_arg = DeclareLaunchArgument(
        "params_file",
        default_value=default_params,
        description="Path to the parameters YAML file",
    )

    # Node definitions
    sensor_node = Node(
        package="agrobot_ros2",
        executable="sensor_publisher",
        name="sensor_publisher",
        parameters=[LaunchConfiguration("params_file")],
        output="screen",
    )

    drive_node = Node(
        package="agrobot_ros2",
        executable="drive_subscriber",
        name="drive_subscriber",
        parameters=[LaunchConfiguration("params_file")],
        output="screen",
    )

    ai_node = Node(
        package="agrobot_ros2",
        executable="ai_node",
        name="ai_node",
        parameters=[LaunchConfiguration("params_file")],
        output="screen",
    )

    mission_node = Node(
        package="agrobot_ros2",
        executable="mission_node",
        name="mission_node",
        parameters=[LaunchConfiguration("params_file")],
        output="screen",
    )

    return LaunchDescription([
        params_arg,
        sensor_node,
        drive_node,
        ai_node,
        mission_node,
    ])
