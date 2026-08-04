"""Central configuration for the Raspberry Pi services.

Pin numbers use BCM numbering and mirror docs/circuit-diagram.md §3.
Secrets (MQTT creds, Telegram token) should come from environment variables,
never be committed.
"""
import os

# --- MQTT (Mosquitto runs locally on the Pi) ---
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_TLS = os.getenv("MQTT_TLS", "0") == "1"
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883" if MQTT_TLS else "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_CA_CERT = os.getenv("MQTT_CA_CERT", "")  # path to broker CA when TLS is on
ROVER_ID = os.getenv("ROVER_ID", "rover01")
TOPICS = {
    "npk": f"rover/{ROVER_ID}/npk",
    "gps": f"rover/{ROVER_ID}/gps",
    "status": f"rover/{ROVER_ID}/status",
    "alert": f"rover/{ROVER_ID}/alert",
    "health": f"rover/{ROVER_ID}/health",
}

# --- Serial link to ESP32 (via CP2102) ---
SERIAL_PORT = os.getenv("ESP32_SERIAL", "/dev/ttyUSB0")
SERIAL_BAUD = 115200

# --- BCM GPIO map (circuit §3, conflicts resolved) ---
GPIO = {
    "encoder_left": 17,
    "encoder_right": 27,  # moved off GPIO18 to free the PWM/DMA pin for the LED strip
    "ds18b20": 24,        # OneWire (also needs dtoverlay=w1-gpio)
    "float_sensor": 25,
    "rain_sensor": 26,
    "ws2812b": 18,        # GPIO18 = hardware PWM/DMA; required by rpi_ws281x (GPIO23 won't work)
    "btn_up": 5, "btn_down": 6, "btn_left": 12, "btn_right": 16,
    "mode_sel_a": 20, "mode_sel_b": 21,
    # Aimed-spray pan/tilt servos (FC-01). Hardware-PWM-capable pins.
    "servo_pan": 13,      # GPIO13 (PWM1) -> pan SG90 (lateral aim)
    "servo_tilt": 19,     # GPIO19 (PWM1) -> tilt SG90 (height aim)
}

# --- I2C addresses (circuit §4.1) ---
I2C_ADDR = {
    "ina219": 0x40,
    "mpu6050": 0x68,
    "vl53l1x": 0x29,
    "ssd1306": 0x3C,
    "pcf8574": 0x20,
    "ads1115": 0x48,
}

# --- Models ---
MODEL_DIR = os.getenv("MODEL_DIR", "models")
# Primary edge-AI: Pi 5 + Hailo-8 AI HAT+ (.hef models, HailoRT). Detectors try
# Hailo first, then fall back to the Coral/CPU TFLite path below.
USE_HAILO = os.getenv("USE_HAILO", "1") == "1"
# Coral USB Edge TPU fallback (`*_edgetpu.tflite`); still the working prototype
# path and the CPU-INT8 fallback for machines without an accelerator.
USE_CORAL = os.getenv("USE_CORAL", "1") == "1"
# OTA manifest URL (docs/UPGRADES.md §8; empty = OTA disabled). Consumed by
# the standalone pi/ai/model_ota.py oneshot, listed here for discoverability.
MODEL_MANIFEST_URL = os.getenv("MODEL_MANIFEST_URL", "")

# --- Odometry / EKF (docs/UPGRADES.md §5) ---
TRACK_WIDTH_M = float(os.getenv("TRACK_WIDTH_M", "0.35"))  # wheel centre-to-centre
GPS_VAR_M2 = float(os.getenv("GPS_VAR_M2", "2.5"))  # Neo-6M ~1.5 m sigma; RTK ~0.0001

# --- Active-learning frame capture (docs/UPGRADES.md §8) ---
CAPTURE_DIR = os.getenv("CAPTURE_DIR", "captures")

# --- Telegram alerts + two-way control (docs/UPGRADES.md §9) ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
# Comma-separated chat IDs allowed to send inbound commands (/stop, /status,
# /photo, /summary). Empty = two-way control disabled (fail closed).
TELEGRAM_ALLOWED_CHAT_IDS = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "")

# --- Field-health telemetry (docs/farmer-needs-and-durability.md §2.2) ---
HEALTH_PERIOD_S = float(os.getenv("HEALTH_PERIOD_S", "30"))
BOOT_COUNTER_PATH = os.getenv("BOOT_COUNTER_PATH", "~/.agrirover_boots")
HEALTH_DISK_PATH = os.getenv("HEALTH_DISK_PATH", "/")

# --- Chemical-savings tracker (docs/farmer-needs-and-durability.md §1.3) ---
SAVINGS_PATH = os.getenv("SAVINGS_PATH", "savings.jsonl")
SPRAY_FLOW_ML_S = float(os.getenv("SPRAY_FLOW_ML_S", "30"))  # calibrate per nozzle
BASELINE_L_PER_ACRE = float(os.getenv("BASELINE_L_PER_ACRE", "100"))  # knapsack broadcast
CHEMICAL_PRICE_INR_L = float(os.getenv("CHEMICAL_PRICE_INR_L", "500"))
SPRAY_SWATH_M = float(os.getenv("SPRAY_SWATH_M", "0.3"))
LABOUR_INR_PER_ACRE = float(os.getenv("LABOUR_INR_PER_ACRE", "0"))
SUMMARY_LANG = os.getenv("SUMMARY_LANG", "hi")  # farmer-facing summary language

# --- Plant database ---
PLANT_DB_PATH = os.getenv("PLANT_DB_PATH", "plant_db.json")
PLANT_MATCH_TOLERANCE_M = float(os.getenv("PLANT_MATCH_TOLERANCE_M", "0.5"))
