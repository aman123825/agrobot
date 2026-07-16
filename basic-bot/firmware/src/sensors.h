/**
 * sensors.h - Basic-bot sensing API + telemetry snapshot struct.
 */
#pragma once
#include <stdint.h>

struct NpkReading {
    bool     valid = false;   // last Modbus read succeeded
    float    moisture = 0;    // soil moisture % (probe's own reading)
    float    temperature = 0; // soil temperature degC
    uint16_t conductivity = 0;// EC uS/cm
    float    ph = 0;
    uint16_t n = 0, p = 0, k = 0;  // mg/kg
};

struct Telemetry {
    NpkReading npk;
    float air_temp_c   = NAN;   // DHT22
    float air_humidity = NAN;   // DHT22 %RH
    float soil_moisture_pct = 0;// capacitive sensor
    float soil_moisture_mv  = 0;// raw calibrated millivolts (for calibration)
    float battery_v    = 0;
    float battery_pct  = 0;
    float left_distance_cm   = -1.0f;  // -1 = no echo
    float center_distance_cm = -1.0f;
    float right_distance_cm  = -1.0f;
    float chip_temp_c  = 0;     // ESP32 die temperature
};

void sensors_init();
void sensors_poll_fast();   // ultrasonic only (call at 5 Hz)
void sensors_poll_slow();   // NPK, DHT22, moisture, battery (call at 1 Hz)
const Telemetry& sensors_snapshot();
