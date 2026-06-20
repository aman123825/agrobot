"""ROS 2 package setup for agrobot_ros2."""
from setuptools import find_packages, setup

package_name = "agrobot_ros2"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/agrobot_launch.py"]),
        ("share/" + package_name + "/config", ["config/params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="AgroBot Team",
    maintainer_email="dev@agrobot.local",
    description="ROS 2 integration layer for the AgroBot agricultural rover",
    license="MIT",
    entry_points={
        "console_scripts": [
            "sensor_publisher = agrobot_ros2.sensor_publisher:main",
            "drive_subscriber = agrobot_ros2.drive_subscriber:main",
            "ai_node = agrobot_ros2.ai_node:main",
            "mission_node = agrobot_ros2.mission_node:main",
        ],
    },
)
