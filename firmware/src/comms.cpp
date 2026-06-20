/**
 * comms.cpp - WiFi/MQTT publish + the UART command link to the Raspberry Pi.
 *
 * Pi -> ESP32 (newline-terminated commands over UART0):
 *   STOP, RESUME, EVT_TILT_HALT          - hard halt / release
 *   FWD, BACK, LEFT, RIGHT, DRIVE_STOP   - manual drive
 *   DOSE                                 - request one dosing cycle
 *   PUMP_DISABLE, PUMP_ENABLE            - block / allow dosing (tank empty)
 *   PAUSE_IRRIGATION, RESUME_IRRIGATION  - rain pause
 * ESP32 -> Pi: "ACK <cmd>" plus periodic telemetry is published over MQTT.
 */
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"
#include "events.h"
#include "sensors.h"
#include "drive.h"
#include "comms.h"

static WiFiClient         wifiClient;
static PubSubClient       mqtt(wifiClient);
static EventGroupHandle_t sEvents = nullptr;
static unsigned long      sLastReconnectMs = 0;

static void ensureConnected() {
    // Throttle reconnect attempts so we never block the drive loop hard.
    if (WiFi.status() == WL_CONNECTED && mqtt.connected()) return;
    unsigned long now = millis();
    if (now - sLastReconnectMs < 3000) return;
    sLastReconnectMs = now;

    if (WiFi.status() != WL_CONNECTED) {
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);   // non-blocking
    }
    if (WiFi.status() == WL_CONNECTED && !mqtt.connected()) {
        mqtt.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
        mqtt.connect(MQTT_CLIENT_ID);
    }
}

void comms_init(EventGroupHandle_t events) {
    sEvents = events;
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    mqtt.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
}

void comms_publish_telemetry() {
    ensureConnected();
    if (!mqtt.connected()) return;
    mqtt.loop();

    const Telemetry& t = sensors_snapshot();
    char buf[256];

    snprintf(buf, sizeof(buf),
             "{\"valid\":%d,\"n\":%.1f,\"p\":%.1f,\"k\":%.1f,\"ph\":%.2f,"
             "\"ec\":%.0f,\"soil_t\":%.1f,\"soil_m\":%.1f}",
             t.npk.valid ? 1 : 0, t.npk.n, t.npk.p, t.npk.k, t.npk.ph,
             t.npk.conductivity, t.npk.temperature, t.npk.moisture);
    mqtt.publish(TOPIC_NPK, buf);

    snprintf(buf, sizeof(buf), "{\"lat\":%.6f,\"lng\":%.6f,\"fix\":%d}",
             t.lat, t.lng, t.gps_fix ? 1 : 0);
    mqtt.publish(TOPIC_GPS, buf);

    snprintf(buf, sizeof(buf),
             "{\"batt_v\":%.2f,\"air_t\":%.1f,\"air_h\":%.1f,\"tds\":%.0f,"
             "\"moist\":%.1f,\"dist_cm\":%.1f}",
             t.battery_v, t.air_temp_c, t.air_humidity, t.tds_ppm,
             t.soil_moisture_pct, t.front_distance_cm);
    mqtt.publish(TOPIC_STATUS, buf);
}

void comms_publish_alert(const char* msg) {
    if (mqtt.connected()) mqtt.publish(TOPIC_ALERT, msg);
}

static void handleCommand(const char* cmd) {
    const int spd = MANUAL_DRIVE_SPEED;

    if      (!strcmp(cmd, "STOP") || !strcmp(cmd, "EVT_TILT_HALT"))
        xEventGroupSetBits(sEvents, EVT_HALT);
    else if (!strcmp(cmd, "RESUME"))
        xEventGroupClearBits(sEvents, EVT_HALT);
    else if (!strcmp(cmd, "FWD"))         drive_set(spd,  spd);
    else if (!strcmp(cmd, "BACK"))        drive_set(-spd, -spd);
    else if (!strcmp(cmd, "LEFT"))        drive_set(-spd, spd);
    else if (!strcmp(cmd, "RIGHT"))       drive_set(spd,  -spd);
    else if (!strcmp(cmd, "DRIVE_STOP"))  drive_set(0, 0);
    else if (!strcmp(cmd, "DOSE"))        xEventGroupSetBits(sEvents, EVT_DOSE_REQUEST);
    else if (!strcmp(cmd, "PUMP_DISABLE"))xEventGroupSetBits(sEvents, EVT_PUMP_DISABLE);
    else if (!strcmp(cmd, "PUMP_ENABLE")) xEventGroupClearBits(sEvents, EVT_PUMP_DISABLE);
    else if (!strcmp(cmd, "PAUSE_IRRIGATION"))  xEventGroupSetBits(sEvents, EVT_PAUSE_IRRIG);
    else if (!strcmp(cmd, "RESUME_IRRIGATION")) xEventGroupClearBits(sEvents, EVT_PAUSE_IRRIG);
    else { Serial.printf("NAK %s\n", cmd); return; }

    Serial.printf("ACK %s\n", cmd);
}

void comms_poll_pi() {
    static char line[64];
    static size_t idx = 0;
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\n' || c == '\r') {
            if (idx > 0) {
                line[idx] = '\0';
                handleCommand(line);
                idx = 0;
            }
        } else if (idx < sizeof(line) - 1) {
            line[idx++] = c;
        } else {
            idx = 0;  // overflow -> drop the line
        }
    }
}
