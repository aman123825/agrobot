/**
 * dosing.h - Sequential pump + actuator dosing controller.
 *
 * Implements the never-simultaneous relay sequence from circuit §5.2:
 *   Ch1 pump pre-soak -> Ch2 actuator extend -> dwell -> micro-dose -> retract
 */
#pragma once
#include "events.h"   // EventGroupHandle_t + EVT_DOSING

// Pass the shared event group so the sequence can assert EVT_DOSING and force
// the drive task to keep the motors stopped while the probe is in the soil.
void dosing_init(EventGroupHandle_t events);

// Runs one full insertion+dose cycle. Blocking on the sensor-task timeline
// (Core 0). Returns true on success, false if aborted (e.g. tank empty).
bool dosing_run_sequence();
