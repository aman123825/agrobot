/**
 * telemetry.cpp - Builds the "TLM {json}" line the laptop console parses.
 *
 * Composed into one buffer and written with a single Serial.println so lines
 * from the two tasks never interleave mid-line.
 */
#include <Arduino.h>
#include <math.h>
#include "config.h"
#include "events.h"
#include "sensors.h"
#include "telemetry.h"

static EventGroupHandle_t sEvents = nullptr;

void telemetry_init(EventGroupHandle_t events) { sEvents = events; }

// JSON has no NaN: write a fixed-point number, or "null" when invalid.
static int numOrNull(char* out, size_t cap, float v, int decimals) {
    if (isnan(v) || isinf(v)) return snprintf(out, cap, "null");
    return snprintf(out, cap, "%.*f", decimals, v);
}

static const char* stateStr(EventBits_t bits) {
    if (bits & EVT_DOSING)      return "DOSING";
    if (bits & EVT_HALT)        return "HALT";
    if (bits & EVT_LOW_BATTERY) return "LOW_BATT";
    if (bits & EVT_OVERTEMP)    return "OVERTEMP";
    if (bits & EVT_OBSTACLE)    return "OBSTACLE";
    return "OK";
}

void telemetry_print() {
    const Telemetry& t = sensors_snapshot();
    EventBits_t bits = sEvents ? xEventGroupGetBits(sEvents) : 0;

    char air_c[16], air_rh[16], dist_l[16], dist_c[16], dist_r[16];
    numOrNull(air_c,  sizeof(air_c),  t.air_temp_c, 1);
    numOrNull(air_rh, sizeof(air_rh), t.air_humidity, 1);
    numOrNull(dist_l, sizeof(dist_l), t.left_distance_cm   < 0 ? NAN : t.left_distance_cm,   1);
    numOrNull(dist_c, sizeof(dist_c), t.center_distance_cm < 0 ? NAN : t.center_distance_cm, 1);
    numOrNull(dist_r, sizeof(dist_r), t.right_distance_cm  < 0 ? NAN : t.right_distance_cm,  1);

    char npk[160];
    if (t.npk.valid) {
        snprintf(npk, sizeof(npk),
                 "{\"n\":%u,\"p\":%u,\"k\":%u,\"ph\":%.1f,\"ec\":%u,"
                 "\"soil_c\":%.1f,\"soil_moist\":%.1f}",
                 t.npk.n, t.npk.p, t.npk.k, t.npk.ph, t.npk.conductivity,
                 t.npk.temperature, t.npk.moisture);
    } else {
        snprintf(npk, sizeof(npk), "null");
    }

    char line[512];
    snprintf(line, sizeof(line),
             "TLM {\"up_ms\":%lu,\"state\":\"%s\",\"batt_v\":%.2f,"
             "\"batt_pct\":%.0f,\"moist_pct\":%.1f,\"moist_mv\":%.0f,"
             "\"air_c\":%s,\"air_rh\":%s,"
             "\"dist_l\":%s,\"dist_c\":%s,\"dist_r\":%s,"
             "\"chip_c\":%.1f,\"pump_disabled\":%s,\"npk\":%s}",
             (unsigned long)millis(), stateStr(bits), t.battery_v,
             t.battery_pct, t.soil_moisture_pct, t.soil_moisture_mv,
             air_c, air_rh, dist_l, dist_c, dist_r, t.chip_temp_c,
             (bits & EVT_PUMP_DISABLE) ? "true" : "false", npk);
    Serial.println(line);
}
