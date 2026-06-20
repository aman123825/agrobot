/**
 * sensors.h - ESP32-side sensing stack (circuit §4 / BOM Layer 4).
 *
 * NPK (RS485/Modbus), DHT22, capacitive moisture, TDS, front ultrasonic,
 * GPS (UART1), and battery voltage.
 */
#pragma once
#include <stdint.h>

struct NpkReading {
    float n, p, k;          // mg/kg
    float ph;
    float moisture;         // % (from the probe)
    float conductivity;     // uS/cm
    float temperature;      // degC (soil, from the probe)
    bool  valid;
};

struct Telemetry {
    NpkReading npk;
    float air_temp_c;        // DHT22
    float air_humidity;      // DHT22
    float soil_moisture_pct; // capacitive sensor (calibrated)
    float tds_ppm;
    float battery_v;
    float front_distance_cm; // HC-SR04 front (-1 = no echo)
    double lat, lng;         // GPS
    bool  gps_fix;
};

void sensors_init();
void sensors_poll();                  // refresh all sensors into the shared snapshot
const Telemetry& sensors_snapshot();  // latest readings (read by comms / main)
float sensors_read_battery_v();
float sensors_read_distance_cm();      // single HC-SR04 ping (front)

// Modbus helper exposed for host unit-testing of the CRC/parse logic.
uint16_t modbus_crc16(const uint8_t* buf, uint32_t len);
