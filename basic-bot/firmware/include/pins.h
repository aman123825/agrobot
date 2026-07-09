/**
 * pins.h - AgriRover BASIC BOT pin map (subset of the full rover).
 *
 * Same verified GPIO assignments as the full firmware (docs/circuit-diagram.md
 * §2) so nothing has to be rewired when you upgrade later. Only the pins the
 * basic (no-AI) build actually uses are listed here.
 *
 * Board: ESP32 DevKit V1 (38-pin, WROOM-32).
 * NOTE: GPIO34/35/36/39 are INPUT-ONLY (no internal pull-ups, no output).
 */
#pragma once

// ---- Drive: 2x BTS7960 (IBT-2), one per side ----
// Each driver takes two PWM inputs (RPWM, LPWM):
//   forward = PWM on RPWM, LPWM low; reverse = PWM on LPWM, RPWM low.
// R_EN and L_EN of BOTH drivers are tied HIGH to 3.3V (always enabled).
#define PIN_MOTOR_LEFT_RPWM   19   // BTS7960 #1 RPWM (left forward)
#define PIN_MOTOR_LEFT_LPWM   21   // BTS7960 #1 LPWM (left reverse)
#define PIN_MOTOR_RIGHT_RPWM  22   // BTS7960 #2 RPWM (right forward)
#define PIN_MOTOR_RIGHT_LPWM  23   // BTS7960 #2 LPWM (right reverse)

// ---- Front ultrasonic (HC-SR04, fixed mount - no sweep servo in basic bot) ----
#define PIN_US_FRONT_TRIG 25   // 3.3V trigger is fine
#define PIN_US_FRONT_ECHO 18   // via 2.2k/3.9k divider -> ~3.2V (NEVER raw 5V)

// ---- NPK probe over RS485 (MAX485 on UART2) ----
#define PIN_RS485_DI      17   // UART2 TX -> MAX485 DI
#define PIN_RS485_RO      16   // UART2 RX <- MAX485 RO
#define PIN_RS485_DE_RE    4   // MAX485 DE+RE tied; HIGH=transmit

// ---- Ambient + analog sensors ----
#define PIN_DHT22         14   // DHT22 data (10k pull-up to 3.3V)
#define PIN_MOISTURE      34   // capacitive soil moisture (ADC1_CH6, input-only)
#define PIN_VBAT_SENSE    35   // battery divider 39k/10k (ADC1_CH7, input-only)

// ---- Dosing relays (2-channel module, active-LOW) ----
// External 10k pull-ups to 3.3V required on both pins (boot-window safety).
#define PIN_RELAY_PUMP     26  // Ch1: pump (pre-soak + micro-dose)
#define PIN_RELAY_ACTUATOR 13  // Ch2: linear actuator (extend; spring retracts)

// ---- LEDC PWM channels (drive only; timers 0+1 @ 1 kHz) ----
#define LEDC_CH_LEFT_RPWM    0
#define LEDC_CH_LEFT_LPWM    1
#define LEDC_CH_RIGHT_RPWM   2
#define LEDC_CH_RIGHT_LPWM   3
#define LEDC_PWM_FREQ_HZ  1000
#define LEDC_PWM_RES_BITS    8   // 0..255 duty
