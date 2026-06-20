/**
 * gps.cpp - Neo-6M driver with SBAS/GAGAN, averaging, and DGPS injection.
 */
#include <Arduino.h>
#include <TinyGPSPlus.h>
#include <math.h>
#include "pins.h"
#include "config.h"
#include "gps.h"

static TinyGPSPlus    gps;
static HardwareSerial GPSser(1);   // UART1

// ---- UBX helpers ----
static void ubxChecksum(const uint8_t* payload, uint16_t len, uint8_t* ckA, uint8_t* ckB) {
    uint8_t a = 0, b = 0;
    for (uint16_t i = 0; i < len; i++) { a += payload[i]; b += a; }
    *ckA = a;
    *ckB = b;
}

// Send a UBX frame: class, id, payload. Checksum spans class..end of payload.
static void ubxSend(uint8_t cls, uint8_t id, const uint8_t* payload, uint16_t len) {
    uint8_t head[6] = { 0xB5, 0x62, cls, id, (uint8_t)(len & 0xFF), (uint8_t)(len >> 8) };
    // checksum over [cls, id, len_lo, len_hi, payload...]
    uint8_t buf[64];
    uint16_t n = 0;
    buf[n++] = cls; buf[n++] = id;
    buf[n++] = (uint8_t)(len & 0xFF); buf[n++] = (uint8_t)(len >> 8);
    for (uint16_t i = 0; i < len && n < sizeof(buf); i++) buf[n++] = payload[i];
    uint8_t ckA, ckB;
    ubxChecksum(buf, n, &ckA, &ckB);
    GPSser.write(head, 6);
    if (len) GPSser.write(payload, len);
    GPSser.write(ckA);
    GPSser.write(ckB);
    GPSser.flush();
}

// UBX-CFG-SBAS: enable SBAS, ranging + corrections, auto-scan all PRNs (the
// receiver will lock GAGAN where available).
static void gpsEnableSbas() {
    uint8_t payload[8] = {
        0x01,        // mode: SBAS enabled
        0x03,        // usage: range + diffCorr
        0x03,        // maxSBAS channels
        0x00,        // scanmode2
        0x00, 0x00, 0x00, 0x00  // scanmode1 = 0 -> auto-scan all PRNs
    };
    ubxSend(0x06, 0x16, payload, sizeof(payload));
}

void gps_init() {
    GPSser.begin(GPS_BAUD, SERIAL_8N1, PIN_GPS_RX, PIN_GPS_TX);
#if GPS_SBAS_ENABLE
    delay(200);
    gpsEnableSbas();
#endif
}

void gps_update() {
    while (GPSser.available()) gps.encode((char)GPSser.read());
}

bool gps_fix_valid() {
    return gps.location.isValid() && gps.location.age() < GPS_FIX_MAX_AGE_MS;
}

bool gps_get(double* lat, double* lng) {
    if (!gps_fix_valid()) return false;
    *lat = gps.location.lat();
    *lng = gps.location.lng();
    return true;
}

void gps_inject_rtcm(const uint8_t* buf, size_t len) {
    GPSser.write(buf, len);   // forwarded to the receiver's RX pin
}

int gps_robust_mean(const double* lat, const double* lng, int n,
                    double* outLat, double* outLng) {
    if (n <= 0) return 0;

    double mLat = 0, mLng = 0;
    for (int i = 0; i < n; i++) { mLat += lat[i]; mLng += lng[i]; }
    mLat /= n; mLng /= n;

    if (n < 4) {  // too few to reject outliers meaningfully
        *outLat = mLat; *outLng = mLng;
        return n;
    }

    // Per-sample squared distance from the mean; reject beyond 2 sigma.
    double var = 0;
    for (int i = 0; i < n; i++) {
        double dlat = lat[i] - mLat, dlng = lng[i] - mLng;
        var += dlat * dlat + dlng * dlng;
    }
    var /= n;
    double thresh = 4.0 * var;   // (2 sigma)^2

    double sLat = 0, sLng = 0;
    int used = 0;
    for (int i = 0; i < n; i++) {
        double dlat = lat[i] - mLat, dlng = lng[i] - mLng;
        if (dlat * dlat + dlng * dlng <= thresh) {
            sLat += lat[i]; sLng += lng[i]; used++;
        }
    }
    if (used == 0) { *outLat = mLat; *outLng = mLng; return n; }
    *outLat = sLat / used;
    *outLng = sLng / used;
    return used;
}

bool gps_collect_average(double* outLat, double* outLng, int* nUsed) {
    static double latBuf[GPS_AVG_SAMPLES];
    static double lngBuf[GPS_AVG_SAMPLES];
    int collected = 0;

    for (int i = 0; i < GPS_AVG_SAMPLES; i++) {
        unsigned long deadline = millis() + GPS_AVG_GAP_MS;
        while (millis() < deadline) gps_update();
        double la, ln;
        if (gps_get(&la, &ln)) {
            latBuf[collected] = la;
            lngBuf[collected] = ln;
            collected++;
        }
    }
    if (collected == 0) { if (nUsed) *nUsed = 0; return false; }

    int used = gps_robust_mean(latBuf, lngBuf, collected, outLat, outLng);
    if (nUsed) *nUsed = used;
    return true;
}
