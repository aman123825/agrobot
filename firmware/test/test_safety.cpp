// Host unit tests: drive-inhibit event mask (events.h), HMAC-SHA256 command
// authentication, replay rejection, and failure lockout (secure_link.cpp).
//
// Compiles the REAL secure_link.cpp against the mocks. A self-contained
// SHA-256/HMAC implementation (validated against an RFC 4231 test vector)
// backs the mbedtls mock so the authentication path executes for real.
//
// Build & run:
//   clang++ -std=gnu++17 -I test/mocks -I include -I src \
//           src/secure_link.cpp test/test_safety.cpp -o /tmp/test_safety && /tmp/test_safety
#include "Arduino.h"
#include "events.h"
#include "config.h"
#include "secure_link.h"
#include "mbedtls/md.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <initializer_list>

// ---- controllable fake clock (secure_link uses millis() for lockout) ----
static unsigned long gFakeMillis = 0;
unsigned long millis() { return gFakeMillis; }

// ---- minimal but real SHA-256 (FIPS 180-4) ----
namespace sha256impl {
static const uint32_t K[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static inline uint32_t rotr(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }

struct Ctx { uint32_t h[8]; uint8_t buf[64]; uint64_t len = 0; size_t fill = 0; };

static void init(Ctx& c) {
    static const uint32_t H0[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
                                   0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
    memcpy(c.h, H0, sizeof(H0)); c.len = 0; c.fill = 0;
}

static void block(Ctx& c, const uint8_t* p) {
    uint32_t w[64];
    for (int i = 0; i < 16; i++)
        w[i] = (uint32_t)p[4*i] << 24 | (uint32_t)p[4*i+1] << 16 | (uint32_t)p[4*i+2] << 8 | p[4*i+3];
    for (int i = 16; i < 64; i++) {
        uint32_t s0 = rotr(w[i-15],7) ^ rotr(w[i-15],18) ^ (w[i-15] >> 3);
        uint32_t s1 = rotr(w[i-2],17) ^ rotr(w[i-2],19) ^ (w[i-2] >> 10);
        w[i] = w[i-16] + s0 + w[i-7] + s1;
    }
    uint32_t a=c.h[0],b=c.h[1],cc=c.h[2],d=c.h[3],e=c.h[4],f=c.h[5],g=c.h[6],h=c.h[7];
    for (int i = 0; i < 64; i++) {
        uint32_t S1 = rotr(e,6) ^ rotr(e,11) ^ rotr(e,25);
        uint32_t ch = (e & f) ^ (~e & g);
        uint32_t t1 = h + S1 + ch + K[i] + w[i];
        uint32_t S0 = rotr(a,2) ^ rotr(a,13) ^ rotr(a,22);
        uint32_t mj = (a & b) ^ (a & cc) ^ (b & cc);
        uint32_t t2 = S0 + mj;
        h=g; g=f; f=e; e=d+t1; d=cc; cc=b; b=a; a=t1+t2;
    }
    c.h[0]+=a; c.h[1]+=b; c.h[2]+=cc; c.h[3]+=d; c.h[4]+=e; c.h[5]+=f; c.h[6]+=g; c.h[7]+=h;
}

static void update(Ctx& c, const uint8_t* p, size_t n) {
    c.len += n;
    while (n) {
        size_t take = 64 - c.fill; if (take > n) take = n;
        memcpy(c.buf + c.fill, p, take);
        c.fill += take; p += take; n -= take;
        if (c.fill == 64) { block(c, c.buf); c.fill = 0; }
    }
}

static void final(Ctx& c, uint8_t out[32]) {
    uint64_t bits = c.len * 8;
    uint8_t pad = 0x80;
    update(c, &pad, 1);
    uint8_t zero = 0;
    while (c.fill != 56) update(c, &zero, 1);
    uint8_t lenb[8];
    for (int i = 0; i < 8; i++) lenb[i] = (uint8_t)(bits >> (56 - 8*i));
    update(c, lenb, 8);
    for (int i = 0; i < 8; i++) {
        out[4*i]   = (uint8_t)(c.h[i] >> 24);
        out[4*i+1] = (uint8_t)(c.h[i] >> 16);
        out[4*i+2] = (uint8_t)(c.h[i] >> 8);
        out[4*i+3] = (uint8_t)(c.h[i]);
    }
}

static void hash(const uint8_t* p, size_t n, uint8_t out[32]) {
    Ctx c; init(c); update(c, p, n); final(c, out);
}

static void hmac(const uint8_t* key, size_t keyLen,
                 const uint8_t* msg, size_t msgLen, uint8_t out[32]) {
    uint8_t k[64] = {0};
    if (keyLen > 64) hash(key, keyLen, k); else memcpy(k, key, keyLen);
    uint8_t ipad[64], opad[64];
    for (int i = 0; i < 64; i++) { ipad[i] = k[i] ^ 0x36; opad[i] = k[i] ^ 0x5c; }
    uint8_t inner[32];
    Ctx c; init(c); update(c, ipad, 64); update(c, msg, msgLen); final(c, inner);
    init(c); update(c, opad, 64); update(c, inner, 32); final(c, out);
}
} // namespace sha256impl

// ---- back the mbedtls mock with the real implementation ----
static const mbedtls_md_info_t* kInfo = (const mbedtls_md_info_t*)1;
const mbedtls_md_info_t* mbedtls_md_info_from_type(mbedtls_md_type_t) { return kInfo; }
int mbedtls_md_hmac(const mbedtls_md_info_t*,
                    const unsigned char* key, size_t keylen,
                    const unsigned char* input, size_t ilen,
                    unsigned char* output) {
    sha256impl::hmac(key, keylen, input, ilen, output);
    return 0;
}

// ---- helpers ----
static const char* kKey = COMMAND_HMAC_KEY;  // same default the firmware uses

// Sign "v1|<ctr>|<cmd>" exactly the way the Pi does.
static void sign_envelope(unsigned long long ctr, const char* cmd, char* out, size_t outSz) {
    char prefix[192];
    snprintf(prefix, sizeof(prefix), "v1|%llu|%s", ctr, cmd);
    uint8_t mac[32];
    sha256impl::hmac((const uint8_t*)kKey, strlen(kKey),
                     (const uint8_t*)prefix, strlen(prefix), mac);
    char hex[2 * CMD_AUTH_TRUNC_BYTES + 1];
    for (int i = 0; i < CMD_AUTH_TRUNC_BYTES; i++) sprintf(hex + 2*i, "%02x", mac[i]);
    snprintf(out, outSz, "%s|%s", prefix, hex);
}

// ---- tests ----
static void test_event_mask() {
    // The six inhibiting conditions, and only those, are in the mask (Table 2).
    const unsigned inhibit = EVT_HALT | EVT_LOW_BATTERY | EVT_DOSING |
                             EVT_OBSTACLE | EVT_LINK_LOST | EVT_OVERTEMP;
    assert(EVT_DRIVE_INHIBIT == inhibit);
    assert((EVT_DRIVE_INHIBIT & EVT_DOSE_REQUEST) == 0);
    assert((EVT_DRIVE_INHIBIT & EVT_PAUSE_IRRIG) == 0);
    assert((EVT_DRIVE_INHIBIT & EVT_PUMP_DISABLE) == 0);

    // All nine bits are distinct (no aliasing).
    const unsigned bits[9] = {EVT_HALT, EVT_LOW_BATTERY, EVT_DOSE_REQUEST,
                              EVT_PAUSE_IRRIG, EVT_DOSING, EVT_OBSTACLE,
                              EVT_PUMP_DISABLE, EVT_LINK_LOST, EVT_OVERTEMP};
    unsigned seen = 0;
    for (unsigned b : bits) { assert((seen & b) == 0); seen |= b; }

    // Any single inhibiting bit is sufficient to inhibit drive.
    for (unsigned b : {EVT_HALT, EVT_LOW_BATTERY, EVT_DOSING,
                       EVT_OBSTACLE, EVT_LINK_LOST, EVT_OVERTEMP})
        assert((b & EVT_DRIVE_INHIBIT) != 0);

    printf("EVENT-MASK TESTS PASSED\n");
}

static void test_hmac_vector() {
    // RFC 4231 test case 2: key "Jefe", data "what do ya want for nothing?"
    const char* key = "Jefe";
    const char* msg = "what do ya want for nothing?";
    const uint8_t expect[32] = {
        0x5b,0xdc,0xc1,0x46,0xbf,0x60,0x75,0x4e,0x6a,0x04,0x24,0x26,0x08,0x95,0x75,0xc7,
        0x5a,0x00,0x3f,0x08,0x9d,0x27,0x39,0x83,0x9d,0xec,0x58,0xb9,0x64,0xec,0x38,0x43};
    uint8_t mac[32];
    sha256impl::hmac((const uint8_t*)key, strlen(key), (const uint8_t*)msg, strlen(msg), mac);
    assert(memcmp(mac, expect, 32) == 0);
    printf("HMAC-SHA256 RFC 4231 VECTOR PASSED\n");
}

static void test_auth_and_replay() {
    char env[256], cmd[128];

    // Fail closed before a key is configured.
    assert(secure_link_check("v1|1|MOVE 10 10|00", cmd, sizeof(cmd)) == SECURE_NOKEY);

    secure_link_init(kKey, strlen(kKey));

    // 1) Authentic, fresh command is accepted and the payload extracted.
    sign_envelope(1, "MOVE 10 10", env, sizeof(env));
    assert(secure_link_check(env, cmd, sizeof(cmd)) == SECURE_OK);
    assert(strcmp(cmd, "MOVE 10 10") == 0);

    // 2) Exact replay of the same envelope is rejected.
    assert(secure_link_check(env, cmd, sizeof(cmd)) == SECURE_REPLAY);

    // 3) A stale (lower) counter with a valid signature is rejected.
    sign_envelope(5, "MOVE 0 0", env, sizeof(env));
    assert(secure_link_check(env, cmd, sizeof(cmd)) == SECURE_OK);
    sign_envelope(3, "DOSE 1", env, sizeof(env));
    assert(secure_link_check(env, cmd, sizeof(cmd)) == SECURE_REPLAY);

    // 4) Tampered payload (signature no longer matches) is rejected.
    sign_envelope(6, "MOVE 10 10", env, sizeof(env));
    char* p = strstr(env, "MOVE 10 10");
    p[0] = 'D'; p[1] = 'O'; p[2] = 'S'; p[3] = 'E';  // MOVE -> DOSE, same length prefix
    assert(secure_link_check(env, cmd, sizeof(cmd)) == SECURE_BAD_SIG);

    // 5) Malformed envelopes are rejected without crashing.
    assert(secure_link_check("garbage", cmd, sizeof(cmd)) == SECURE_MALFORMED);
    assert(secure_link_check("v1|", cmd, sizeof(cmd)) == SECURE_MALFORMED);
    assert(secure_link_check("v1||", cmd, sizeof(cmd)) == SECURE_MALFORMED);

    printf("AUTHENTICATION + REPLAY TESTS PASSED\n");
}

static void test_lockout() {
    char env[256], cmd[128];

    // A valid command first: clears any failure count carried over from the
    // previous test (the firmware resets it only on a successful check).
    sign_envelope(50, "STATUS", env, sizeof(env));
    assert(secure_link_check(env, cmd, sizeof(cmd)) == SECURE_OK);

    // Drive the failure counter to the threshold with bad signatures.
    for (int i = 0; i < CMD_FAIL_LOCK_THRESHOLD; i++) {
        snprintf(env, sizeof(env), "v1|%d|MOVE 1 1|%032d", 100 + i, 0);  // bogus MAC
        assert(secure_link_check(env, cmd, sizeof(cmd)) == SECURE_BAD_SIG);
    }

    // Now locked: even a validly signed command is refused during cooldown.
    sign_envelope(200, "MOVE 2 2", env, sizeof(env));
    assert(secure_link_check(env, cmd, sizeof(cmd)) == SECURE_LOCKED);

    // After the cooldown elapses, valid commands are accepted again.
    gFakeMillis += CMD_LOCK_COOLDOWN_MS + 1;
    assert(secure_link_check(env, cmd, sizeof(cmd)) == SECURE_OK);
    assert(strcmp(cmd, "MOVE 2 2") == 0);

    printf("LOCKOUT TESTS PASSED\n");
}

int main() {
    test_event_mask();
    test_hmac_vector();
    test_auth_and_replay();
    test_lockout();
    printf("ALL SAFETY/SECURITY HOST TESTS PASSED\n");
    return 0;
}
