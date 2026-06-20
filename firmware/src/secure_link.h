/**
 * secure_link.h - Authenticated, anti-replay command link.
 *
 * Every command from the Pi must arrive as a signed envelope:
 *     v1|<counter>|<command>|<hmac_hex>
 * where hmac = HMAC-SHA256(key, "v1|<counter>|<command>") truncated to
 * CMD_AUTH_TRUNC_BYTES and hex-encoded. The counter must strictly increase
 * (anti-replay); the last accepted value is persisted in NVS across reboots.
 *
 * This makes spoofed or replayed drive/dosing commands on the UART link
 * computationally infeasible without the shared secret.
 */
#pragma once
#include <stddef.h>

enum SecureResult {
    SECURE_OK,         // authentic + fresh; outCmd populated
    SECURE_BAD_SIG,    // HMAC mismatch
    SECURE_REPLAY,     // counter not greater than last accepted
    SECURE_MALFORMED,  // wrong envelope shape
    SECURE_LOCKED,     // too many failures; in cooldown
    SECURE_NOKEY,      // no key configured (fail closed)
};

void         secure_link_init(const char* key, size_t keyLen);
SecureResult secure_link_check(const char* line, char* outCmd, size_t outSz);
