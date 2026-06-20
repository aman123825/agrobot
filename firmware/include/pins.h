/**
 * pins.h - AgriRover ESP32 pin map
 *
 * SINGLE SOURCE OF TRUTH for ESP32 GPIO assignments.
 * Mirrors docs/circuit-diagram.md §2. Do not edit pins here without
 * updating the circuit diagram (and vice versa).
 *
 * Board: ESP32 DevKit V1 (38-pin, WROOM-32).
 * NOTE: GPIO34/35/36/39 are INPUT-ONLY (no internal pull-ups, no output).
 */
#pragma once

// ---- Drive: L298N #1 (LEFT) + #2 (RIGHT) ----
#define PIN_MOTOR_IN1     19   // L298N #1 IN1  (left dir)
#define PIN_MOTOR_IN2     21   // L298N #1 IN2  (left dir)
#define PIN_MOTOR_IN3     22   // L298N #2 IN3  (right dir)
#define PIN_MOTOR_IN4     23   // L298N #2 IN4  (right dir)
#define PIN_MOTOR_ENA     32   // L298N ENA  (left speed, LEDC PWM)
#define PIN_MOTOR_ENB     33   // L298N ENB  (right speed, LEDC PWM)

// ---- Front ultrasonic (HC-SR04) on SG90 sweep servo ----
#define PIN_US_FRONT_TRIG 25   // 3.3V trigger is fine
#define PIN_US_FRONT_ECHO 18   // via 2.2k/3.9k divider -> 3.2V (see §6.1)
#define PIN_SERVO_US      27   // SG90 180-deg sweep mount

// ---- NPK probe over RS485 (MAX485 on UART2) ----
#define PIN_RS485_DI      17   // UART2 TX -> MAX485 DI
#define PIN_RS485_RO      16   // UART2 RX <- MAX485 RO
#define PIN_RS485_DE_RE    4   // MAX485 DE+RE tied; HIGH=transmit

// ---- Ambient + analog sensors ----
#define PIN_DHT22         14   // DHT22 data (10k pull-up to 3.3V)
#define PIN_MOISTURE      34   // capacitive soil moisture (ADC1_CH6, input-only)
#define PIN_VBAT_SENSE    35   // battery divider 39k/10k (ADC1_CH7, input-only)
#define PIN_TDS           36   // TDS meter (ADC1_CH0, input-only)

// ---- GPS (Neo-6M on UART1, receive-only) ----
#define PIN_GPS_RX        39   // UART1 RX <- GPS TX (input-only)

// ---- Dosing relays (2-channel module) ----
#define PIN_RELAY_PUMP    26   // Ch1: pump (pre-soak + micro-dose)
#define PIN_RELAY_ACTUATOR 13  // Ch2: linear actuator (extend)
// OPEN ITEM (circuit §5.2): Branch B (DC reversible actuator) needs a DPDT
// direction line. Reclaim a freed GPIO here when actuator type is confirmed.
// #define PIN_ACTUATOR_DIR  <tbd>

// ---- LEDC PWM channel assignments ----
#define LEDC_CH_LEFT       0
#define LEDC_CH_RIGHT      1
#define LEDC_CH_SERVO      2
#define LEDC_PWM_FREQ_HZ   1000
#define LEDC_PWM_RES_BITS  8    // 0..255 duty
