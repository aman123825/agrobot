/**
 * dosing.h - Sequential dosing state machine API.
 */
#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

void dosing_init(EventGroupHandle_t events);
bool dosing_run_sequence();   // blocking; asserts EVT_DOSING for the duration
