/**
 * comms.cpp - WiFi/MQTT publish + the AUTHENTICATED UART command link to the Pi.
 *
 * Inbound commands must be HMAC-signed envelopes (see secure_link.h). Plain or
 * replayed commands are rejected. Recognized inner commands:
 *   STOP, RESUME, EVT_TILT_HALT          - hard halt / release
 *   FWD, BACK, LEFT, RIGHT, DRIVE_STOP   - manual drive
 *   DOSE                                 - request one dosing cycle
 *   PUMP_DISABLE, PUMP_ENABLE            - block / allow dosing
 *   PAUSE_IRRIGATION, RESUME_IRRIGATION  - rain pause
 *
 * MQTT uses username/password and, when MQTT_USE_TLS is defined, TLS with a
 * pinned CA certificate.
 */
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"
#include "events.h"
#include "sensors.h"
#include "drive.h"
#include "secure_link.h"
#include "comms.h"

#ifdef MQTT_USE_TLS
#include <WiFiClientSecure.h>
static WiFiClientSecure netClient;
#else
static WiFiClient netClient;
#endif

static PubSubClient       mqtt(netClient);
static EventGroupHandle_t sEvents = nullptr;
static unsigned long      sLastReconnectMs = 0;
static unsigned long      sLastTamperAlertMs = 0;
static unsigned long      sLastCmdMs = 0;

static void ensureConnected() {
    if (WiFi.status() == WL_CONNECTED && mqtt.connected()) return;
    unsigned long now = millis();
    if (now - sLastReconnectMs < 3000) return;   // throttle; never block the loop hard
    sLastReconnectMs = now;

    if (WiFi.status() != WL_CONNECTED) {
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);     // non-blocking
        return;
    }
    if (!mqtt.connected()) {
        mqtt.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
        mqtt.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS);  // authenticated
    }
}

void comms_init(EventGroupHandle_t events) {
    sEvents = events;
    sLastCmdMs = millis();   // grace period before heartbeat can trip
    secure_link_init(COMMAND_HMAC_KEY, strlen(COMMAND_HMAC_KEY));

    WiFi.mode(WIFI_STA);
#ifdef MQTT_USE_TLS
    netClient.setCACert(MQTT_CA_CERT);            // pin the broker's CA
#endif
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

static void executeCommand(const char* cmd) {
    const int spd = MANUAL_DRIVE_SPEED;

    if      (!strcmp(cmd, "STOP") || !strcmp(cmd, "EVT_TILT_HALT"))
        xEventGroupSetBits(sEvents, EVT_HALT);
    else if (!strcmp(cmd, "RESUME"))            xEventGroupClearBits(sEvents, EVT_HALT);
    else if (!strcmp(cmd, "FWD"))               drive_set(spd,  spd);
    else if (!strcmp(cmd, "BACK"))              drive_set(-spd, -spd);
    else if (!strcmp(cmd, "LEFT"))              drive_set(-spd, spd);
    else if (!strcmp(cmd, "RIGHT"))             drive_set(spd,  -spd);
    else if (!strcmp(cmd, "DRIVE_STOP"))        drive_set(0, 0);
    else if (!strcmp(cmd, "DOSE"))              xEventGroupSetBits(sEvents, EVT_DOSE_REQUEST);
    else if (!strcmp(cmd, "PUMP_DISABLE"))      xEventGroupSetBits(sEvents, EVT_PUMP_DISABLE);
    else if (!strcmp(cmd, "PUMP_ENABLE"))       xEventGroupClearBits(sEvents, EVT_PUMP_DISABLE);
    else if (!strcmp(cmd, "PAUSE_IRRIGATION"))  xEventGroupSetBits(sEvents, EVT_PAUSE_IRRIG);
    else if (!strcmp(cmd, "RESUME_IRRIGATION")) xEventGroupClearBits(sEvents, EVT_PAUSE_IRRIG);
    else if (!strncmp(cmd, "SETPWM", 6)) {
        // Closed-loop output from the Pi's velocity PID: "SETPWM <left> <right>"
        int l = 0, r = 0;
        if (sscanf(cmd, "SETPWM %d %d", &l, &r) == 2) {
            l = (l > 255) ? 255 : (l < -255 ? -255 : l);
            r = (r > 255) ? 255 : (r < -255 ? -255 : r);
            drive_set((int16_t)l, (int16_t)r);
        } else { Serial.printf("NAK parse %s\n", cmd); return; }
    }
    else if (!strcmp(cmd, "PING")) { /* heartbeat only; SECURE_OK refreshed it */ }
    else { Serial.printf("NAK unknown %s\n", cmd); return; }

    Serial.printf("ACK %s\n", cmd);
}

unsigned long comms_ms_since_cmd() {
    return millis() - sLastCmdMs;
}

static void onAuthFailure(SecureResult r) {
    // Rate-limit tamper alerts to avoid flooding under attack.
    unsigned long now = millis();
    if (now - sLastTamperAlertMs > 5000) {
        sLastTamperAlertMs = now;
        if (r == SECURE_BAD_SIG || r == SECURE_LOCKED)
            comms_publish_alert("{\"type\":\"tamper\",\"link\":\"unauthorized_command\"}");
    }
    Serial.println("NAK auth");
}

void comms_poll_pi() {
    static char line[160];   // signed envelope is longer than a bare command
    static size_t idx = 0;
    char cmd[48];

    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\n' || c == '\r') {
            if (idx > 0) {
                line[idx] = '\0';
                SecureResult r = secure_link_check(line, cmd, sizeof(cmd));
                if (r == SECURE_OK) { sLastCmdMs = millis(); executeCommand(cmd); }
                else                onAuthFailure(r);
                idx = 0;
            }
        } else if (idx < sizeof(line) - 1) {
            line[idx++] = c;
        } else {
            idx = 0;  // overflow -> drop the line
        }
    }
}
