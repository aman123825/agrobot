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
    float moisture;         // %
    float conductivity;     // uS/cm
    float temperature;      // degC
    bool  valid;
};

struct Telemetry {
    NpkReading npk;
    float air_temp_c;       // DHT22
    float air_humidity;     // DHT22
    float soil_moisture_pct;// capacitive
    float tds_ppm;
    float battery_v;
    double lat, lng;        // GPS
    bool  gps_fix;
};

void sensors_init();
void sensors_poll();                 // refresh all sensors into the shared snapshot
const Telemetry& sensors_snapshot(); // latest readings (read by comms)
float sensors_read_battery_v();
