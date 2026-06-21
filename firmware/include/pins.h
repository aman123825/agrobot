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

// ---- Drive: 2x BTS7960 (IBT-2), one per side (FC-10) ----
// BTS7960 is a dual half-bridge: each side takes two PWM inputs (RPWM, LPWM).
//   forward  = PWM on RPWM, LPWM held LOW
//   reverse  = PWM on LPWM, RPWM held LOW
//   stop     = both LOW (coast)
// R_EN and L_EN of BOTH drivers are tied HIGH to 3.3V (always enabled); the
// firmware controls direction/speed purely through the 4 PWM lines. This frees
// GPIO32/33 (previously L298N ENA/ENB) for future use.
#define PIN_MOTOR_LEFT_RPWM   19   // BTS7960 #1 RPWM (left forward)
#define PIN_MOTOR_LEFT_LPWM   21   // BTS7960 #1 LPWM (left reverse)
#define PIN_MOTOR_RIGHT_RPWM  22   // BTS7960 #2 RPWM (right forward)
#define PIN_MOTOR_RIGHT_LPWM  23   // BTS7960 #2 LPWM (right reverse)
// GPIO32/33 freed (were L298N ENA/ENB). BTS7960 R_EN/L_EN -> 3.3V (tie high).
// Optionally repurpose 32/33 to drive R_EN/L_EN for a hardware coast-disable.

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

// ---- GPS (Neo-6M on UART1) ----
#define PIN_GPS_RX        39   // UART1 RX <- GPS TX (input-only)
// DGPS/RTCM correction output to the GPS RX pin (optional, experimental).
// GPIO15 is a strapping pin whose required boot level (HIGH) matches an idle
// UART TX line, so it is safe to use here. Leave the GPS RX pin unconnected if
// you are not feeding RTCM corrections.
#define PIN_GPS_TX        15   // UART1 TX -> GPS RX (RTCM/DGPS injection)

// ---- Dosing relays (2-channel module) ----
#define PIN_RELAY_PUMP    26   // Ch1: pump (pre-soak + micro-dose)
#define PIN_RELAY_ACTUATOR 13  // Ch2: linear actuator (extend)
// Branch B (DC reversible actuator, FC-03): direction line for a DPDT relay
// that flips actuator polarity to power the retract phase. Only used when
// config.h sets ACTUATOR_DC_REVERSIBLE=1. GPIO2 is a strapping pin left free
// for this; if it is needed elsewhere, route this through the PCF8574 instead.
#define PIN_ACTUATOR_DIR   2   // Branch B only (DPDT polarity); idle otherwise

// ---- LEDC PWM channel assignments ----
// Four channels drive the two BTS7960 sides (timers 0 + 1 at 1 kHz). The servo
// uses a separate timer (channel 4 -> timer 2) at 50 Hz so the 1 kHz drive PWM
// never interferes with the 20 ms servo frame.
#define LEDC_CH_LEFT_RPWM    0
#define LEDC_CH_LEFT_LPWM    1
#define LEDC_CH_RIGHT_RPWM   2
#define LEDC_CH_RIGHT_LPWM   3
#define LEDC_CH_SERVO        4
#define LEDC_PWM_FREQ_HZ   1000
#define LEDC_PWM_RES_BITS  8    // 0..255 duty
