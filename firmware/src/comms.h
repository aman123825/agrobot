/**
 * comms.h - Connectivity: WiFi + MQTT publish, and the UART command link to
 * the Raspberry Pi (circuit §4.4 / BOM #107, #108).
 */
#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

// Pass the shared event group so incoming Pi commands (STOP/RESUME/etc.) can
// set/clear cross-core event bits.
void comms_init(EventGroupHandle_t events);

void comms_publish_telemetry();   // publish latest sensor snapshot to MQTT topics
void comms_poll_pi();             // drain UART commands from the Pi
