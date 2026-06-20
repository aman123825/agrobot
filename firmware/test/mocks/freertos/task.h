// Minimal FreeRTOS task mock (host syntax check only).
#pragma once
#include "freertos/FreeRTOS.h"

BaseType_t xTaskCreatePinnedToCore(TaskFunction_t fn, const char* name,
                                   uint32_t stackWords, void* params,
                                   UBaseType_t prio, TaskHandle_t* handle,
                                   BaseType_t core);
