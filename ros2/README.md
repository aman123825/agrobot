# AgroBot ROS 2 Integration Layer

Optional ROS 2 package that bridges the AgroBot rover's Python services into
the ROS 2 ecosystem, enabling integration with navigation stacks (Nav2),
visualization (RViz2), and other ROS 2-based tooling.

## Package Structure

```
ros2/
  agrobot_ros2/
    __init__.py
    sensor_publisher.py   - Bridges MQTT telemetry to ROS 2 topics
    drive_subscriber.py   - Converts /cmd_vel to serial motor commands
    ai_node.py            - Runs obstacle/weed detection on camera images
    mission_node.py       - Exposes mission scheduler as ROS 2 services
  launch/
    agrobot_launch.py     - Launches all nodes with params
  config/
    params.yaml           - Default node parameters
  resource/
    agrobot_ros2          - Ament resource index marker
  package.xml
  setup.py
  setup.cfg
```

## Prerequisites

- ROS 2 Humble (or later) installed
- Python 3.10+
- paho-mqtt (`pip install paho-mqtt`)
- pyserial (`pip install pyserial`)

## Installation

```bash
# From your ROS 2 workspace src/ directory:
ln -s /path/to/agrobot/ros2 src/agrobot_ros2

# Build
colcon build --packages-select agrobot_ros2

# Source
source install/setup.bash
```

## Running

### Launch all nodes

```bash
ros2 launch agrobot_ros2 agrobot_launch.py
```

### Launch with custom parameters

```bash
ros2 launch agrobot_ros2 agrobot_launch.py params_file:=/path/to/custom_params.yaml
```

### Run individual nodes

```bash
ros2 run agrobot_ros2 sensor_publisher
ros2 run agrobot_ros2 drive_subscriber
ros2 run agrobot_ros2 ai_node
ros2 run agrobot_ros2 mission_node
```

## Topics

| Topic | Type | Direction | Description |
|-------|------|-----------|-------------|
| `/agrobot/gps` | sensor_msgs/NavSatFix | Published | GPS fix from rover |
| `/agrobot/temperature` | sensor_msgs/Temperature | Published | DHT22 temperature |
| `/agrobot/velocity` | geometry_msgs/TwistStamped | Published | Current velocity |
| `/agrobot/odom` | nav_msgs/Odometry | Published | Wheel odometry |
| `/agrobot/npk` | std_msgs/Float32MultiArray | Published | Soil NPK values |
| `/cmd_vel` | geometry_msgs/Twist | Subscribed | Drive commands |
| `/agrobot/camera/image_raw` | sensor_msgs/Image | Subscribed | Camera feed |
| `/agrobot/obstacle_detected` | std_msgs/Bool | Published | Obstacle flag |
| `/agrobot/weed_detected` | std_msgs/Bool | Published | Weed flag |
| `/agrobot/detection_count` | std_msgs/Int32 | Published | Total detections |
| `/agrobot/mission/status` | std_msgs/String | Published | Current mission JSON |

## Services

| Service | Type | Description |
|---------|------|-------------|
| `add_mission` | std_srvs/Trigger | Add a scan mission to the queue |
| `cancel_mission` | std_srvs/Trigger | Cancel the current active mission |
| `list_missions` | std_srvs/Trigger | List all missions (JSON in message) |

## Parameters

See `config/params.yaml` for all available parameters and their defaults.

## Architecture

The ROS 2 layer acts as a bridge between the existing Pi services and the
ROS 2 ecosystem. It does not replace the core Pi modules but rather wraps
them to provide standard ROS 2 interfaces:

- **sensor_publisher** connects to the same MQTT broker that the ESP32
  publishes telemetry to and re-publishes as typed ROS 2 messages.
- **drive_subscriber** receives standard ROS 2 velocity commands and
  translates them into the HMAC-signed serial protocol the ESP32 expects.
- **ai_node** reuses the detection models from `pi/ai/` and publishes
  results on standard topics.
- **mission_node** wraps the mission scheduler logic and exposes it via
  ROS 2 services for integration with behavior trees or planners.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_HOST` | localhost | MQTT broker hostname |
| `MQTT_PORT` | 1883 | MQTT broker port |
| `ROVER_ID` | rover01 | Rover identifier for MQTT topics |
| `ESP32_SERIAL` | /dev/ttyUSB0 | Serial port for ESP32 |
| `AGRO_LINK_KEY` | (empty) | HMAC key for command signing |
| `MODEL_DIR` | models | Path to AI model files |
