#include <Arduino.h>
#include "control_state.h"

static portMUX_TYPE sMux = portMUX_INITIALIZER_UNLOCKED;
static int16_t sLeft = 0;
static int16_t sRight = 0;
static uint32_t sLastMotionMs = 0;
static int sSpeed = 0;
static ControlSource sOwner = {ControlSource::NONE, 0};

static bool sameSource(ControlSource a, ControlSource b) {
    return a.kind == b.kind && a.id == b.id;
}

void control_state_init(int defaultSpeed) {
    portENTER_CRITICAL(&sMux);
    sLeft = sRight = 0;
    sLastMotionMs = millis();
    sSpeed = constrain(defaultSpeed, 0, 255);
    sOwner = {ControlSource::NONE, 0};
    portEXIT_CRITICAL(&sMux);
}

bool control_set_motion(ControlSource source, int16_t left, int16_t right,
                        uint32_t nowMs) {
    bool accepted = false;
    portENTER_CRITICAL(&sMux);
    if (sOwner.kind == ControlSource::NONE || sameSource(source, sOwner)) {
        sOwner = source;
        sLeft = constrain(left, -255, 255);
        sRight = constrain(right, -255, 255);
        sLastMotionMs = nowMs;
        if (sLeft == 0 && sRight == 0) sOwner = {ControlSource::NONE, 0};
        accepted = true;
    }
    portEXIT_CRITICAL(&sMux);
    return accepted;
}

void control_get_motion(int16_t* left, int16_t* right) {
    portENTER_CRITICAL(&sMux);
    if (left) *left = sLeft;
    if (right) *right = sRight;
    portEXIT_CRITICAL(&sMux);
}

void control_force_stop() {
    portENTER_CRITICAL(&sMux);
    sLeft = sRight = 0;
    sOwner = {ControlSource::NONE, 0};
    portEXIT_CRITICAL(&sMux);
}

void control_outputs_inhibit() {
    portENTER_CRITICAL(&sMux);
    sLeft = sRight = 0;
    portEXIT_CRITICAL(&sMux);
}

bool control_stop_if_owner(ControlSource source) {
    bool stopped = false;
    portENTER_CRITICAL(&sMux);
    if (sameSource(source, sOwner)) {
        sLeft = sRight = 0;
        sOwner = {ControlSource::NONE, 0};
        stopped = true;
    }
    portEXIT_CRITICAL(&sMux);
    return stopped;
}

void control_release_if_expired(uint32_t nowMs, uint32_t deadmanMs) {
    portENTER_CRITICAL(&sMux);
    if (sOwner.kind != ControlSource::NONE &&
        (uint32_t)(nowMs - sLastMotionMs) > deadmanMs) {
        sLeft = sRight = 0;
        sOwner = {ControlSource::NONE, 0};
    }
    portEXIT_CRITICAL(&sMux);
}

uint32_t control_ms_since_motion(uint32_t nowMs) {
    uint32_t elapsed;
    portENTER_CRITICAL(&sMux);
    elapsed = nowMs - sLastMotionMs;
    portEXIT_CRITICAL(&sMux);
    return elapsed;
}

bool control_set_speed(ControlSource source, int speed) {
    bool accepted = false;
    portENTER_CRITICAL(&sMux);
    if (sOwner.kind == ControlSource::NONE || sameSource(source, sOwner)) {
        sSpeed = constrain(speed, 0, 255);
        accepted = true;
    }
    portEXIT_CRITICAL(&sMux);
    return accepted;
}

int control_get_speed() {
    int speed;
    portENTER_CRITICAL(&sMux);
    speed = sSpeed;
    portEXIT_CRITICAL(&sMux);
    return speed;
}

bool control_source_owns_drive(ControlSource source) {
    bool owns;
    portENTER_CRITICAL(&sMux);
    owns = sameSource(source, sOwner);
    portEXIT_CRITICAL(&sMux);
    return owns;
}

bool control_has_owner() {
    bool owned;
    portENTER_CRITICAL(&sMux);
    owned = sOwner.kind != ControlSource::NONE;
    portEXIT_CRITICAL(&sMux);
    return owned;
}
