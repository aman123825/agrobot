/**
 * config.h - AgriRover BASIC BOT runtime configuration.
 *
 * No WiFi, no MQTT, no secrets: the basic bot talks plain text over USB
 * serial to a laptop. Everything here is a tuning constant.
 */
#pragma once

// ---- Serial link to the laptop ----
#define LINK_BAUD           115200
// Dead-man: drive setpoints expire if no new drive command arrives within
// this window while the motors are running. The laptop teleop relies on OS
// key auto-repeat, so this must be longer than the keyboard repeat delay.
#define CMD_DEADMAN_MS      1000

// ---- Manual drive speed (0..255 duty, changeable at runtime via SPEED n) ----
#define MANUAL_DRIVE_SPEED  180

// ---- Front ultrasonic obstacle safety ----
#define US_STOP_DISTANCE_CM 25.0f  // block forward drive below this
#define US_TIMEOUT_US       30000UL
#define US_MEDIAN_SAMPLES   3      // median-of-N rejects spurious echoes

// ---- NPK probe (Modbus RTU over RS485) ----
#define NPK_BAUD            9600
#define NPK_SLAVE_ADDR      0x01
#define NPK_FRAME_TIMEOUT_MS 300   // 19-byte reply @9600 takes ~20 ms
#define NPK_REG_START       0x0000 // first holding register
#define NPK_REG_COUNT       7      // moisture,temp,EC,pH,N,P,K (vendor-dependent!)
#define NPK_MAX_RETRIES     2
// If the probe is absent/unwired, don't burn the sensor loop retrying every
// second - back off and try again later.
#define NPK_FAIL_BACKOFF_MS 10000

// ---- ADC calibration & oversampling ----
#define ADC_OVERSAMPLE      16     // averaged raw reads per sample
#define ADC_VREF_MV         1100   // fallback Vref (mV) if eFuse not burned

// ---- Battery (3S LiPo) ----
#define LIPO_FULL_V         12.6f
#define LIPO_CUTOFF_V        9.9f  // below this: drive inhibited + ALERT
#define VBAT_DIVIDER_RATIO  (10.0f / (39.0f + 10.0f))   // 39k/10k divider

// ---- Thermal guardian: ESP32 die temperature (no extra hardware) ----
#define ESP32_OVERTEMP_C        85.0f  // inhibit drive at/above this
#define ESP32_OVERTEMP_CLEAR_C  80.0f  // clear below this (hysteresis)

// ---- Dosing sequence timing (Branch A: spring-return actuator) ----
#define DOSE_PRESOAK_MS     1500   // pump pre-soak before actuator extends
#define DOSE_DWELL_MS        800   // hold at full insertion before dosing
#define DOSE_INJECT_MS      1500   // micro-dose pulse
#define ACTUATOR_TRAVEL_MS  4000   // worst-case extend/retract time

// ---- Relay module polarity (common opto modules are active-LOW) ----
#define RELAY_ACTIVE_LOW    1

// ---- Loop cadence ----
#define DRIVE_LOOP_MS       20     // 50 Hz drive/command loop
#define FAST_SENSE_MS       200    // 5 Hz ultrasonic obstacle check
#define SLOW_SENSE_EVERY    5      // slow sensors + telemetry every Nth fast loop (1 Hz)

// ---- Watchdog ----
#define WDT_TIMEOUT_S       5

// ---- FreeRTOS task placement ----
#define TASK_DRIVE_CORE     1
#define TASK_SENSOR_CORE    0
#define TASK_STACK_WORDS    4096
