/**
 * sensors.cpp - Basic-bot sensing: moisture, battery, DHT22, HC-SR04, NPK.
 *
 * - ADC reads use esp_adc_cal (factory Vref) + oversampling -> calibrated mV.
 * - Capacitive moisture uses a multi-point calibration curve.
 * - Ultrasonic uses median-of-N + temperature-compensated speed of sound.
 * - NPK Modbus RTU is hand-rolled (CRC-16); failed reads back off so a
 *   missing probe doesn't stall the sensor loop.
 *
 * NPK register order is vendor-dependent - check your probe's datasheet and
 * adjust the mapping at the bottom of readNpk().
 */
#include <Arduino.h>
#include <DHT.h>
#include <math.h>
#include "driver/adc.h"
#include "esp_adc_cal.h"
#include "pins.h"
#include "config.h"
#include "sensors.h"

static DHT            dht(PIN_DHT22, DHT22);
static HardwareSerial RS485(2);   // UART2 -> MAX485
static Telemetry      snap;
static esp_adc_cal_characteristics_t sAdcChars;
static uint32_t       sNpkNextAttemptMs = 0;

#define CH_MOISTURE  ADC1_CHANNEL_6   // GPIO34
#define CH_VBAT      ADC1_CHANNEL_7   // GPIO35

// Multi-point capacitive-moisture calibration: ascending mV with the matching
// percent (capacitive sensors read LOWER voltage when wetter). CALIBRATE for
// your probe: note the "moist_mv" telemetry field in air (dry) and in water.
static const float MOIST_CAL_MV[]  = { 1200.0f, 1900.0f, 2600.0f };
static const float MOIST_CAL_PCT[] = { 100.0f,  50.0f,   0.0f   };
static const int   MOIST_CAL_N = sizeof(MOIST_CAL_MV) / sizeof(MOIST_CAL_MV[0]);

// ---- Modbus RTU CRC-16 (poly 0xA001) ----
static uint16_t modbusCrc16(const uint8_t* buf, uint32_t len) {
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
    return esp_adc_cal_raw_to_voltage(acc / ADC_OVERSAMPLE, &sAdcChars);
}

void sensors_init() {
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(CH_MOISTURE, ADC_ATTEN_DB_11);
    adc1_config_channel_atten(CH_VBAT,     ADC_ATTEN_DB_11);
    esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_11, ADC_WIDTH_BIT_12,
                             ADC_VREF_MV, &sAdcChars);

    pinMode(PIN_RS485_DE_RE, OUTPUT);
    digitalWrite(PIN_RS485_DE_RE, LOW);

    // Init all 3 ultrasonic sensors (left / center / right)
    const uint8_t usTrig[] = {PIN_US_LEFT_TRIG, PIN_US_CENTER_TRIG, PIN_US_RIGHT_TRIG};
    const uint8_t usEcho[] = {PIN_US_LEFT_ECHO, PIN_US_CENTER_ECHO, PIN_US_RIGHT_ECHO};
    for (int i = 0; i < 3; i++) {
        pinMode(usTrig[i], OUTPUT);
        digitalWrite(usTrig[i], LOW);
        pinMode(usEcho[i], INPUT);
    }

    dht.begin();
    RS485.begin(NPK_BAUD, SERIAL_8N1, PIN_RS485_RO, PIN_RS485_DI);
}

// ---- Ultrasonic (3 sensors: left, center, right) ----
static unsigned long pingOnce(uint8_t trigPin, uint8_t echoPin) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    return pulseIn(echoPin, HIGH, US_TIMEOUT_US);
}

static void insertionSort(float* a, int n) {
    for (int i = 1; i < n; i++) {
        float key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; }
        a[j + 1] = key;
    }
}

static float medianPing(uint8_t trigPin, uint8_t echoPin, float speed_cm_per_us) {
    float samples[US_MEDIAN_SAMPLES];
    int n = 0;
    for (int i = 0; i < US_MEDIAN_SAMPLES; i++) {
        unsigned long dur = pingOnce(trigPin, echoPin);
        if (dur > 0) samples[n++] = dur * speed_cm_per_us / 2.0f;
        delay(5);
    }
    if (n == 0) return -1.0f;
    insertionSort(samples, n);
    return samples[n / 2];
}

