/**
 * comms.cpp - WiFi/MQTT + Pi UART bridge (skeleton).
 *
 * Pi -> ESP32 commands (over UART0): STOP, RESUME, LEFT, RIGHT, SPRAY_ON,
 *   SPRAY_OFF, PAUSE_IRRIGATION, EVT_TILT_HALT, PUMP_DISABLE.
 * ESP32 -> Pi: sensor_ack, gps_coords, battery_pct, mode_status, velocity.
 */
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"
#include "sensors.h"
#include "drive.h"
#include "comms.h"

// Event bits mirror main.cpp.
#define EVT_HALT        (1 << 0)
#define EVT_LOW_BATTERY (1 << 1)
#define EVT_PAUSE_IRRIG (1 << 3)

static WiFiClient       wifiClient;
static PubSubClient     mqtt(wifiClient);
static EventGroupHandle_t gEvents = nullptr;

static void ensureConnected() {
    if (WiFi.status() != WL_CONNECTED) {
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    }
    if (!mqtt.connected()) {
        mqtt.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
        mqtt.connect(MQTT_CLIENT_ID);
    }
}

void comms_init(EventGroupHandle_t events) {
    gEvents = events;
    WiFi.mode(WIFI_STA);
    ensureConnected();
}

void comms_publish_telemetry() {
    ensureConnected();
    mqtt.loop();
    const Telemetry& t = sensors_snapshot();
    char buf[256];
    // TODO: build proper JSON (ArduinoJson). Minimal payloads for now.
    snprintf(buf, sizeof(buf), "{\"n\":%.1f,\"p\":%.1f,\"k\":%.1f,\"ph\":%.2f}",
             t.npk.n, t.npk.p, t.npk.k, t.npk.ph);
    mqtt.publish(TOPIC_NPK, buf);
    snprintf(buf, sizeof(buf), "{\"lat\":%.6f,\"lng\":%.6f,\"fix\":%d}",
             t.lat, t.lng, t.gps_fix ? 1 : 0);
    mqtt.publish(TOPIC_GPS, buf);
    snprintf(buf, sizeof(buf), "{\"batt_v\":%.2f}", t.battery_v);
    mqtt.publish(TOPIC_STATUS, buf);
}

void comms_poll_pi() {
    static char line[64];
    static size_t idx = 0;
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\n' || idx >= sizeof(line) - 1) {
            line[idx] = '\0';
            idx = 0;
            if (!strcmp(line, "STOP") || !strcmp(line, "EVT_TILT_HALT"))
                xEventGroupSetBits(gEvents, EVT_HALT);
            else if (!strcmp(line, "RESUME"))
                xEventGroupClearBits(gEvents, EVT_HALT);
            else if (!strcmp(line, "PAUSE_IRRIGATION"))
                xEventGroupSetBits(gEvents, EVT_PAUSE_IRRIG);
            // TODO: LEFT/RIGHT/SPRAY_ON/SPRAY_OFF/PUMP_DISABLE
        } else {
            line[idx++] = c;
        }
    }
}
