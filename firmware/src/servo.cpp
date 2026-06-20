/**
 * servo.cpp - SG90 servo driver (50 Hz LEDC PWM).
 *
 * SG90 expects a 20 ms frame (50 Hz). Pulse width 0.5 ms -> 0 deg,
 * 2.5 ms -> 180 deg. At 16-bit resolution the full 65535 count spans the
 * 20 ms period, so:
 *   duty(0.5 ms) = 0.5/20  * 65535 = 1638
 *   duty(2.5 ms) = 2.5/20  * 65535 = 8192
 */
#include <Arduino.h>
#include "pins.h"
#include "servo.h"

static const int      SERVO_FREQ_HZ = 50;
static const int      SERVO_RES_BITS = 16;
static const uint32_t SERVO_DUTY_MIN = 1638;   // 0 deg  (0.5 ms)
static const uint32_t SERVO_DUTY_MAX = 8192;   // 180 deg (2.5 ms)

void servo_us_init() {
    ledcSetup(LEDC_CH_SERVO, SERVO_FREQ_HZ, SERVO_RES_BITS);
    ledcAttachPin(PIN_SERVO_US, LEDC_CH_SERVO);
    servo_us_write_deg(90);   // center on startup
}

void servo_us_write_deg(uint8_t deg) {
    if (deg > 180) deg = 180;
    uint32_t duty = SERVO_DUTY_MIN +
                    (uint32_t)deg * (SERVO_DUTY_MAX - SERVO_DUTY_MIN) / 180;
    ledcWrite(LEDC_CH_SERVO, duty);
}