void sensors_poll_fast() {
    float tempC = isnan(snap.air_temp_c) ? 20.0f : snap.air_temp_c;
    float speed_cm_per_us = (331.4f + 0.6f * tempC) / 10000.0f;
    snap.left_distance_cm   = medianPing(PIN_US_LEFT_TRIG,   PIN_US_LEFT_ECHO,   speed_cm_per_us);
    snap.center_distance_cm = medianPing(PIN_US_CENTER_TRIG, PIN_US_CENTER_ECHO, speed_cm_per_us);
    snap.right_distance_cm  = medianPing(PIN_US_RIGHT_TRIG,  PIN_US_RIGHT_ECHO,  speed_cm_per_us);
}

// ---- Moisture ----
static float soilMoisturePct(float mv) {
    if (mv <= MOIST_CAL_MV[0])               return MOIST_CAL_PCT[0];
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

// ---- NPK (Modbus function 0x03: read holding registers) ----
static bool readHoldingRegisters(uint16_t start, uint16_t count, uint16_t* regs) {
    uint8_t req[8];
    req[0] = NPK_SLAVE_ADDR;
    req[1] = 0x03;
    req[2] = (uint8_t)(start >> 8);
    req[3] = (uint8_t)(start & 0xFF);
    req[4] = (uint8_t)(count >> 8);
    req[5] = (uint8_t)(count & 0xFF);
    uint16_t crc = modbusCrc16(req, 6);
    req[6] = (uint8_t)(crc & 0xFF);
    req[7] = (uint8_t)(crc >> 8);

    while (RS485.available()) RS485.read();
    digitalWrite(PIN_RS485_DE_RE, HIGH);
    delayMicroseconds(50);
    RS485.write(req, sizeof(req));
    RS485.flush();
    delayMicroseconds(50);
    digitalWrite(PIN_RS485_DE_RE, LOW);

    if (count > 32) return false;
    const uint32_t expected = 5 + 2 * count;
    uint8_t resp[5 + 2 * 32];
    uint32_t got = 0;
    unsigned long deadline = millis() + NPK_FRAME_TIMEOUT_MS;
    while (got < expected && millis() < deadline) {
        if (RS485.available()) resp[got++] = (uint8_t)RS485.read();
    }
    if (got < expected)            return false;
    if (resp[0] != NPK_SLAVE_ADDR) return false;
    if (resp[1] != 0x03)           return false;
    if (resp[2] != 2 * count)      return false;

    uint16_t rxCrc = modbusCrc16(resp, expected - 2);
    uint16_t frameCrc = (uint16_t)resp[expected - 2] | ((uint16_t)resp[expected - 1] << 8);
    if (rxCrc != frameCrc)         return false;

    for (uint16_t i = 0; i < count; i++) {
        regs[i] = ((uint16_t)resp[3 + 2 * i] << 8) | resp[4 + 2 * i];
    }
    return true;
}

static void readNpk() {
    if (millis() < sNpkNextAttemptMs) return;   // backing off after failures

    uint16_t regs[NPK_REG_COUNT];
    bool ok = false;
    for (int attempt = 0; attempt < NPK_MAX_RETRIES && !ok; attempt++) {
        ok = readHoldingRegisters(NPK_REG_START, NPK_REG_COUNT, regs);
        if (!ok) delay(50);
    }
    if (!ok) {
        snap.npk.valid = false;   // keep last numbers, flag them stale
        sNpkNextAttemptMs = millis() + NPK_FAIL_BACKOFF_MS;
        return;
    }
    // Common 7-in-1 layout: 0=moisture 1=temp 2=EC 3=pH 4=N 5=P 6=K.
    snap.npk.moisture     = regs[0] / 10.0f;
    snap.npk.temperature  = (int16_t)regs[1] / 10.0f;
    snap.npk.conductivity = regs[2];
    snap.npk.ph           = regs[3] / 10.0f;
    snap.npk.n            = regs[4];
    snap.npk.p            = regs[5];
    snap.npk.k            = regs[6];
    snap.npk.valid        = true;
}

void sensors_poll_slow() {
    readNpk();

    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t)) snap.air_temp_c   = t;
    if (!isnan(h)) snap.air_humidity = h;

    float mv = (float)readMv(CH_MOISTURE);
    snap.soil_moisture_mv  = mv;
    snap.soil_moisture_pct = soilMoisturePct(mv);

    float v_adc = readMv(CH_VBAT) / 1000.0f;
    snap.battery_v   = v_adc / VBAT_DIVIDER_RATIO;   // undo 39k/10k divider
    snap.battery_pct = constrain(
        (snap.battery_v - LIPO_CUTOFF_V) / (LIPO_FULL_V - LIPO_CUTOFF_V) * 100.0f,
        0.0f, 100.0f);

    snap.chip_temp_c = temperatureRead();
}

const Telemetry& sensors_snapshot() { return snap; }
