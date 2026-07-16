# AgriRover — Basic Bot (Step 1, no AI)

Self-contained code for the **Core-tier build**: ESP32 only — no Raspberry Pi,
no camera, no Coral, no WiFi/MQTT. You drive the rover and read its sensors
from a **laptop over USB serial**.

Everything that runs on this bot lives in this folder. The pin map is the same
as the full firmware (`../firmware`), so nothing gets rewired when you upgrade.

## What it does

- **Tank drive** via 2× BTS7960 (hold a key on the laptop to drive; a dead-man
  timer stops the motors the moment you release it or the cable drops).
- **Obstacle guard**: 3× HC-SR04 (left/center/right) block *forward* motion under 25 cm
  (turning and reversing still work so you can back away).
- **Soil sensing**: 7-in-1 NPK probe (RS485/Modbus), capacitive moisture,
  DHT22 air temp/humidity, battery voltage.
- **Fertilizer dosing**: pre-soak → actuator extend → micro-dose →
  spring retract, with the drive frozen for the whole sequence.
- **Safety**: latched emergency halt command, low-battery drive inhibit,
  ESP32 overtemp inhibit, relays forced off at boot.
- **Telemetry**: one JSON line per second over USB; the laptop console shows
  it live and can log to CSV.

## Folder layout

```
basic-bot/
├── firmware/               # PlatformIO project (ESP32 DevKit V1)
│   ├── platformio.ini
│   ├── include/
│   │   ├── pins.h          # GPIO map (matches the full rover)
│   │   └── config.h        # all tuning constants
│   └── src/
│       ├── main.cpp        # 2 FreeRTOS tasks: drive @50Hz, sensors @5Hz/1Hz
│       ├── drive.*         # BTS7960 tank drive (LEDC PWM)
│       ├── sensors.*       # moisture, battery, DHT22, HC-SR04, NPK Modbus
│       ├── dosing.*        # relay dosing state machine (spring-return)
│       ├── commands.*      # plain-text serial command protocol
│       ├── telemetry.*     # "TLM {json}" output line
│       └── events.h        # cross-core event bits
└── laptop/
    ├── rover.py            # keyboard teleop + telemetry console + CSV log
    └── requirements.txt    # pyserial
```

## Wiring (subset actually used)

| ESP32 pin | Connects to | Note |
|---|---|---|
| GPIO19 / GPIO21 | BTS7960 #1 RPWM / LPWM (left) | R_EN+L_EN of both drivers → 3.3 V |
| GPIO22 / GPIO23 | BTS7960 #2 RPWM / LPWM (right) | |
| GPIO25 / GPIO18 | HC-SR04 Left TRIG / ECHO | ECHO **via 10k/10k divider** (2.5 V) |
| GPIO32 / GPIO33 | HC-SR04 Center TRIG / ECHO | ECHO **via 10k/10k divider** (2.5 V) |
| GPIO15 / GPIO39 | HC-SR04 Right TRIG / ECHO | GPIO39 input-only; ECHO **via 10k/10k divider** |
| GPIO17 / GPIO16 / GPIO4 | MAX485 DI / RO / DE+RE | NPK probe A/B on the MAX485 |
| GPIO14 | DHT22 data | 10k pull-up to 3.3 V |
| GPIO34 | Moisture AOUT | **power the sensor from 3.3 V, not 5 V** |
| GPIO35 | Battery divider 39k/10k | ~2.57 V at 12.6 V full charge |
| GPIO26 / GPIO13 | Relay Ch1 pump / Ch2 actuator | **10k pull-ups to 3.3 V on both** |
| EN | E-stop button (NC → GND) | hardware kill, independent of software |
| VIN | 5 V from LM2596 buck | via ferrite bead; set buck to **5.00 V first** |

Full electrical detail: [`../docs/circuit-diagram.md`](../docs/circuit-diagram.md).

> ⚠️ The three hardware-damage rules from [`../BUILD.md`](../BUILD.md) apply
> unchanged: buck to 5.00 V **before** connecting the ESP32; moisture sensor on
> **3.3 V**; **10k pull-ups** on the relay pins.

## Flash the firmware

```bash
cd basic-bot/firmware
pio run                 # build
pio run -t upload       # flash the ESP32 over USB
pio device monitor      # optional: watch raw output @115200
```

You should see `BOOT agrirover-basic ready (type HELP)` and a `TLM {...}` line
every second. Relays must stay silent at boot (fail-safe working).

## Drive it from the laptop

```bash
cd basic-bot/laptop
pip install -r requirements.txt
python rover.py                      # auto-detects the port
python rover.py --port COM5 --log field1.csv
```

| Key | Action | Key | Action |
|---|---|---|---|
| `w`/`s` | forward / back (hold) | `x` | **emergency halt** (latched) |
| `a`/`d` | spin left / right (hold) | `r` | resume after halt |
| space | stop motors | `f` | run dosing sequence |
| `+`/`-` | speed up / down | `u` | toggle pump disable |
| `t` | telemetry now | `q` | quit (sends stop) |

## Command protocol (if you script it yourself)

One command per line at 115200 baud; firmware replies `ACK <cmd>` or
`NAK <reason>`:

`FWD` `BACK` `LEFT` `RIGHT` `DRIVE_STOP` `STOP` `RESUME` `SPEED <0-255>`
`SETPWM <l> <r>` `DOSE` `PUMP_DISABLE` `PUMP_ENABLE` `STATUS` `PING` `HELP`

Drive commands expire after **1 s** (`CMD_DEADMAN_MS`) — keep re-sending while
moving. Telemetry arrives as `TLM {json}`, events as `ALERT {json}` /
`EVT ...` lines.

## Calibrate (once assembled)

1. **Moisture**: watch `moist_mv` in the telemetry with the probe in dry air,
   then in water; put those two values into `MOIST_CAL_MV[]` in
   `firmware/src/sensors.cpp`.
2. **Battery**: compare `batt_v` against a multimeter on the pack; adjust
   `VBAT_DIVIDER_RATIO` in `config.h` if your resistors are off-nominal.
3. **NPK register order**: vendor-dependent — if N/P/K look swapped, reorder
   the mapping at the bottom of `readNpk()` in `sensors.cpp` per your
   probe's datasheet.
4. **Dead-man vs key repeat**: if the rover stutters while holding a key,
   raise `CMD_DEADMAN_MS` (your OS key-repeat delay is longer than 1 s) or
   increase your OS key-repeat rate.

## Deliberately left out (comes with the full firmware later)

WiFi/MQTT, the HMAC-authenticated Pi link, GPS/navigation, camera + AI
(weed/disease detection), OTA updates, encoders, OLED/LED interface, LoRa.
When you add the Raspberry Pi, switch to [`../firmware`](../firmware) — the
wiring you did here carries over as-is.
