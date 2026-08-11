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
#define CMD_CTR_PERSIST_INTERVAL_MS 30000  // throttle NVS counter writes (wear)

// ---- Rover identity (fleet support) ----
// Override at build time: -DROVER_ID=\"rover02\"
#ifndef ROVER_ID
#define ROVER_ID "rover01"
#endif

// ---- MQTT topics (match docs/circuit-diagram.md §4.4 + BOM #101) ----
// Topics now include rover ID for fleet support (C string concatenation).
#define TOPIC_NPK     "rover/" ROVER_ID "/npk"
#define TOPIC_GPS     "rover/" ROVER_ID "/gps"
#define TOPIC_STATUS  "rover/" ROVER_ID "/status"
#define TOPIC_ALERT   "rover/" ROVER_ID "/alert"

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

// ---- ADC calibration & oversampling (accuracy) ----
#define ADC_OVERSAMPLE      16     // averaged raw reads per sample
#define ADC_VREF_MV         1100   // fallback Vref (mV) if eFuse not burned

// ---- NPK robustness ----
#define NPK_MAX_RETRIES     3      // retry a failed Modbus read this many times

// ---- Ultrasonic accuracy ----
#define US_MEDIAN_SAMPLES   5      // median-of-N pings rejects spurious echoes

// ---- GPS (Neo-6M) accuracy: SBAS/GAGAN + stationary averaging ----
#define GPS_BAUD            9600
#define GPS_SBAS_ENABLE     1      // enable SBAS augmentation (India: GAGAN)
#define GPS_AVG_SAMPLES     30     // fixes averaged at a stationary waypoint
#define GPS_AVG_GAP_MS      100    // spacing between averaged fixes

// ---- Link heartbeat / dead-man (safety) ----
#define LINK_HEARTBEAT_TIMEOUT_MS 1500  // halt if no valid command within this

// ---- Watchdog ----
#define WDT_TIMEOUT_S       5      // task watchdog timeout

// ---- OTA firmware update ----
#ifndef OTA_HOSTNAME
#define OTA_HOSTNAME        "agrorover"
#endif
#ifndef OTA_PASSWORD
#define OTA_PASSWORD        "CHANGE_ME_OTA_PASSWORD"  // set in secrets.h
#endif

// ---- Battery (4S LiFePO4) thresholds ----
// LiFePO4 chosen over LiPo for hot-climate thermal tolerance (FC-02).
#define BATT_FULL_V       14.6f   // 3.65 V/cell
#define BATT_NOMINAL_V    12.8f   // 3.20 V/cell
#define BATT_CUTOFF_V     11.0f   // 2.75 V/cell; triggers EVT_LOW_BATTERY -> return-to-base
#define VBAT_DIVIDER_RATIO (10.0f / (39.0f + 10.0f))  // 39k/10k (14.6 V -> 2.98 V at ADC)

// ---- Thermal guardian (FC-02): ESP32 die-temperature limits ----
// temperatureRead() returns the internal SoC temperature (degC). Above the
// limit we assert EVT_OVERTEMP (in EVT_DRIVE_INHIBIT) and publish one alert;
// the bit clears below the lower threshold (hysteresis) to avoid chatter.
#define ESP32_OVERTEMP_C        85.0f  // assert EVT_OVERTEMP at/above this
#define ESP32_OVERTEMP_CLEAR_C  80.0f  // clear EVT_OVERTEMP below this

// ---- Dosing sequence timing (circuit §5.2) ----
#define DOSE_PRESOAK_MS   1500    // Ch1 pump pre-soak before actuator extends
#define DOSE_DWELL_MS      800    // hold at full insertion before dosing
#define DOSE_INJECT_MS    1500    // micro-dose pulse (1ml @ 40ml/min peristaltic)
#define ACTUATOR_TRAVEL_MS 4000   // worst-case extend/retract (limit-switch backed)

// ---- Actuator retraction type (FC-03) ----
// 0 = Branch A (spring-return): de-energizing Ch2 retracts. Default; needs no
//     extra GPIO. 1 = Branch B (DC reversible): a DPDT relay on PIN_ACTUATOR_DIR
//     flips polarity to power the retract phase. Leave at 0 unless a reversible
//     actuator + DPDT relay are physically wired (see pins.h / circuit §5.2).
#ifndef ACTUATOR_DC_REVERSIBLE
#define ACTUATOR_DC_REVERSIBLE 0
#endif

// ---- FreeRTOS task config ----
#define TASK_DRIVE_CORE    1
#define TASK_SENSOR_CORE   0
#define TASK_STACK_WORDS   4096
