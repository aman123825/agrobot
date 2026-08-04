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

// ---- 3x HC-SR04 ultrasonic (left / center / right, fixed mount) ----
// Each ECHO pin needs a voltage divider (5V -> ~3.2V, safe for ESP32).
// As wired: 2.2k/3.9k -> Vout = 5 * 3.9/(2.2+3.9) = 3.2V. NEVER connect a raw
// 5V ECHO to an ESP32 pin. ECHO uses the input-only pins 34/35/36 (read-only
// is all ECHO needs); TRIG uses output-capable pins (no strapping pins used).
#define PIN_US_LEFT_TRIG    27
#define PIN_US_LEFT_ECHO    34   // via 2.2k/3.9k divider (ADC1_CH6, input-only)
#define PIN_US_CENTER_TRIG  33
#define PIN_US_CENTER_ECHO  35   // via 2.2k/3.9k divider (ADC1_CH7, input-only)
#define PIN_US_RIGHT_TRIG   25
#define PIN_US_RIGHT_ECHO   36   // via 2.2k/3.9k divider (ADC1_CH0, input-only)

// ---- NPK probe over RS485 (MAX485 on UART2) ----
#define PIN_RS485_DI      17   // UART2 TX -> MAX485 DI
#define PIN_RS485_RO      16   // UART2 RX <- MAX485 RO
#define PIN_RS485_DE_RE    4   // MAX485 DE+RE tied; HIGH=transmit

// ---- Ambient + analog sensors ----
#define PIN_DHT22         14   // DHT22 data (10k pull-up to 3.3V)
#define PIN_MOISTURE      32   // capacitive soil moisture (ADC1_CH4); power sensor from 3.3V
#define PIN_VBAT_SENSE    39   // battery divider 39k/10k (ADC1_CH3, input-only)

// ---- Dosing pump relay (single channel, active-LOW) ----
// External 10k pull-up to 3.3V required (boot-window safety).
#define PIN_RELAY_PUMP     26  // pump (pre-soak + micro-dose)

// ---- Probe-insertion servo (MG995 positional) ----
// This was the linear-actuator relay (GPIO13); it is now the servo signal that
// lowers and raises the combined NPK + moisture probe. Add a 10k pull-DOWN to
// GND so the line idles low (no pulses) until the firmware drives it. Power the
// servo from the 5V (LM2596) rail, NOT 3.3V, and share ground with the ESP32 --
// an MG995 can pull ~1A (much more if it stalls), so give it its own supply tap.
#define PIN_SERVO_INSERT   13

// ---- LEDC PWM channels ----
// Drive motors use channels 0-3 (timers 0+1). The servo uses channel 4
// (timer 2) at 50 Hz so its timing never disturbs the drive PWM.
#define LEDC_CH_LEFT_RPWM    0
#define LEDC_CH_LEFT_LPWM    1
#define LEDC_CH_RIGHT_RPWM   2
#define LEDC_CH_RIGHT_LPWM   3
#define LEDC_PWM_FREQ_HZ     100
#define LEDC_PWM_RES_BITS    8   // 0..255 duty

#define LEDC_CH_SERVO        4   // insertion servo (timer 2)
#define LEDC_SERVO_FREQ_HZ   50  // standard hobby-servo frame rate
#define LEDC_SERVO_RES_BITS  16  // fine pulse-width resolution at 50 Hz
