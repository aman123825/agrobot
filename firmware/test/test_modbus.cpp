// Host unit test for the Modbus CRC-16 used by sensors.cpp.
// Compiles the real sensors.cpp against the mocks and verifies CRC behavior.
#include "Arduino.h"
#include "sensors.h"
#include <cassert>
#include <cstdio>

// ---- definitions for the declared-only Arduino symbols sensors.cpp links to ----
void pinMode(uint8_t, uint8_t) {}
void digitalWrite(uint8_t, uint8_t) {}
int  digitalRead(uint8_t) { return 0; }
int  analogRead(uint8_t) { return 0; }
void analogReadResolution(uint8_t) {}
void analogSetAttenuation(adc_attenuation_t) {}
void delay(uint32_t) {}
void delayMicroseconds(uint32_t) {}
unsigned long millis() { return 0; }
unsigned long pulseIn(uint8_t, uint8_t, unsigned long) { return 0; }
double ledcSetup(uint8_t, double, uint8_t) { return 0; }
void   ledcAttachPin(uint8_t, uint8_t) {}
void   ledcWrite(uint8_t, uint32_t) {}
void   vTaskDelay(TickType_t) {}
HardwareSerial Serial;

int main() {
    // 1) Known Modbus vector: 01 03 00 00 00 01 -> CRC 0x0A84 (appended 84 0A).
    uint8_t known[] = {0x01, 0x03, 0x00, 0x00, 0x00, 0x01};
    uint16_t crc = modbus_crc16(known, sizeof(known));
    printf("known-vector CRC = 0x%04X (expect 0x0A84)\n", crc);
    assert(crc == 0x0A84);

    // 2) Self-check invariant: CRC over a frame that already includes its CRC == 0.
    uint8_t frame[8] = {0x01, 0x03, 0x00, 0x00, 0x00, 0x07, 0, 0};
    uint16_t c = modbus_crc16(frame, 6);
    frame[6] = (uint8_t)(c & 0xFF);
    frame[7] = (uint8_t)(c >> 8);
    uint16_t check = modbus_crc16(frame, 8);
    printf("self-check CRC over full frame = 0x%04X (expect 0x0000)\n", check);
    assert(check == 0x0000);

    printf("MODBUS CRC TESTS PASSED\n");
    return 0;
}
