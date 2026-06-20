/**
 * ota.cpp - ArduinoOTA setup with a required password.
 */
#include <ArduinoOTA.h>
#include "config.h"
#include "ota.h"

void ota_init() {
    ArduinoOTA.setHostname(OTA_HOSTNAME);
    ArduinoOTA.setPassword(OTA_PASSWORD);   // refuse unauthenticated OTA
    ArduinoOTA.begin();
}

void ota_handle() {
    ArduinoOTA.handle();
}
