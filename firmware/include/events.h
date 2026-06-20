/**
 * events.h - Cross-core FreeRTOS event bits (single definition).
 *
 * Centralized here so main.cpp, comms.cpp, and dosing.cpp can never drift
 * out of sync on the bit positions (a real hazard if duplicated by hand).
 */
#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

#define EVT_HALT          (1 << 0)  // e-stop / tilt / obstacle -> stop motors
#define EVT_LOW_BATTERY   (1 << 1)  // LiPo below cutoff -> return-to-base
#define EVT_DOSE_REQUEST  (1 << 2)  // waypoint reached -> run dosing sequence
#define EVT_PAUSE_IRRIG   (1 << 3)  // rain detected (relayed from Pi)
#define EVT_DOSING        (1 << 4)  // dosing in progress -> drive MUST stay stopped
#define EVT_OBSTACLE      (1 << 5)  // local ultrasonic obstacle within stop distance
#define EVT_PUMP_DISABLE  (1 << 6)  // tank empty / Pi override -> block dosing
#define EVT_LINK_LOST     (1 << 7)  // no valid command within heartbeat timeout

// Bits that must force the drive to a stop.
#define EVT_DRIVE_INHIBIT (EVT_HALT | EVT_LOW_BATTERY | EVT_DOSING | EVT_OBSTACLE | EVT_LINK_LOST)

// Shared event group (defined in main.cpp).
extern EventGroupHandle_t gEvents;
