# AgriRover — Basic Bot (Step 1, no AI)

Self-contained code for the **Core-tier build**: the ESP32 DevKit handles drive,
sensing, safety, and a private WiFi mobile-control page without a Raspberry Pi,
Coral, MQTT, or router. You can operate it from a **phone over WiFi** or retain
the **laptop USB serial** console. An AI-Thinker **ESP32-CAM** supplies live video
on the same rover WiFi network (see `camera/`).

Everything that runs on this bot lives in this folder. The pin map is the same
as the full firmware (`../firmware`), so nothing gets rewired when you upgrade.

## What it does

- **Tank drive** via 2× BTS7960 (hold a key on the laptop to drive; a dead-man
  timer stops the motors the moment you release it or the cable drops).
- **Obstacle guard**: 3× HC-SR04 (left/center/right) block *forward* motion under 25 cm
  (turning and reversing still work so you can back away).
- **Soil sensing**: 7-in-1 NPK probe (RS485/Modbus), capacitive moisture,
  DHT22 air temp/humidity, battery voltage.
- **Fertilizer dosing**: pre-soak → MG995 servo lowers the probe → micro-dose →
  servo raises the probe, with the drive frozen for the whole sequence.
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
│       ├── dosing.*        # dosing state machine (MG995 servo insertion)
│       ├── commands.*      # plain-text serial command protocol
│       ├── telemetry.*     # "TLM {json}" output line
│       └── events.h        # cross-core event bits
├── laptop/
│   ├── rover.py            # keyboard teleop + telemetry console + CSV log
│   └── requirements.txt    # pyserial
└── camera/                 # optional ESP32-CAM MJPEG video (separate board)
    ├── platformio.ini
    └── src/main.cpp
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
| GPIO26 | Relay Ch1 pump | **10k pull-up to 3.3 V** |
| GPIO13 | MG995 insertion servo signal | servo on **5 V** rail, common ground |
| Hardware E-stop | NC latching switch in actuator power feed | physically cuts motor/pump power; do not wire NC directly from EN to GND |
| VIN | 5 V from LM2596 buck | via ferrite bead; set buck to **5.00 V first** |

Complete circuit guide: [`docs/circuit-connections.md`](docs/circuit-connections.md).  
Visual wiring overview: [`docs/circuit-connections.svg`](docs/circuit-connections.svg).

> ⚠️ Set the buck to 5.00 V **before** connecting either ESP32; power the
> moisture sensor from **3.3 V**; use a **10k pull-up** on the active-low relay
> input; and use a real latching hardware E-stop in the actuator power feed.

## Flash the firmware

```bash
cd basic-bot/firmware
pio run                 # build
pio run -t upload       # flash the ESP32 over USB
pio device monitor      # optional: watch raw output @115200
```

You should see `BOOT agrirover-basic ready (type HELP)` and a `TLM {...}` line
every second. Relays must stay silent at boot (fail-safe working).

## Control it from a phone

1. Flash both `firmware/` and `camera/`, then power the DevKit and camera.
2. Join WiFi **`AgriRover-Control`** using password **`agrirover123`**.
3. Ignore the phone's no-internet warning and stay connected.
4. Open **http://192.168.4.1/**.

The page provides press-and-hold drive controls, emergency halt/resume, speed,
dosing, pump control, all telemetry, safety banners, and the live camera feed.
No mobile app installation or router is required. Full setup and troubleshooting:
[`docs/mobile-control.md`](docs/mobile-control.md).

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
| `c` | open camera stream | | |

## Camera (optional ESP32-CAM)

An AI-Thinker **ESP32-CAM** joins the DevKit's `AgriRover-Control` network at
**192.168.4.2** and streams live MJPEG into the phone controller. You can also
press **`c`** in the laptop console or open **http://192.168.4.2/** directly.
Details in [`camera/README.md`](camera/README.md).

## Command protocol (if you script it yourself)

One command per line at 115200 baud; firmware replies `ACK <cmd>` or
`NAK <reason>`:

`FWD` `BACK` `LEFT` `RIGHT` `DRIVE_STOP` `STOP` `RESUME` `SPEED <0-255>`
`SETPWM <l> <r>` `DOSE` `PUMP_DISABLE` `PUMP_ENABLE` `STATUS` `PING` `HELP`

Drive commands expire after **1 s** (`CMD_DEADMAN_MS`) — keep re-sending while
moving. Telemetry arrives as `TLM {json}`, events as `ALERT {json}` /
`EVT ...` lines.

## Calibrate (once assembled)

**Quick path:** run `python laptop/calibrate.py` — it reads live telemetry and
prints the exact `MOIST_CAL_MV[]` and `VBAT_DIVIDER_RATIO` values to paste
(steps 1–2 below, automated). Manual reference:

1. **Moisture**: watch `moist_mv` in the telemetry with the probe in dry air,
   then in water; put those two values into `MOIST_CAL_MV[]` in
   `firmware/src/sensors.cpp`.
2. **Battery**: compare `batt_v` against a multimeter on the pack; adjust
   `VBAT_DIVIDER_RATIO` in `config.h` if your resistors are off-nominal.
3. **NPK register order**: vendor-dependent — if N/P/K look swapped, reorder
   the mapping at the bottom of `readNpk()` in `sensors.cpp` per your
   probe's datasheet.
4. **Drive stutter**: the console now drives on key press/release (not OS key
   auto-repeat), so holding a key should be smooth. If it still stutters,
   check the USB link/port rather than raising `CMD_DEADMAN_MS`.

## Poster

A one-page A4 ITSP poster for **this** build (no AI, no Pi) lives at
[`../poster/basic-bot-poster.html`](../poster/basic-bot-poster.html). Rebuild the
PDF and PNG proof with:

```bash
npm i puppeteer-core
npx @puppeteer/browsers install chrome-headless-shell@stable
CHROME=<path to chrome-headless-shell> \
POSTER_FILE=basic-bot-poster.html POSTER_OUT=AgriRover_BasicBot_Poster \
  node poster/build-poster.mjs
```

The script prints a fit check and fails visibly if the content ever spills past
one A4 sheet. Omit the two `POSTER_*` variables to rebuild the full-rover poster.

## Deliberately left out (comes with the full firmware later)

WiFi/MQTT, the HMAC-authenticated Pi link, GPS/navigation, on-board AI
(weed/disease detection), OTA updates, encoders, OLED/LED interface, LoRa.
When you add the Raspberry Pi, switch to [`../firmware`](../firmware) — the
wiring you did here carries over as-is.
