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
USE_CORAL = os.getenv("USE_CORAL", "1") == "1"

# --- Telegram alerts ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- Plant database ---
PLANT_DB_PATH = os.getenv("PLANT_DB_PATH", "plant_db.json")
PLANT_MATCH_TOLERANCE_M = float(os.getenv("PLANT_MATCH_TOLERANCE_M", "0.5"))
