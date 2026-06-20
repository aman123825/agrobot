/**
 * secure_link.cpp - HMAC-SHA256 authenticated command verification.
 *
 * Uses the ESP32's bundled mbedTLS for HMAC and NVS (Preferences) to persist
 * the anti-replay counter. Comparison of the MAC is constant-time to avoid
 * leaking information through timing.
 */
#include <Arduino.h>
#include <Preferences.h>
#include <string.h>
#include <stdlib.h>
#include "mbedtls/md.h"
#include "config.h"
#include "secure_link.h"

static const uint8_t* sKey = nullptr;
static size_t         sKeyLen = 0;
static Preferences    sPrefs;
static unsigned long long sLastCounter = 0;
static unsigned long  sLastPersistMs = 0;
static int            sFailCount = 0;
static unsigned long  sLockUntilMs = 0;

static void hmac_sha256(const uint8_t* data, size_t len, uint8_t out[32]) {
    const mbedtls_md_info_t* info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
    mbedtls_md_hmac(info, sKey, sKeyLen, data, len, out);
}

// Constant-time compare of a hex string against raw bytes.
static bool ct_equal_hex(const char* hex, const uint8_t* raw, size_t rawLen) {
    if (strlen(hex) != rawLen * 2) return false;
    uint8_t diff = 0;
    for (size_t i = 0; i < rawLen; i++) {
        char b[3] = { hex[2 * i], hex[2 * i + 1], 0 };
        uint8_t v = (uint8_t)strtol(b, nullptr, 16);
        diff |= (uint8_t)(v ^ raw[i]);
    }
    return diff == 0;
}

void secure_link_init(const char* key, size_t keyLen) {
    sKey = (const uint8_t*)key;
    sKeyLen = keyLen;
    sPrefs.begin("agro", false);
    sLastCounter = sPrefs.getULong64("ctr", 0);
    sLastPersistMs = millis();
}

SecureResult secure_link_check(const char* line, char* outCmd, size_t outSz) {
    if (sKeyLen == 0)               return SECURE_NOKEY;          // fail closed
    if (millis() < sLockUntilMs)    return SECURE_LOCKED;
    if (strncmp(line, "v1|", 3) != 0) return SECURE_MALFORMED;

    const char* pCtr = line + 3;
    const char* bar2 = strchr(pCtr, '|');
    if (!bar2)                      return SECURE_MALFORMED;
    const char* cmd  = bar2 + 1;
    const char* barL = strrchr(line, '|');
    if (!barL || barL <= bar2)      return SECURE_MALFORMED;
    const char* hmacHex = barL + 1;

    // Parse counter.
    char ctrBuf[24];
    size_t cl = (size_t)(bar2 - pCtr);
    if (cl == 0 || cl >= sizeof(ctrBuf)) return SECURE_MALFORMED;
    memcpy(ctrBuf, pCtr, cl);
    ctrBuf[cl] = '\0';
    unsigned long long ctr = strtoull(ctrBuf, nullptr, 10);

    // Recompute HMAC over the signed prefix = everything before the last '|'.
    uint8_t mac[32];
    hmac_sha256((const uint8_t*)line, (size_t)(barL - line), mac);

    if (!ct_equal_hex(hmacHex, mac, CMD_AUTH_TRUNC_BYTES)) {
        if (++sFailCount >= CMD_FAIL_LOCK_THRESHOLD) {
            sLockUntilMs = millis() + CMD_LOCK_COOLDOWN_MS;
            sFailCount = 0;
        }
        return SECURE_BAD_SIG;
    }
    if (ctr <= sLastCounter)        return SECURE_REPLAY;

    // Authentic + fresh: commit the new counter and extract the command.
    sFailCount = 0;
    sLastCounter = ctr;
    // Throttle NVS writes (the counter advances every command). Persisting the
    // actual counter at most every CMD_CTR_PERSIST_INTERVAL_MS bounds flash
    // wear; the worst case after an ungraceful power loss is that commands from
    // the last interval could be replayed - an acceptable, tiny window.
    unsigned long now = millis();
    if (now - sLastPersistMs >= CMD_CTR_PERSIST_INTERVAL_MS) {
        sPrefs.putULong64("ctr", sLastCounter);
        sLastPersistMs = now;
    }

    size_t cmdLen = (size_t)(barL - cmd);
    if (cmdLen >= outSz) cmdLen = outSz - 1;
    memcpy(outCmd, cmd, cmdLen);
    outCmd[cmdLen] = '\0';
    return SECURE_OK;
}
