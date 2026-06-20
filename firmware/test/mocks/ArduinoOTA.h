// Minimal ArduinoOTA mock (host syntax check only).
#pragma once

class ArduinoOTAClass {
public:
    void setHostname(const char* h) { (void)h; }
    void setPassword(const char* p) { (void)p; }
    void begin() {}
    void handle() {}
};

extern ArduinoOTAClass ArduinoOTA;
