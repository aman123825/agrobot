#pragma once

#include <stdint.h>

struct ControlSource {
    enum Kind : uint8_t { NONE = 0, USB_SERIAL = 1, WEBSOCKET = 2 } kind;
    uint32_t id;
};

void control_state_init(int defaultSpeed);

bool control_set_motion(ControlSource source, int16_t left, int16_t right,
                        uint32_t nowMs);
void control_get_motion(int16_t* left, int16_t* right);
void control_force_stop();
void control_outputs_inhibit();
bool control_stop_if_owner(ControlSource source);
void control_release_if_expired(uint32_t nowMs, uint32_t deadmanMs);
uint32_t control_ms_since_motion(uint32_t nowMs);

bool control_set_speed(ControlSource source, int speed);
int control_get_speed();

bool control_source_owns_drive(ControlSource source);
bool control_has_owner();
