/**
 * servo.h - SG90 servo driver for the ultrasonic sweep mount (GPIO27).
 *
 * Uses LEDC channel LEDC_CH_SERVO at 50 Hz. This channel maps to a different
 * LEDC timer (channel 4 -> timer 2) than the four BTS7960 motor PWM channels
 * (0-3 -> timers 0/1), so there is no interference with the 1 kHz drive PWM.
 */
#pragma once
#include <stdint.h>

void servo_us_init();              // configure LEDC + center the servo
void servo_us_write_deg(uint8_t deg);  // 0..180 degrees
