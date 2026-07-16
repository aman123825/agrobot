/**
 * commands.cpp - Plain-text command protocol over USB serial.
 *
 * One command per line, replies "ACK <cmd>" or "NAK <reason>". This is a
 * wired USB link to the operator's laptop, so no HMAC auth here - the full
 * firmware (../firmware) adds the authenticated Pi link and MQTT.
 *
 * Drive commands (FWD/BACK/LEFT/RIGHT/SETPWM) refresh the dead-man timer;
 * hold the key down in the laptop console to keep moving.
 */
#include <Arduino.h>
#include <ctype.h>
#include "pins.h"
#include "config.h"
#include "events.h"
#include "drive.h"
#include "telemetry.h"
#include "commands.h"

static EventGroupHandle_t sEvents = nullptr;
static unsigned long      sLastDriveCmdMs = 0;
static int                sSpeed = MANUAL_DRIVE_SPEED;

static char   sBuf[96];
static size_t sLen = 0;

void commands_init(EventGroupHandle_t events) {
    sEvents = events;
    sLastDriveCmdMs = millis();
}

unsigned long commands_ms_since_drive_cmd() { return millis() - sLastDriveCmdMs; }

static void driveCmd(int16_t left, int16_t right) {
    sLastDriveCmdMs = millis();
    drive_set(left, right);
}

static void printHelp() {
    Serial.println("HELP commands:");
    Serial.println("  FWD | BACK | LEFT | RIGHT   drive (auto-stops after deadman timeout)");
    Serial.println("  DRIVE_STOP                  stop motors");
    Serial.println("  STOP | RESUME               latch / clear emergency halt");
    Serial.println("  SPEED <0-255>               set manual drive duty");
    Serial.println("  SETPWM <l> <r>              per-side duty, -255..255");
    Serial.println("  DOSE                        run the dosing sequence (drive freezes)");
    Serial.println("  PUMP_DISABLE | PUMP_ENABLE  block / allow dosing");
    Serial.println("  STATUS                      print a telemetry line now");
    Serial.println("  PING                        link check");
}

static void execute(char* cmd) {
    for (char* p = cmd; *p; p++) *p = toupper((unsigned char)*p);
    EventBits_t bits = sEvents ? xEventGroupGetBits(sEvents) : 0;

    if (!strcmp(cmd, "FWD")) {
        if (bits & EVT_OBSTACLE) { Serial.println("NAK obstacle"); return; }
        driveCmd(sSpeed, sSpeed);
    }
    else if (!strcmp(cmd, "BACK"))       driveCmd(-sSpeed, -sSpeed);
    else if (!strcmp(cmd, "LEFT"))       driveCmd(-sSpeed, sSpeed);
    else if (!strcmp(cmd, "RIGHT"))      driveCmd(sSpeed, -sSpeed);
    else if (!strcmp(cmd, "DRIVE_STOP")) drive_stop();
    else if (!strcmp(cmd, "STOP")) {
        xEventGroupSetBits(sEvents, EVT_HALT);
        drive_stop();
    }
    else if (!strcmp(cmd, "RESUME"))       xEventGroupClearBits(sEvents, EVT_HALT);
    else if (!strcmp(cmd, "DOSE"))         xEventGroupSetBits(sEvents, EVT_DOSE_REQUEST);
    else if (!strcmp(cmd, "PUMP_DISABLE")) xEventGroupSetBits(sEvents, EVT_PUMP_DISABLE);
    else if (!strcmp(cmd, "PUMP_ENABLE"))  xEventGroupClearBits(sEvents, EVT_PUMP_DISABLE);
    else if (!strncmp(cmd, "SPEED", 5)) {
        int v;
        if (sscanf(cmd, "SPEED %d", &v) == 1 && v >= 0 && v <= 255) sSpeed = v;
        else { Serial.printf("NAK parse %s\n", cmd); return; }
    }
    else if (!strncmp(cmd, "SETPWM", 6)) {
        int l, r;
        if (sscanf(cmd, "SETPWM %d %d", &l, &r) == 2) {
            driveCmd((int16_t)constrain(l, -255, 255),
                     (int16_t)constrain(r, -255, 255));
        } else { Serial.printf("NAK parse %s\n", cmd); return; }
    }
    else if (!strcmp(cmd, "STATUS")) { telemetry_print(); }
    else if (!strcmp(cmd, "PING"))   { /* reply below is the point */ }
    else if (!strcmp(cmd, "HELP"))   { printHelp(); }
    else { Serial.printf("NAK unknown %s\n", cmd); return; }

    Serial.printf("ACK %s\n", cmd);
}

void commands_poll() {
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\r') continue;
        if (c == '\n') {
            sBuf[sLen] = '\0';
            if (sLen > 0) execute(sBuf);
            sLen = 0;
        } else if (sLen < sizeof(sBuf) - 1) {
            sBuf[sLen++] = c;
        } else {
            sLen = 0;   // overlong line: discard
            Serial.println("NAK overflow");
        }
    }
}
