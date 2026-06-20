// Minimal WiFi mock (host syntax check only).
#pragma once

#define WL_CONNECTED 3
enum WiFiModeAlias { WIFI_STA = 1, WIFI_AP = 2 };

class WiFiClient {
public:
    WiFiClient() {}
};

class WiFiClass {
public:
    void mode(int m) { (void)m; }
    int  begin(const char* ssid, const char* pass) { (void)ssid; (void)pass; return 0; }
    int  status() { return 0; }
};

extern WiFiClass WiFi;
