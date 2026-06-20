// Minimal ESP task watchdog mock (host syntax check only).
#pragma once
#include <cstdint>

int esp_task_wdt_init(uint32_t timeout_s, bool panic);
int esp_task_wdt_add(void* handle);
int esp_task_wdt_reset(void);
