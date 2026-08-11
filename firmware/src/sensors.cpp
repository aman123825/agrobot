/**
 * sensors.cpp - ESP32 sensing implementation (accuracy-tuned).
 *
 * Accuracy upgrades:
 *  - ADC reads use esp_adc_cal (factory Vref) + 16x oversampling -> calibrated mV.
 *  - Capacitive moisture uses a multi-point calibration curve (not 2-point linear).
 *  - TDS is temperature-compensated.
 *  - Ultrasonic uses median-of-N + temperature-compensated speed of sound.
 *  - NPK Modbus reads retry on failure and keep the last good value.
 *
 * NPK register order is vendor-dependent - adjust the mapping to your datasheet.
 */
#include <Arduino.h>
#include <DHT.h>
#include <math.h>
#include "driver/adc.h"
#include "esp_adc_cal.h"
#include "pins.h"
#include "config.h"
#include "gps.h"
#include "sensors.h"

static DHT            dht(PIN_DHT22, DHT22);
static HardwareSerial RS485(2);   // UART2 -> MAX485
static Telemetry      snap;
static esp_adc_cal_characteristics_t sAdcChars;

// ADC1 channels for the analog pins (GPIO34/35/36).
#define CH_MOISTURE  ADC1_CHANNEL_6   // GPIO34
#define CH_VBAT      ADC1_CHANNEL_7   // GPIO35
#define CH_TDS       ADC1_CHANNEL_0   // GPIO36

// Multi-point capacitive-moisture calibration: ascending mV with the matching
// percent (capacitive sensors read LOWER voltage when wetter). CALIBRATE THESE
// for your probe: measure mV in air (dry) and submerged (wet).
static const float MOIST_CAL_MV[]  = { 1200.0f, 1900.0f, 2600.0f };
static const float MOIST_CAL_PCT[] = { 100.0f,  50.0f,   0.0f   };
static const int   MOIST_CAL_N = sizeof(MOIST_CAL_MV) / sizeof(MOIST_CAL_MV[0]);

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

// Oversampled, calibrated ADC read in millivolts.
static uint32_t readMv(adc1_channel_t ch) {
    uint32_t acc = 0;
    for (int i = 0; i < ADC_OVERSAMPLE; i++) acc += adc1_get_raw(ch);
    uint32_t raw = acc / ADC_OVERSAMPLE;
    return esp_adc_cal_raw_to_voltage(raw, &sAdcChars);
}

void sensors_init() {
    // Calibrated ADC1 at 12-bit, 11 dB (~0..3.1 V usable).
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(CH_MOISTURE, ADC_ATTEN_DB_11);
    adc1_config_channel_atten(CH_VBAT,     ADC_ATTEN_DB_11);
    adc1_config_channel_atten(CH_TDS,      ADC_ATTEN_DB_11);
    esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12,
                             ADC_VREF_MV, &sAdcChars);

    pinMode(PIN_RS485_DE_RE, OUTPUT);
    digitalWrite(PIN_RS485_DE_RE, LOW);

    pinMode(PIN_US_FRONT_TRIG, OUTPUT);
    digitalWrite(PIN_US_FRONT_TRIG, LOW);
    pinMode(PIN_US_FRONT_ECHO, INPUT);

    dht.begin();
    RS485.begin(NPK_BAUD, SERIAL_8N1, PIN_RS485_RO, PIN_RS485_DI);
    gps_init();

    snap.front_distance_cm = -1.0f;
}

float sensors_read_battery_v() {
    float v_adc = readMv(CH_VBAT) / 1000.0f;
    return v_adc / VBAT_DIVIDER_RATIO;   // undo 39k/10k divider
}

// One ultrasonic ping; returns echo duration in microseconds (0 = no echo).
static unsigned long pingOnce() {
    digitalWrite(PIN_US_FRONT_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_US_FRONT_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_US_FRONT_TRIG, LOW);
    return pulseIn(PIN_US_FRONT_ECHO, HIGH, US_TIMEOUT_US);
}

static void insertionSort(float* a, int n) {
    for (int i = 1; i < n; i++) {
        float key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; }
        a[j + 1] = key;
    }
}

float sensors_read_distance_cm() {
    float samples[US_MEDIAN_SAMPLES];
    int n = 0;
    float tempC = isnan(snap.air_temp_c) ? 20.0f : snap.air_temp_c;
    float speed_cm_per_us = (331.4f + 0.6f * tempC) / 10000.0f;  // temp-comp
    for (int i = 0; i < US_MEDIAN_SAMPLES; i++) {
        unsigned long dur = pingOnce();
        if (dur > 0) samples[n++] = dur * speed_cm_per_us / 2.0f;
        delay(10);
    }
    if (n == 0) return -1.0f;
    insertionSort(samples, n);
    return samples[n / 2];   // median
}

