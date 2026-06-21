// Minimal Arduino core mock for host-side syntax checking ONLY.
// Declares just the symbols the AgriRover firmware uses. Not for flashing.
#pragma once
#include <cstdint>
#include <cstddef>
#include <cstdio>
#include <cstring>
#include <cmath>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

using std::isnan;

// ---- digital/analog levels & modes ----
#define HIGH         0x1
#define LOW          0x0
#define INPUT        0x01
#define OUTPUT       0x03
#define INPUT_PULLUP 0x05
#define SERIAL_8N1   0x800001c

enum adc_attenuation_t { ADC_0db, ADC_2_5db, ADC_6db, ADC_11db };

// ---- helper macros (defined after <cmath> so they don't break std::abs) ----
#define constrain(amt, low, high) ((amt) < (low) ? (low) : ((amt) > (high) ? (high) : (amt)))
#ifndef abs
#define abs(x) ((x) > 0 ? (x) : -(x))
#endif

// ---- GPIO / timing ----
void pinMode(uint8_t pin, uint8_t mode);
void digitalWrite(uint8_t pin, uint8_t val);
int  digitalRead(uint8_t pin);
int  analogRead(uint8_t pin);
void analogReadResolution(uint8_t bits);
void analogSetAttenuation(adc_attenuation_t att);
void delay(uint32_t ms);
void delayMicroseconds(uint32_t us);
unsigned long millis(void);
unsigned long pulseIn(uint8_t pin, uint8_t state, unsigned long timeout);

// ---- ESP32 internal die-temperature sensor ----
float temperatureRead(void);

// ---- LEDC PWM ----
double ledcSetup(uint8_t channel, double freq, uint8_t resolutionBits);
void   ledcAttachPin(uint8_t pin, uint8_t channel);
void   ledcWrite(uint8_t channel, uint32_t duty);

// ---- HardwareSerial ----
class HardwareSerial {
public:
    HardwareSerial(int uartNum = 0) { (void)uartNum; }
    void begin(unsigned long baud, int config = SERIAL_8N1, int rxPin = -1, int txPin = -1) {
        (void)baud; (void)config; (void)rxPin; (void)txPin;
    }
    int  available() { return 0; }
    int  read() { return -1; }
    size_t write(const uint8_t* buf, size_t len) { (void)buf; (void)len; return len; }
    size_t write(uint8_t b) { (void)b; return 1; }
    void flush() {}
    int  printf(const char* fmt, ...) { (void)fmt; return 0; }
    size_t print(const char* s) { (void)s; return 0; }
    size_t println(const char* s) { (void)s; return 0; }
};

extern HardwareSerial Serial;
