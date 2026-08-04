#include <Arduino.h>
#include "pins.h"
#include "config.h"
#include "control_state.h"
#include "drive.h"

void drive_init() {
    ledcSetup(LEDC_CH_LEFT_RPWM, LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcSetup(LEDC_CH_LEFT_LPWM, LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcSetup(LEDC_CH_RIGHT_RPWM, LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcSetup(LEDC_CH_RIGHT_LPWM, LEDC_PWM_FREQ_HZ, LEDC_PWM_RES_BITS);
    ledcAttachPin(PIN_MOTOR_LEFT_RPWM, LEDC_CH_LEFT_RPWM);
    ledcAttachPin(PIN_MOTOR_LEFT_LPWM, LEDC_CH_LEFT_LPWM);
    ledcAttachPin(PIN_MOTOR_RIGHT_RPWM, LEDC_CH_RIGHT_RPWM);
    ledcAttachPin(PIN_MOTOR_RIGHT_LPWM, LEDC_CH_RIGHT_LPWM);
    drive_stop();
}

static void applySide(uint8_t chR, uint8_t chL, int16_t value) {
    uint8_t duty = (uint8_t)constrain(abs(value), 0, 255);
    if (value >= 0) {
        ledcWrite(chR, duty);
        ledcWrite(chL, 0);
    } else {
        ledcWrite(chR, 0);
        ledcWrite(chL, duty);
    }
}

void drive_update() {
    int16_t left, right;
    control_get_motion(&left, &right);
#if DRIVE_INVERT_LEFT
    left = -left;      // left motor wired reversed -> correct direction in software
#endif
#if DRIVE_INVERT_RIGHT
    right = -right;
#endif
    applySide(LEDC_CH_LEFT_RPWM, LEDC_CH_LEFT_LPWM, left);
    applySide(LEDC_CH_RIGHT_RPWM, LEDC_CH_RIGHT_LPWM, right);
}

void drive_set(int16_t left, int16_t right) {
    // Legacy internal API: serial control is the implicit source.
    control_set_motion({ControlSource::USB_SERIAL, 0}, left, right, millis());
}

void drive_get(int16_t* left, int16_t* right) {
    control_get_motion(left, right);
}

void drive_stop() {
    control_outputs_inhibit();
    ledcWrite(LEDC_CH_LEFT_RPWM, 0);
    ledcWrite(LEDC_CH_LEFT_LPWM, 0);
    ledcWrite(LEDC_CH_RIGHT_RPWM, 0);
    ledcWrite(LEDC_CH_RIGHT_LPWM, 0);
}
