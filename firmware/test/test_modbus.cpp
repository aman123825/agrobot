// Host unit tests: Modbus CRC-16 (sensors.cpp) and GPS robust-mean (gps.cpp).
// Compiles the real sources against the mocks and executes the pure logic.
#include "Arduino.h"
#include "driver/adc.h"
#include "esp_adc_cal.h"
#include "sensors.h"
#include "gps.h"
#include <cassert>
#include <cmath>
#include <cstdio>

// ---- definitions for declared-only Arduino symbols the sources link to ----
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

// ---- ADC mock definitions ----
int adc1_config_width(adc_bits_width_t) { return 0; }
int adc1_config_channel_atten(adc1_channel_t, adc_atten_t) { return 0; }
int adc1_get_raw(adc1_channel_t) { return 2000; }
esp_adc_cal_value_t esp_adc_cal_characterize(adc_unit_t, adc_atten_t, adc_bits_width_t,
                                             uint32_t, esp_adc_cal_characteristics_t*) {
    return ESP_ADC_CAL_VAL_DEFAULT_VREF;
}
uint32_t esp_adc_cal_raw_to_voltage(uint32_t raw, const esp_adc_cal_characteristics_t*) {
    return raw;  // identity for the test
}

static void test_modbus() {
    uint8_t known[] = {0x01, 0x03, 0x00, 0x00, 0x00, 0x01};
    uint16_t crc = modbus_crc16(known, sizeof(known));
    printf("known-vector CRC = 0x%04X (expect 0x0A84)\n", crc);
    assert(crc == 0x0A84);

    uint8_t frame[8] = {0x01, 0x03, 0x00, 0x00, 0x00, 0x07, 0, 0};
    uint16_t c = modbus_crc16(frame, 6);
    frame[6] = (uint8_t)(c & 0xFF);
    frame[7] = (uint8_t)(c >> 8);
    assert(modbus_crc16(frame, 8) == 0x0000);
    printf("MODBUS CRC TESTS PASSED\n");
}

static void test_gps_robust_mean() {
    // 9 tight samples near (18.5200000, 73.8000000) + 1 gross outlier.
    double lat[10], lng[10];
    for (int i = 0; i < 9; i++) {
        lat[i] = 18.5200000 + (i - 4) * 0.0000010;  // ~0.1 m scatter
        lng[i] = 73.8000000 + (i - 4) * 0.0000010;
    }
    lat[9] = 18.5300000;  // ~1 km outlier
    lng[9] = 73.8100000;

    double oLat, oLng;
    int used = gps_robust_mean(lat, lng, 10, &oLat, &oLng);
    printf("robust-mean used %d/10 samples -> %.7f, %.7f\n", used, oLat, oLng);
    assert(used == 9);                       // the outlier was rejected
    assert(fabs(oLat - 18.5200000) < 1e-5);  // close to the true cluster
    assert(fabs(oLng - 73.8000000) < 1e-5);
    printf("GPS ROBUST-MEAN TEST PASSED\n");
}

int main() {
    test_modbus();
    test_gps_robust_mean();
    printf("ALL HOST TESTS PASSED\n");
    return 0;
}
