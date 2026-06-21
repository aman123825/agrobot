/**
 * drive.cpp - Tank drive implementation (2x BTS7960 / IBT-2, FC-10).
 *
 * Each side uses two LEDC PWM channels (RPWM + LPWM). Direction is set by
 * which line carries the PWM; the other is held at 0. This replaces the old
 * L298N IN1/IN2 + ENA scheme. Public API is unchanged so main.cpp / comms.cpp
 * compile without edits. ENA/ENB are gone (R_EN/L_EN are tied to 3.3V).
 */
#include <Arduino.h>
#include "pins.h"
#include "config.h"
#include "drive.h"

static volatile int16_t gLeft = 0, gRight = 0;
static volatile float   gMeasuredMmPerS = 0.0f;

void drive_init() {
    // Configure all four BTS7960 PWM channels and attach their pins.
    ledcSetup(LEDC_CH_LEFT_RPWM,  LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcSetup(LEDC_CH_LEFT_LPWM,  LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcSetup(LEDC_CH_RIGHT_RPWM, LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcSetup(LEDC_CH_RIGHT_LPWM, LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcAttachPin(PIN_MOTOR_LEFT_RPWM,  LEDC_CH_LEFT_RPWM);
    ledcAttachPin(PIN_MOTOR_LEFT_LPWM,  LEDC_CH_LEFT_LPWM);
    ledcAttachPin(PIN_MOTOR_RIGHT_RPWM, LEDC_CH_RIGHT_RPWM);
    ledcAttachPin(PIN_MOTOR_RIGHT_LPWM, LEDC_CH_RIGHT_LPWM);

    drive_stop();
}

// BTS7960: fwd -> PWM on RPWM, LPWM=0; rev -> PWM on LPWM, RPWM=0; stop -> 0/0.
static void applySide(uint8_t chR, uint8_t chL, int16_t v) {
    uint8_t duty = (uint8_t)constrain(abs(v), 0, 255);
    if (v >= 0) {
        ledcWrite(chR, duty);
        ledcWrite(chL, 0);
    } else {
        ledcWrite(chR, 0);
        ledcWrite(chL, duty);
    }
}

void drive_update() {
    applySide(LEDC_CH_LEFT_RPWM,  LEDC_CH_LEFT_LPWM,  gLeft);
    applySide(LEDC_CH_RIGHT_RPWM, LEDC_CH_RIGHT_LPWM, gRight);
}

void drive_set(int16_t left, int16_t right) { gLeft = left; gRight = right; }

void drive_stop() {
    gLeft = gRight = 0;
    ledcWrite(LEDC_CH_LEFT_RPWM,  0);
    ledcWrite(LEDC_CH_LEFT_LPWM,  0);
    ledcWrite(LEDC_CH_RIGHT_RPWM, 0);
    ledcWrite(LEDC_CH_RIGHT_LPWM, 0);
}

void drive_set_measured_velocity(float mm_per_s) { gMeasuredMmPerS = mm_per_s; }
float drive_get_measured_velocity() { return gMeasuredMmPerS; }
