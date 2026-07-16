/**
 * telemetry.h - One-line JSON telemetry over USB serial.
 */
#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

void telemetry_init(EventGroupHandle_t events);
void telemetry_print();   // print one "TLM {...}" line from the latest snapshot
