# Host verification harness

These files exist **only for offline verification on a development machine** —
they are not compiled into the firmware that runs on the ESP32.

- `mocks/` — minimal stand-in headers (`Arduino.h`, `DHT.h`, `TinyGPSPlus.h`,
  `WiFi.h`, `PubSubClient.h`, `freertos/*`) that declare just the symbols the
  firmware uses, so a host compiler can type-check the sources without the
  Espressif toolchain or internet access.
- `test_modbus.cpp` — compiles the real `sensors.cpp` and `gps.cpp` against the
  mocks and executes the Modbus CRC-16 (probe frame validation) against a known
  vector + the self-check invariant, and the GPS robust-mean outlier rejection.
- `test_safety.cpp` — compiles the real `secure_link.cpp` against the mocks and
  executes the `EVT_DRIVE_INHIBIT` event-mask logic, HMAC-SHA256 command
  authentication (validated against an RFC 4231 test vector), anti-replay
  counter rejection, and the bad-signature lockout/cooldown path.

`pio run` (build/flash) ignores this directory and uses the real Arduino/ESP32
framework, so these mocks never affect the firmware image.

## Run the checks

```bash
cd firmware

# 1) Syntax/type-check every source file
for f in src/*.cpp; do
  clang++ -fsyntax-only -std=gnu++17 -I test/mocks -I include -I src "$f"
done

# 2) Execute the Modbus CRC + GPS robust-mean unit tests
clang++ -std=gnu++17 -I test/mocks -I include -I src \
        src/sensors.cpp src/gps.cpp test/test_modbus.cpp -o /tmp/test_modbus && /tmp/test_modbus

# 3) Execute the safety/security unit tests (event mask, HMAC, replay, lockout)
clang++ -std=gnu++17 -I test/mocks -I include -I src \
        src/secure_link.cpp test/test_safety.cpp -o /tmp/test_safety && /tmp/test_safety
```

## Real hardware build

```bash
cd firmware
pio run            # compile for ESP32 DevKit V1 (needs internet for first run)
pio run -t upload  # flash
```
