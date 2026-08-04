/**
 * events.h - Cross-core FreeRTOS event bits for the basic bot.
 */
#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

#define EVT_HALT          (1 << 0)  // latched by STOP command; cleared by RESUME
#define EVT_OBSTACLE      (1 << 1)  // front distance < threshold (blocks FWD only)
#define EVT_LOW_BATTERY   (1 << 2)  // battery below cutoff (hysteresis)
#define EVT_DOSING        (1 << 3)  // dosing sequence running (drive frozen)
#define EVT_DOSE_REQUEST  (1 << 4)  // DOSE command pending
#define EVT_PUMP_DISABLE  (1 << 5)  // PUMP_DISABLE command (blocks dosing)
#define EVT_OVERTEMP      (1 << 6)  // ESP32 die temperature too high
#define EVT_PROBE_DOWN_REQ (1 << 7) // manual: lower the NPK probe (servo)
#define EVT_PROBE_UP_REQ   (1 << 8) // manual: raise the NPK probe (servo)

// Any of these forces the motors to a stop. EVT_OBSTACLE is deliberately NOT
// here: it only blocks forward motion so you can still back away / turn.
#define EVT_DRIVE_INHIBIT (EVT_HALT | EVT_LOW_BATTERY | EVT_DOSING | EVT_OVERTEMP)

extern EventGroupHandle_t gEvents;
