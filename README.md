# AgriRover

Autonomous agricultural rover with a dual-controller architecture:

- **ESP32 DevKit V1** (FreeRTOS) — real-time drive, sensing, dosing, MQTT.
- **Raspberry Pi 4** — AI inference (YOLOv8n obstacle/weed + disease classification on a Coral Edge TPU), stream processing, and the dashboard.

The rover performs soil sensing (7-in-1 NPK probe), targeted liquid fertilizer micro-dosing, snake-routing navigation with GPS logging, and modular field attachments (grass cutter, seed sower, weeder, sprayer).

## Repository layout

```
agrobot/
├── docs/
│   └── circuit-diagram.md     # Full verified circuit & wiring reference + BOM coverage
├── firmware/                  # ESP32 (PlatformIO / Arduino + FreeRTOS)
│   ├── platformio.ini
│   ├── include/
│   │   ├── pins.h             # Verified ESP32 pin map (source of truth)
│   │   └── config.h           # Network, MQTT, Modbus, dosing timing
│   └── src/
│       ├── main.cpp           # Dual-core task setup + EventGroup signaling
│       ├── drive.*            # 2x L298N tank drive (LEDC PWM)
│       ├── sensors.*          # NPK/RS485, DHT22, moisture, TDS, GPS, battery
│       ├── dosing.*           # Sequential pump + actuator state machine
│       └── comms.*            # WiFi/MQTT + UART command link to the Pi
├── pi/                        # Raspberry Pi services (Python)
│   ├── requirements.txt
│   ├── config.py              # BCM pin map + I2C addresses + endpoints
│   ├── ai/                    # obstacle / disease / weed models
│   ├── bridge/                # serial (PySerial) + MQTT (paho) bridges
│   ├── pipeline/              # Pathway real-time stream processing
│   ├── dashboard/             # Streamlit UI
│   └── alerts/                # Telegram push alerts
├── models/                    # Trained model files (see models/README.md)
└── training/                  # Colab training notebooks (see training/README.md)
```

## Getting started

**ESP32 firmware**
```bash
cd firmware
pio run                 # build
pio run -t upload       # flash (set WiFi/MQTT via build_flags or secrets.h)
```

**Raspberry Pi services**
```bash
cd pi
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard/app.py
```

## Documentation

- **[`BUILD.md`](BUILD.md)** — complete start-to-finish build guide (parts → assembly → wiring → flashing → calibration → field operation → maintenance).
- **[`docs/circuit-diagram.md`](docs/circuit-diagram.md)** — full electrical design: power distribution, both pin maps, every bus, the dosing sequence, the hardware-safety review, and a coverage matrix for all 110 BOM components + 15 gap items.
- **[`docs/wiring-summary-v2.md`](docs/wiring-summary-v2.md)** — one-page consolidated v2 wiring (single Mermaid graph + complete connection table) reflecting all upgrades; use this to redraw the circuit.
- **[`SECURITY.md`](SECURITY.md)** — threat model and hardening (authenticated command link, MQTT TLS, secrets, ESP32 secure boot).

## Hardware

The complete electrical design — power distribution, both pin maps, every bus,
the dosing sequence, and a coverage matrix accounting for all 110 BOM components
plus 15 gap-audit items — lives in [`docs/circuit-diagram.md`](docs/circuit-diagram.md).

## Open item

Linear actuator retraction type (spring-return vs DC reversible) determines the
final relay wiring and the retract branch in `firmware/src/dosing.cpp`. See
circuit diagram §5.2.

## Status

Scaffold with working structure and skeleton implementations. Modules marked
`TODO` / `NotImplementedError` are stubs ready to be fleshed out.
