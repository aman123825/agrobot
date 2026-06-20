/**
 * ota.h - Password-protected over-the-air firmware updates (ArduinoOTA).
 *
 * For production, also enable Secure Boot v2 + Flash Encryption so only signed
 * firmware can run and the link key can't be extracted (see SECURITY.md).
 */
#pragma once

void ota_init();     // call once after WiFi is up
void ota_handle();   // call frequently from a fast loop
