// Minimal DHT mock (host syntax check only).
#pragma once
#include <cstdint>

#define DHT11 11
#define DHT22 22

class DHT {
public:
    DHT(uint8_t pin, uint8_t type) { (void)pin; (void)type; }
    void  begin() {}
    float readTemperature() { return 0.0f; }
    float readHumidity() { return 0.0f; }
};
