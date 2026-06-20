/**
 * config.h - AgriRover ESP32 runtime configuration
 *
 * Network, MQTT topics, Modbus, and dosing-sequence timing constants.
 * Secrets (WiFi/MQTT credentials) should be provided via build flags or a
 * local secrets.h that is gitignored - never commit real credentials.
 */
#pragma once

// Local secrets (gitignored). Copy include/secrets.example.h -> include/secrets.h
// and fill in real values, or pass -D flags from platformio.ini build_flags.
#if defined(__has_include)
#  if __has_include("secrets.h")
#    include "secrets.h"
#  endif
#endif

// ---- WiFi ----
#ifndef WIFI_SSID
#define WIFI_SSID        "CHANGE_ME"
#endif
#ifndef WIFI_PASSWORD
#define WIFI_PASSWORD    "CHANGE_ME"
#endif

// ---- MQTT ----
#ifndef MQTT_BROKER_HOST
#define MQTT_BROKER_HOST "192.168.1.10"   // Pi running Mosquitto
#endif
#ifndef MQTT_USER
#define MQTT_USER        "agrorover"
#endif
#ifndef MQTT_PASS
#define MQTT_PASS        ""               // set in secrets.h - never commit
#endif
// Define MQTT_USE_TLS (and provide MQTT_CA_CERT in secrets.h) for encrypted MQTT.
#ifdef MQTT_USE_TLS
#  define MQTT_BROKER_PORT 8883
#else
#  define MQTT_BROKER_PORT 1883
#endif
#define MQTT_CLIENT_ID   "agrorover-esp32"

// ---- Authenticated command link (HMAC-SHA256 + anti-replay) ----
// Shared 32+ byte random secret, identical to the Pi's AGRO_LINK_KEY.
// Set it in secrets.h. The default below is a placeholder and MUST be changed.
#ifndef COMMAND_HMAC_KEY
#define COMMAND_HMAC_KEY "CHANGE_ME_32_BYTE_RANDOM_SECRET!"
#endif
#define CMD_AUTH_TRUNC_BYTES     16     // HMAC truncated to 128 bits (32 hex chars)
#define CMD_FAIL_LOCK_THRESHOLD  8      // bad signatures before lockout
#define CMD_LOCK_COOLDOWN_MS     10000  // lockout duration after threshold

// ---- MQTT topics (match docs/circuit-diagram.md §4.4 + BOM #101) ----
#define TOPIC_NPK     "rover/npk"
#define TOPIC_GPS     "rover/gps"
#define TOPIC_STATUS  "rover/status"
#define TOPIC_ALERT   "rover/alert"

// ---- NPK probe (Modbus RTU over RS485) ----
#define NPK_BAUD          9600
#define NPK_SLAVE_ADDR    0x01
#define NPK_FRAME_TIMEOUT_MS 1000
#define NPK_REG_START     0x0000   // first holding register
#define NPK_REG_COUNT     7        // moisture,temp,EC,pH,N,P,K (vendor-dependent)

// ---- Front ultrasonic obstacle safety ----
#define US_STOP_DISTANCE_CM 25.0f  // local hard-stop threshold
#define US_TIMEOUT_US       30000UL

// ---- Manual drive speed (0..255 duty) ----
#define MANUAL_DRIVE_SPEED  180

// ---- Capacitive soil-moisture calibration (raw 12-bit ADC) ----
#define MOIST_RAW_DRY       3000   // sensor in air (calibrate)
#define MOIST_RAW_WET       1200   // sensor in water (calibrate)

// ---- Telemetry / loop cadence ----
#define GPS_FIX_MAX_AGE_MS  5000   // treat fix as stale beyond this

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
