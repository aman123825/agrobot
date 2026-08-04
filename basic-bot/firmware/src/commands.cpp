#include <Arduino.h>
#include "command_dispatch.h"
#include "commands.h"

static char sBuf[96];
static size_t sLen = 0;

static void serialReply(void*, const char* line) {
    Serial.println(line);
}

void commands_init(EventGroupHandle_t events) {
    command_dispatch_init(events);
}

void commands_poll() {
    const CommandContext ctx = {{ControlSource::USB_SERIAL, 0}, serialReply, nullptr};
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\r') continue;
        if (c == '\n') {
            sBuf[sLen] = '\0';
            if (sLen > 0) command_dispatch(ctx, sBuf);
            sLen = 0;
        } else if (sLen < sizeof(sBuf) - 1) {
            sBuf[sLen++] = c;
        } else {
            sLen = 0;
            Serial.println("NAK overflow");
        }
    }
}
