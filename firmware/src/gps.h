/**
 * gps.h - Neo-6M GPS with software accuracy upgrades.
 *
 * - Enables SBAS augmentation at boot (India: GAGAN) for ~1-1.5 m fixes.
 * - Stationary position averaging with outlier rejection for sub-meter
 *   waypoints (the rover stops to sample/dose, so averaging is very effective).
 * - Optional RTCM/DGPS correction injection to the GPS RX pin.
 *
 * Single-frequency L1 receiver: true cm-level RTK is not possible, but the
 * above gets the most out of the Neo-6M without new hardware.
 */
#pragma once
#include <stddef.h>
#include <stdint.h>

void gps_init();
void gps_update();                          // drain UART, update latest fix
bool gps_get(double* lat, double* lng);     // latest fix; returns true if valid
bool gps_fix_valid();

// Feed RTCM 2.x differential corrections to the receiver (DGPS). No-op if the
// GPS RX wire is not connected.
void gps_inject_rtcm(const uint8_t* buf, size_t len);

// Blocking robust average of `samples` fixes (~samples*GPS_AVG_GAP_MS ms).
// Use only when the rover is stationary. Returns true and fills outLat/outLng.
bool gps_collect_average(double* outLat, double* outLng, int* nUsed);

// Pure helper (exposed for host unit testing): outlier-rejected mean of n
// lat/lng samples. Returns number of inliers used (0 if n <= 0).
int gps_robust_mean(const double* lat, const double* lng, int n,
                    double* outLat, double* outLng);
