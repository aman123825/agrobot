// Minimal WiFiClientSecure mock (host syntax check only).
#pragma once
#include "WiFi.h"

class WiFiClientSecure : public WiFiClient {
public:
    void setCACert(const char* cert) { (void)cert; }
    void setInsecure() {}
};
