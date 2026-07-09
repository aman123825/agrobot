/**
 * drive.h - Tank drive API (2x BTS7960 / IBT-2).
 */
#pragma once
#include <stdint.h>

void drive_init();
void drive_set(int16_t left, int16_t right);   // -255..255 per side
void drive_get(int16_t* left, int16_t* right); // current setpoints
void drive_update();                            // push setpoints to PWM
void drive_stop();                              // zero setpoints AND outputs
