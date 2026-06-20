// Minimal ESP32 Preferences (NVS) mock (host syntax check only).
#pragma once
#include <cstdint>

class Preferences {
public:
    bool begin(const char* name, bool readOnly = false) { (void)name; (void)readOnly; return true; }
    void end() {}
    unsigned long long getULong64(const char* key, unsigned long long def = 0) {
        (void)key; return def;
    }
    size_t putULong64(const char* key, unsigned long long value) {
        (void)key; (void)value; return sizeof(value);
    }
};
