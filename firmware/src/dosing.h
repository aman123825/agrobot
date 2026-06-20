/**
 * dosing.h - Sequential pump + actuator dosing controller.
 *
 * Implements the never-simultaneous relay sequence from circuit §5.2:
 *   Ch1 pump pre-soak -> Ch2 actuator extend -> dwell -> micro-dose -> retract
 */
#pragma once

void dosing_init();

// Runs one full insertion+dose cycle. Blocking on the sensor-task timeline
// (Core 0). Returns true on success, false if aborted (e.g. tank empty).
bool dosing_run_sequence();
