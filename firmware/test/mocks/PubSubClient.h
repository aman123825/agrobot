// Minimal PubSubClient (MQTT) mock (host syntax check only).
#pragma once
#include "WiFi.h"

class PubSubClient {
public:
    PubSubClient(WiFiClient& c) { (void)c; }
    PubSubClient& setServer(const char* host, int port) { (void)host; (void)port; return *this; }
    bool connect(const char* id) { (void)id; return false; }
    bool connect(const char* id, const char* user, const char* pass) {
        (void)id; (void)user; (void)pass; return false;
    }
    bool connected() { return false; }
    bool loop() { return false; }
    bool publish(const char* topic, const char* payload) { (void)topic; (void)payload; return false; }
};
