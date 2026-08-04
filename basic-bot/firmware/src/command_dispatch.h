#pragma once

#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "control_state.h"

typedef void (*CommandReplyFn)(void* user, const char* line);

struct CommandContext {
    ControlSource source;
    CommandReplyFn reply;
    void* user;
};

void command_dispatch_init(EventGroupHandle_t events);
void command_dispatch(const CommandContext& ctx, const char* command);
