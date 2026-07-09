/**
 * drive.cpp - Tank drive implementation (2x BTS7960 / IBT-2).
 *
 * Each side uses two LEDC PWM channels (RPWM + LPWM). Direction is set by
 * which line carries the PWM; the other is held at 0.
 *   forward = PWM on RPWM, LPWM 0; reverse = PWM on LPWM, RPWM 0; stop = 0/0.
 * R_EN/L_EN on both drivers are tied to 3.3V in hardware (always enabled).
 */
#include <Arduino.h>
#include "pins.h"
#include "config.h"
#include "drive.h"

static volatile int16_t gLeft = 0, gRight = 0;

void drive_init() {
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

void drive_get(int16_t* left, int16_t* right) {
    if (left)  *left  = gLeft;
    if (right) *right = gRight;
}

void drive_stop() {
    gLeft = gRight = 0;
    ledcWrite(LEDC_CH_LEFT_RPWM,  0);
    ledcWrite(LEDC_CH_LEFT_LPWM,  0);
    ledcWrite(LEDC_CH_RIGHT_RPWM, 0);
    ledcWrite(LEDC_CH_RIGHT_LPWM, 0);
}
