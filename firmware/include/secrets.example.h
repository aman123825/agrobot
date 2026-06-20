/**
 * secrets.example.h - copy to include/secrets.h (gitignored) and fill in.
 * NEVER commit secrets.h. Alternatively pass these as -D build flags.
 *
 * Generate a strong link key, e.g.:  openssl rand -hex 32
 * The COMMAND_HMAC_KEY here MUST exactly match the Pi's AGRO_LINK_KEY.
 */
#pragma once

#define WIFI_SSID        "your-ssid"
#define WIFI_PASSWORD    "your-wifi-password"

#define MQTT_BROKER_HOST "192.168.1.10"
#define MQTT_USER        "agrorover"
#define MQTT_PASS        "strong-mqtt-password"

#define COMMAND_HMAC_KEY "replace-with-32-plus-byte-random-secret"

// ---- Optional: encrypted MQTT over TLS ----
// #define MQTT_USE_TLS
// static const char* MQTT_CA_CERT =
//     "-----BEGIN CERTIFICATE-----\n"
//     "...your broker CA cert...\n"
//     "-----END CERTIFICATE-----\n";
