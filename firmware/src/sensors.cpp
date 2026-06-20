/**
 * sensors.cpp - ESP32 sensing implementation.
 *
 * RS485/NPK: PIN_RS485_DE_RE is driven HIGH to transmit the Modbus query and
 * LOW to receive the response (circuit §4.2). The 7-in-1 probe register order
 * is vendor-dependent - adjust the NPK_* mapping below to match your probe's
 * datasheet if your values look swapped.
 */
#include <Arduino.h>
#include <DHT.h>
#include <TinyGPSPlus.h>
#include "pins.h"
#include "config.h"
#include "sensors.h"

static DHT            dht(PIN_DHT22, DHT22);
static TinyGPSPlus    gps;
static HardwareSerial RS485(2);   // UART2 -> MAX485
static HardwareSerial GPSser(1);  // UART1 -> Neo-6M (RX only)
static Telemetry      snap;

// ---- Modbus RTU CRC-16 (poly 0xA001) ----
uint16_t modbus_crc16(const uint8_t* buf, uint32_t len) {
    uint16_t crc = 0xFFFF;
    for (uint32_t i = 0; i < len; i++) {
        crc ^= buf[i];
        for (int b = 0; b < 8; b++) {
            if (crc & 0x0001) { crc >>= 1; crc ^= 0xA001; }
            else              { crc >>= 1; }
        }
    }
    return crc;
}

void sensors_init() {
    analogReadResolution(12);                 // 0..4095 on ADC1
    analogSetAttenuation(ADC_11db);           // full ~0..3.3V range (inputs must stay <=3.3V)

    pinMode(PIN_RS485_DE_RE, OUTPUT);
    digitalWrite(PIN_RS485_DE_RE, LOW);        // default to receive

    pinMode(PIN_US_FRONT_TRIG, OUTPUT);
    digitalWrite(PIN_US_FRONT_TRIG, LOW);
    pinMode(PIN_US_FRONT_ECHO, INPUT);

    dht.begin();
    RS485.begin(NPK_BAUD, SERIAL_8N1, PIN_RS485_RO, PIN_RS485_DI);
    GPSser.begin(9600, SERIAL_8N1, PIN_GPS_RX, -1);  // RX only

    snap.front_distance_cm = -1.0f;
}

float sensors_read_battery_v() {
    int raw = analogRead(PIN_VBAT_SENSE);
    float v_adc = (raw / 4095.0f) * 3.3f;
    return v_adc / VBAT_DIVIDER_RATIO;         // undo 39k/10k divider
}

float sensors_read_distance_cm() {
    digitalWrite(PIN_US_FRONT_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_US_FRONT_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_US_FRONT_TRIG, LOW);

    unsigned long dur = pulseIn(PIN_US_FRONT_ECHO, HIGH, US_TIMEOUT_US);
    if (dur == 0) return -1.0f;                // no echo within range
    return dur / 58.0f;                        // us -> cm
}

static float soilMoisturePct() {
    int raw = analogRead(PIN_MOISTURE);
    float pct = (float)(MOIST_RAW_DRY - raw) /
                (float)(MOIST_RAW_DRY - MOIST_RAW_WET) * 100.0f;
    if (pct < 0)   pct = 0;
    if (pct > 100) pct = 100;
    return pct;
}

static float tdsPpm() {
    int raw = analogRead(PIN_TDS);
    float v = (raw / 4095.0f) * 3.3f;
    // DFRobot Gravity TDS transfer function (no temp compensation here).
    return (133.42f * v * v * v - 255.86f * v * v + 857.39f * v) * 0.5f;
}

// Read `count` holding registers starting at `start` (function 0x03).
// Returns true and fills regs[] on a CRC-valid response.
static bool readHoldingRegisters(uint16_t start, uint16_t count, uint16_t* regs) {
    uint8_t req[8];
    req[0] = NPK_SLAVE_ADDR;
    req[1] = 0x03;
    req[2] = (uint8_t)(start >> 8);
    req[3] = (uint8_t)(start & 0xFF);
    req[4] = (uint8_t)(count >> 8);
    req[5] = (uint8_t)(count & 0xFF);
    uint16_t crc = modbus_crc16(req, 6);
    req[6] = (uint8_t)(crc & 0xFF);
    req[7] = (uint8_t)(crc >> 8);

    // Transmit.
    while (RS485.available()) RS485.read();    // flush stale bytes
    digitalWrite(PIN_RS485_DE_RE, HIGH);
    delayMicroseconds(50);
    RS485.write(req, sizeof(req));
    RS485.flush();                              // wait until fully shifted out
    delayMicroseconds(50);
    digitalWrite(PIN_RS485_DE_RE, LOW);         // back to receive

    // Receive: addr,func,bytecount + 2*count data + 2 CRC.
    const uint32_t expected = 5 + 2 * count;
    uint8_t resp[5 + 2 * 32];
    if (count > 32) return false;
    uint32_t got = 0;
    unsigned long deadline = millis() + NPK_FRAME_TIMEOUT_MS;
    while (got < expected && millis() < deadline) {
        if (RS485.available()) resp[got++] = (uint8_t)RS485.read();
    }
    if (got < expected)              return false;
    if (resp[0] != NPK_SLAVE_ADDR)   return false;
    if (resp[1] != 0x03)             return false;
    if (resp[2] != 2 * count)        return false;

    uint16_t rxCrc = modbus_crc16(resp, expected - 2);
    uint16_t frameCrc = (uint16_t)resp[expected - 2] |
                        ((uint16_t)resp[expected - 1] << 8);
    if (rxCrc != frameCrc)           return false;

    for (uint16_t i = 0; i < count; i++) {
        regs[i] = ((uint16_t)resp[3 + 2 * i] << 8) | resp[4 + 2 * i];
    }
    return true;
}

static NpkReading readNpk() {
    NpkReading r{};
    uint16_t regs[NPK_REG_COUNT];
    if (!readHoldingRegisters(NPK_REG_START, NPK_REG_COUNT, regs)) {
        r.valid = false;
        return r;
    }
    // Common 7-in-1 layout: 0=moisture 1=temp 2=EC 3=pH 4=N 5=P 6=K.
    r.moisture     = regs[0] / 10.0f;
    r.temperature  = (int16_t)regs[1] / 10.0f;   // signed, 0.1 degC
    r.conductivity = regs[2];                    // uS/cm
    r.ph           = regs[3] / 10.0f;
    r.n            = regs[4];
    r.p            = regs[5];
    r.k            = regs[6];
    r.valid        = true;
    return r;
}

void sensors_poll() {
    snap.npk               = readNpk();
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    snap.air_temp_c        = isnan(t) ? snap.air_temp_c : t;
    snap.air_humidity      = isnan(h) ? snap.air_humidity : h;
    snap.soil_moisture_pct = soilMoisturePct();
    snap.tds_ppm           = tdsPpm();
    snap.battery_v         = sensors_read_battery_v();
    snap.front_distance_cm = sensors_read_distance_cm();

    while (GPSser.available()) gps.encode(GPSser.read());
    snap.gps_fix = gps.location.isValid() && gps.location.age() < GPS_FIX_MAX_AGE_MS;
    if (snap.gps_fix) {
        snap.lat = gps.location.lat();
        snap.lng = gps.location.lng();
    }
}

const Telemetry& sensors_snapshot() { return snap; }
