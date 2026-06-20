/**
 * config.h - AgriRover ESP32 runtime configuration
 *
 * Network, MQTT topics, Modbus, and dosing-sequence timing constants.
 * Secrets (WiFi/MQTT credentials) should be provided via build flags or a
 * local secrets.h that is gitignored - never commit real credentials.
 */
#pragma once

// ---- WiFi / MQTT (override in secrets.h or platformio build flags) ----
#ifndef WIFI_SSID
#define WIFI_SSID        "CHANGE_ME"
#endif
#ifndef WIFI_PASSWORD
#define WIFI_PASSWORD    "CHANGE_ME"
#endif
#ifndef MQTT_BROKER_HOST
#define MQTT_BROKER_HOST "192.168.1.10"   // Pi running Mosquitto
#endif
#define MQTT_BROKER_PORT 1883
#define MQTT_CLIENT_ID   "agrorover-esp32"

// ---- MQTT topics (match docs/circuit-diagram.md §4.4 + BOM #101) ----
#define TOPIC_NPK     "rover/npk"
#define TOPIC_GPS     "rover/gps"
#define TOPIC_STATUS  "rover/status"
#define TOPIC_ALERT   "rover/alert"

// ---- NPK probe (Modbus RTU over RS485) ----
#define NPK_BAUD          9600
#define NPK_SLAVE_ADDR    0x01
#define NPK_FRAME_TIMEOUT_MS 1000

// ---- Battery (3S LiPo) thresholds ----
#define LIPO_FULL_V       12.6f
#define LIPO_NOMINAL_V    11.1f
#define LIPO_CUTOFF_V      9.9f   // triggers EVT_LOW_BATTERY -> return-to-base
#define VBAT_DIVIDER_RATIO (10.0f / (39.0f + 10.0f))  // 39k/10k

// ---- Dosing sequence timing (circuit §5.2) ----
#define DOSE_PRESOAK_MS   1500    // Ch1 pump pre-soak before actuator extends
#define DOSE_DWELL_MS      800    // hold at full insertion before dosing
#define DOSE_INJECT_MS    1500    // micro-dose pulse (1ml @ 40ml/min peristaltic)
#define ACTUATOR_TRAVEL_MS 4000   // worst-case extend/retract (limit-switch backed)

// ---- FreeRTOS task config ----
#define TASK_DRIVE_CORE    1
#define TASK_SENSOR_CORE   0
#define TASK_STACK_WORDS   4096
