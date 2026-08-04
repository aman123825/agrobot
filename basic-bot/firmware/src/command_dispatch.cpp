#include <Arduino.h>
#include <ctype.h>
#include <string.h>
#include "config.h"
#include "events.h"
#include "control_state.h"
#include "telemetry.h"
#include "command_dispatch.h"

static EventGroupHandle_t sEvents = nullptr;

static void sendLine(const CommandContext& ctx, const char* line) {
    if (ctx.reply) ctx.reply(ctx.user, line);
}

static void replyf(const CommandContext& ctx, const char* format,
                   const char* value) {
    char line[128];
    snprintf(line, sizeof(line), format, value);
    sendLine(ctx, line);
}

static void printHelp(const CommandContext& ctx) {
    sendLine(ctx, "HELP commands:");
    sendLine(ctx, "  FWD | BACK | LEFT | RIGHT   drive (dead-man protected)");
    sendLine(ctx, "  DRIVE_STOP                  stop motors and release control");
    sendLine(ctx, "  STOP | RESUME               latch / clear emergency halt");
    sendLine(ctx, "  SPEED <0-255>               set manual drive duty");
    sendLine(ctx, "  SETPWM <l> <r>              per-side duty, -255..255");
    sendLine(ctx, "  DOSE                        run dosing (drive freezes)");
    sendLine(ctx, "  PROBE_DOWN | PROBE_UP       lower / raise the NPK probe (servo)");
    sendLine(ctx, "  PUMP_DISABLE | PUMP_ENABLE  block / allow dosing");
    sendLine(ctx, "  STATUS | PING | HELP");
}

static bool setMotion(const CommandContext& ctx, int16_t left, int16_t right) {
    if (!control_set_motion(ctx.source, left, right, millis())) {
        sendLine(ctx, "NAK controller_busy");
        return false;
    }
    return true;
}

void command_dispatch_init(EventGroupHandle_t events) {
    sEvents = events;
    control_state_init(MANUAL_DRIVE_SPEED);
}

void command_dispatch(const CommandContext& ctx, const char* command) {
    if (!command) return;

    char cmd[96];
    size_t len = strnlen(command, sizeof(cmd));
    if (len == 0) return;
    if (len >= sizeof(cmd)) {
        sendLine(ctx, "NAK overflow");
        return;
    }
    memcpy(cmd, command, len + 1);
    for (char* p = cmd; *p; p++) *p = toupper((unsigned char)*p);

    EventBits_t bits = sEvents ? xEventGroupGetBits(sEvents) : 0;
    bool accepted = true;

    if (!strcmp(cmd, "FWD")) {
        if (bits & EVT_OBSTACLE) { sendLine(ctx, "NAK obstacle"); return; }
        int speed = control_get_speed();
        accepted = setMotion(ctx, speed, speed);
    } else if (!strcmp(cmd, "BACK")) {
        int speed = control_get_speed();
        accepted = setMotion(ctx, -speed, -speed);
    } else if (!strcmp(cmd, "LEFT")) {
        int speed = control_get_speed();
        accepted = setMotion(ctx, -speed, speed);
    } else if (!strcmp(cmd, "RIGHT")) {
        int speed = control_get_speed();
        accepted = setMotion(ctx, speed, -speed);
    } else if (!strcmp(cmd, "DRIVE_STOP")) {
        if (control_source_owns_drive(ctx.source)) {
            control_stop_if_owner(ctx.source);
        } else if (control_has_owner()) {
            sendLine(ctx, "NAK controller_busy");
            return;
        } else {
            control_force_stop();
        }
    } else if (!strcmp(cmd, "STOP")) {
        if (sEvents) xEventGroupSetBits(sEvents, EVT_HALT);
        control_force_stop();
    } else if (!strcmp(cmd, "RESUME")) {
        if (sEvents) xEventGroupClearBits(sEvents, EVT_HALT);
    } else if (!strcmp(cmd, "DOSE")) {
        if (sEvents) xEventGroupSetBits(sEvents, EVT_DOSE_REQUEST);
    } else if (!strcmp(cmd, "PROBE_DOWN")) {
        if (sEvents) xEventGroupSetBits(sEvents, EVT_PROBE_DOWN_REQ);
    } else if (!strcmp(cmd, "PROBE_UP")) {
        if (sEvents) xEventGroupSetBits(sEvents, EVT_PROBE_UP_REQ);
    } else if (!strcmp(cmd, "PUMP_DISABLE")) {
        if (sEvents) xEventGroupSetBits(sEvents, EVT_PUMP_DISABLE);
    } else if (!strcmp(cmd, "PUMP_ENABLE")) {
        if (sEvents) xEventGroupClearBits(sEvents, EVT_PUMP_DISABLE);
    } else if (!strncmp(cmd, "SPEED", 5)) {
        int value;
        if (sscanf(cmd, "SPEED %d", &value) != 1 || value < 0 || value > 255) {
            replyf(ctx, "NAK parse %s", cmd);
            return;
        }
        if (!control_set_speed(ctx.source, value)) {
            sendLine(ctx, "NAK controller_busy");
            return;
        }
    } else if (!strncmp(cmd, "SETPWM", 6)) {
        int left, right;
        if (sscanf(cmd, "SETPWM %d %d", &left, &right) != 2) {
            replyf(ctx, "NAK parse %s", cmd);
            return;
        }
        left = constrain(left, -255, 255);
        right = constrain(right, -255, 255);
        // Any positive component can move the chassis toward an obstacle;
        // pure reverse and in-place opposite-sign turns remain available.
        if ((bits & EVT_OBSTACLE) && (left > 0 || right > 0) && left * right >= 0) {
            sendLine(ctx, "NAK obstacle");
            return;
        }
        accepted = setMotion(ctx, left, right);
    } else if (!strcmp(cmd, "STATUS")) {
        telemetry_print();
    } else if (!strcmp(cmd, "PING")) {
        // The ACK below is the link check.
    } else if (!strcmp(cmd, "HELP")) {
        printHelp(ctx);
    } else {
        replyf(ctx, "NAK unknown %s", cmd);
        return;
    }

    if (accepted) replyf(ctx, "ACK %s", cmd);
}
