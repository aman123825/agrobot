/**
 * drive.cpp - Tank drive implementation.
 *
 * ENA/ENB are driven by LEDC PWM (NOT jumpered high) so the rover has a
 * measurable velocity to offset seed-drop timing against (circuit §5.1).
 */
#include <Arduino.h>
#include "pins.h"
#include "config.h"
#include "drive.h"

static volatile int16_t gLeft = 0, gRight = 0;
static volatile float   gMeasuredMmPerS = 0.0f;

void drive_init() {
    pinMode(PIN_MOTOR_IN1, OUTPUT);
    pinMode(PIN_MOTOR_IN2, OUTPUT);
    pinMode(PIN_MOTOR_IN3, OUTPUT);
    pinMode(PIN_MOTOR_IN4, OUTPUT);

    ledcSetup(LEDC_CH_LEFT,  LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcSetup(LEDC_CH_RIGHT, LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcAttachPin(PIN_MOTOR_ENA, LEDC_CH_LEFT);
    ledcAttachPin(PIN_MOTOR_ENB, LEDC_CH_RIGHT);

    drive_stop();
}

static void applySide(uint8_t inA, uint8_t inB, uint8_t ch, int16_t v) {
    bool fwd = v >= 0;
    digitalWrite(inA, fwd ? HIGH : LOW);
    digitalWrite(inB, fwd ? LOW  : HIGH);
    ledcWrite(ch, (uint8_t)constrain(abs(v), 0, 255));
}

void drive_update() {
    applySide(PIN_MOTOR_IN1, PIN_MOTOR_IN2, LEDC_CH_LEFT,  gLeft);
    applySide(PIN_MOTOR_IN3, PIN_MOTOR_IN4, LEDC_CH_RIGHT, gRight);
}

void drive_set(int16_t left, int16_t right) { gLeft = left; gRight = right; }

void drive_stop() {
    gLeft = gRight = 0;
    ledcWrite(LEDC_CH_LEFT, 0);
    ledcWrite(LEDC_CH_RIGHT, 0);
    digitalWrite(PIN_MOTOR_IN1, LOW); digitalWrite(PIN_MOTOR_IN2, LOW);
    digitalWrite(PIN_MOTOR_IN3, LOW); digitalWrite(PIN_MOTOR_IN4, LOW);
}

void drive_set_measured_velocity(float mm_per_s) { gMeasuredMmPerS = mm_per_s; }
float drive_get_measured_velocity() { return gMeasuredMmPerS; }
