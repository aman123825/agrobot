/**
 * commands.h - Plain-text serial command link (USB) to the laptop.
 */
#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

void commands_init(EventGroupHandle_t events);
void commands_poll();   // collect USB serial lines and dispatch them