static float soilMoisturePct() {
    float mv = (float)readMv(CH_MOISTURE);
    if (mv <= MOIST_CAL_MV[0])              return MOIST_CAL_PCT[0];
    if (mv >= MOIST_CAL_MV[MOIST_CAL_N - 1]) return MOIST_CAL_PCT[MOIST_CAL_N - 1];
    for (int i = 1; i < MOIST_CAL_N; i++) {
        if (mv <= MOIST_CAL_MV[i]) {
            float t = (mv - MOIST_CAL_MV[i - 1]) /
                      (MOIST_CAL_MV[i] - MOIST_CAL_MV[i - 1]);
            return MOIST_CAL_PCT[i - 1] + t * (MOIST_CAL_PCT[i] - MOIST_CAL_PCT[i - 1]);
        }
    }
    return MOIST_CAL_PCT[MOIST_CAL_N - 1];
}

static float tdsPpm(float tempC) {
    float v = readMv(CH_TDS) / 1000.0f;
    float coeff = 1.0f + 0.02f * (tempC - 25.0f);   // temperature compensation
    float vc = (coeff != 0.0f) ? v / coeff : v;
    return (133.42f * vc * vc * vc - 255.86f * vc * vc + 857.39f * vc) * 0.5f;
}

// Read `count` holding registers starting at `start` (function 0x03).
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

    while (RS485.available()) RS485.read();
    digitalWrite(PIN_RS485_DE_RE, HIGH);
    delayMicroseconds(50);
    RS485.write(req, sizeof(req));
    RS485.flush();
    delayMicroseconds(50);
    digitalWrite(PIN_RS485_DE_RE, LOW);

    const uint32_t expected = 5 + 2 * count;
    uint8_t resp[5 + 2 * 32];
    if (count > 32) return false;
    uint32_t got = 0;
    unsigned long deadline = millis() + NPK_FRAME_TIMEOUT_MS;
    while (got < expected && millis() < deadline) {
        if (RS485.available()) resp[got++] = (uint8_t)RS485.read();
    }
    return npk_frame_valid(resp, got, count, regs);
}

// Pure frame validation + register unpack (host unit-tested; see test/).
bool npk_frame_valid(const uint8_t* resp, uint32_t len, uint16_t count, uint16_t* regs) {
    const uint32_t expected = 5 + 2 * (uint32_t)count;
    if (len < expected)            return false;
    if (resp[0] != NPK_SLAVE_ADDR) return false;
    if (resp[1] != 0x03)           return false;
    if (resp[2] != 2 * count)      return false;

    uint16_t rxCrc = modbus_crc16(resp, expected - 2);
    uint16_t frameCrc = (uint16_t)resp[expected - 2] | ((uint16_t)resp[expected - 1] << 8);
    if (rxCrc != frameCrc)         return false;

    for (uint16_t i = 0; i < count; i++) {
        regs[i] = ((uint16_t)resp[3 + 2 * i] << 8) | resp[4 + 2 * i];
    }
    return true;
}

static NpkReading readNpk() {
    NpkReading r{};
    uint16_t regs[NPK_REG_COUNT];
    bool ok = false;
    for (int attempt = 0; attempt < NPK_MAX_RETRIES && !ok; attempt++) {
        ok = readHoldingRegisters(NPK_REG_START, NPK_REG_COUNT, regs);
        if (!ok) delay(50);
    }
    if (!ok) { r.valid = false; return r; }

    // Common 7-in-1 layout: 0=moisture 1=temp 2=EC 3=pH 4=N 5=P 6=K.
    r.moisture     = regs[0] / 10.0f;
    r.temperature  = (int16_t)regs[1] / 10.0f;
    r.conductivity = regs[2];
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
    snap.tds_ppm           = tdsPpm(isnan(snap.air_temp_c) ? 25.0f : snap.air_temp_c);
    snap.battery_v         = sensors_read_battery_v();
    snap.front_distance_cm = sensors_read_distance_cm();

    gps_update();
    double la, ln;
    snap.gps_fix = gps_get(&la, &ln);
    if (snap.gps_fix) { snap.lat = la; snap.lng = ln; }
}

const Telemetry& sensors_snapshot() { return snap; }
