/**
 * drive.h - Four-wheel tank drive over 2x L298N (circuit §5.1).
 */
#pragma once
#include <stdint.h>

void drive_init();
void drive_update();   // apply current velocity/turn targets (called from driveTask)
void drive_stop();

// Velocity targets in range [-255, 255]; sign sets direction.
void drive_set(int16_t left, int16_t right);

// Latest measured speed (mm/s) from Pi-reported wheel encoders; used for the
// seed-drop offset formula on the sower attachment.
void drive_set_measured_velocity(float mm_per_s);
float drive_get_measured_velocity();
