/**
 * sensors.cpp - ESP32 sensing implementation (skeleton).
 *
 * RS485 direction is controlled by PIN_RS485_DE_RE: set HIGH to transmit the
 * 8-byte Modbus query, LOW to receive the response (circuit §4.2).
 */
#include <Arduino.h>
#include <DHT.h>
#include <TinyGPSPlus.h>
#include "pins.h"
#include "config.h"
#include "sensors.h"

static DHT        dht(PIN_DHT22, DHT22);
static TinyGPSPlus gps;
static HardwareSerial RS485(2);   // UART2 -> MAX485
static HardwareSerial GPSser(1);  // UART1 -> Neo-6M (RX only)
static Telemetry      snap;

void sensors_init() {
    analogReadResolution(12);                 // 0..4095 on ADC1
    pinMode(PIN_RS485_DE_RE, OUTPUT);
    digitalWrite(PIN_RS485_DE_RE, LOW);        // default to receive
    dht.begin();
    RS485.begin(NPK_BAUD, SERIAL_8N1, PIN_RS485_RO, PIN_RS485_DI);
    GPSser.begin(9600, SERIAL_8N1, PIN_GPS_RX, -1);  // RX only
}

float sensors_read_battery_v() {
    int raw = analogRead(PIN_VBAT_SENSE);
    float v_adc = (raw / 4095.0f) * 3.3f;
    return v_adc / VBAT_DIVIDER_RATIO;         // undo 39k/10k divider
}

static NpkReading readNpk() {
    NpkReading r{};
    // TODO: build Modbus RTU request for NPK_SLAVE_ADDR, toggle DE/RE, parse
    // the 7-parameter response, CRC-check. Placeholder marks invalid for now.
    r.valid = false;
    return r;
}

void sensors_poll() {
    snap.npk              = readNpk();
    snap.air_temp_c       = dht.readTemperature();
    snap.air_humidity     = dht.readHumidity();
    snap.soil_moisture_pct= 100.0f * (1.0f - analogRead(PIN_MOISTURE) / 4095.0f); // TODO calibrate
    snap.tds_ppm          = (analogRead(PIN_TDS) / 4095.0f) * 1000.0f;            // TODO calibrate
    snap.battery_v        = sensors_read_battery_v();

    while (GPSser.available()) gps.encode(GPSser.read());
    if (gps.location.isValid()) {
        snap.lat = gps.location.lat();
        snap.lng = gps.location.lng();
        snap.gps_fix = true;
    }
}

const Telemetry& sensors_snapshot() { return snap; }
