// Minimal FreeRTOS mock for host-side syntax checking only. NOT for flashing.
#pragma once
#include <cstdint>

typedef uint32_t TickType_t;
typedef int      BaseType_t;
typedef unsigned UBaseType_t;
typedef void*    TaskHandle_t;
typedef void (*TaskFunction_t)(void*);

#define pdMS_TO_TICKS(ms) ((TickType_t)(ms))
#define pdTRUE  1
#define pdFALSE 0

void vTaskDelay(TickType_t ticks);
