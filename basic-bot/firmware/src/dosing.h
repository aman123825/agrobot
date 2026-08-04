/**
 * dosing.h - Sequential dosing state machine API.
 */
#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

void dosing_init(EventGroupHandle_t events);
bool dosing_run_sequence();   // blocking; asserts EVT_DOSING for the duration


// Manual probe control (servo up/down) outside the full dose cycle.
// dosing_probe_down() freezes the drive (EVT_DOSING) while the probe is lowered;
// dosing_probe_up() raises it and releases the freeze. Call from the sensor task.
void dosing_probe_down();
void dosing_probe_up();