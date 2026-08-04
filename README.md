# AgriRover

Production-intent agricultural scouting rover with a dual-controller
architecture:

- **ESP32 DevKit V1** (FreeRTOS) — real-time drive, sensing, dosing, MQTT.
- **Raspberry Pi 5 + Hailo-8 AI HAT+ (26 TOPS)** — prototype AI inference,
  evidence capture, stream processing and dashboard. A Pi 4 + Coral USB Edge
  TPU is the documented fallback path.

The current commercial hypothesis is a tomato crop-protection service in the
Narayangaon/Junnar cluster: repeatable sentinel samples and trap images,
triggered close-row scans, agronomist-reviewed action, treatment/PHI records and
outcome verification. The first pilot keeps pesticide application manual and
does not use the low-cost NPK probe to prescribe fertilizer.

See [`research/AGRIROVER_MARKET_ADOPTION_RESEARCH.md`](research/AGRIROVER_MARKET_ADOPTION_RESEARCH.md)
for the evidence, economics, partner shortlist and pilot gates.

## Key Features

- **Prototype inference pipelines** — obstacle, weed and leaf-disease model
  paths for Hailo, Coral and CPU. Launch-critical tomato classes still require
  local field data and held-out per-class validation.
- **Close-range evidence capture** — geotagged images, active-learning capture,
  plant history and map/report infrastructure for repeatable scouting.
- **Experimental spray and NPK subsystems** — present for supervised bench and
  research tests only; neither farmer savings nor fertilizer prescriptions are
  established.
- **Layered stop logic** — ToF proximity, obstacle inference, IMU tilt,
  heartbeat watchdog and motor-stall detection. These are design controls, not
  a field-safety certification.
- **Coarse mapping and odometry** — GPS, wheel encoders and IMU support field
  geotags; camera-based row following and boundary tests remain field gates.
- **Two-way Telegram control** — `/stop` `/go` `/status` `/photo` from any phone.
- **Traceable records** — evidence, treatment and field-history data; any rupee
  saving must come from calibrated product quantities and farmer invoices.
- **ISOXML export prototype** — a future interoperability path, not a validated
  tractor-terminal integration.
- **Model OTA updates** — the rover gets smarter every season.
- **Active-learning frame capture** — auto-collects hard cases to improve the models.
- **HMAC-authenticated, encrypted command link** between the Pi and the ESP32.
- **Thermal guardian** — monitors CPU, battery, and ambient temperature.
- **Automated software tests** covering AI interfaces, navigation, data and
  stop logic; these do not establish physical field performance.

## Repository layout

```
agrobot/
├── docs/                      # Circuit, wiring, BOM, upgrades, field notes (see Documentation)
├── firmware/                  # ESP32 (PlatformIO / Arduino + FreeRTOS)
│   ├── platformio.ini
│   ├── include/
│   │   ├── pins.h             # Verified ESP32 pin map (source of truth)
│   │   └── config.h           # Network, MQTT, Modbus, dosing timing
│   └── src/
│       ├── main.cpp           # Dual-core task setup + EventGroup signaling
│       ├── drive.*            # 2x BTS7960 (IBT-2) tank drive (LEDC PWM)
│       ├── sensors.*          # NPK/RS485, DHT22, moisture, TDS, GPS, battery
│       ├── dosing.*           # Sequential pump + actuator state machine
│       ├── secure_link.*      # HMAC-authenticated command link
│       └── comms.*            # WiFi/MQTT + UART command link to the Pi
├── pi/                        # Raspberry Pi services (Python)
│   ├── requirements.txt
│   ├── config.py              # BCM pin map + I2C addresses + endpoints
│   ├── main.py                # Service orchestrator
│   ├── ai/                    # obstacle / weed / disease inference (Hailo / Edge TPU)
│   │   ├── hailo_backend.py   # Pi 5 + Hailo-8 AI HAT+ inference (primary)
│   │   ├── yolo_tflite.py     # Coral / CPU TFLite inference (fallback)
│   │   ├── frame_capture.py   # Active-learning frame capture
│   │   ├── benchmark.py       # On-device inference benchmark
│   │   ├── model_ota.py       # Over-the-air model updates
│   │   └── spray_targeting.py # Pan/tilt nozzle aiming
│   ├── control/               # encoders, imu, servo_pwm, velocity_pid
│   ├── nav/                   # ekf (pose fusion), path_planner, geo
│   ├── sensors/               # tof (VL53L1X), thermal_guardian, current_monitor, fuel_gauge
│   ├── data/                  # isoxml (ISO 11783), savings, plant_db, prescription_map
│   ├── monitor/               # health (field telemetry)
│   ├── bridge/                # serial (PySerial) + MQTT (paho) bridges
│   ├── pipeline/              # Pathway real-time stream processing
│   ├── alerts/                # Telegram two-way control + push alerts
│   ├── dashboard/             # Streamlit UI
│   ├── sim/                   # Rover + sensor simulation (no hardware needed)
│   └── tests/                 # Automated test suite (pytest)
├── ros2/                      # ROS 2 package (sensor / drive / AI / mission nodes)
├── deploy/                    # systemd services, mosquitto, TLS certs, Pi hardening
├── models/                    # Trained model files (see models/README.md)
└── training/                  # 3 Colab notebooks + dataset builder (see training/README.md)
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

**Run tests**
```bash
python -m pytest pi/tests
```

## Documentation

- **[`BUILD.md`](BUILD.md)** — complete start-to-finish build guide (parts → assembly → wiring → flashing → calibration → field operation → maintenance).
- **[`docs/circuit-diagram.md`](docs/circuit-diagram.md)** — full electrical design: power distribution, both pin maps, every bus, the dosing sequence, the hardware-safety review, and a coverage matrix for all 110 BOM components + 15 gap items.
- **[`docs/bts7960-drive-schematic.svg`](docs/bts7960-drive-schematic.svg)** — professional pin-level drive schematic for the **2× BTS7960 (IBT-2)** (every RPWM/LPWM/R_EN/L_EN/VCC/GND/B±/M± terminal). Open in a browser.
- **[`docs/wiring-summary-v2.md`](docs/wiring-summary-v2.md)** — one-page consolidated v2 wiring (single Mermaid graph + complete connection table) reflecting all upgrades; use this to redraw the circuit.
- **[`docs/wiring-v2.svg`](docs/wiring-v2.svg)** — rendered block schematic (open in a browser). **[`docs/wiring-v2.dot`](docs/wiring-v2.dot)** — Graphviz source (`dot -Tpng wiring-v2.dot -o out.png`).
- **[`docs/UPGRADES.md`](docs/UPGRADES.md)** — full fixes/upgrades/advancements roadmap (models, edge hardware, RTK, sensing, MLOps, priorities).
- **[`docs/farmer-needs-and-durability.md`](docs/farmer-needs-and-durability.md)** — Indian farmer needs vs. what the rover serves, plus the durability/ruggedization plan (ICAR trials, market research, IIT-B pathway).
- **[`docs/accelerator-alternatives.md`](docs/accelerator-alternatives.md)** — AI-accelerator options beyond the Coral USB Edge TPU, with an accuracy-headroom analysis and India-market pricing/benchmarks.
- **[`docs/hardware-upgrades-groww.md`](docs/hardware-upgrades-groww.md)** — researched hardware-upgrade roadmap (IIT-B × Groww Track A, ₹50,000 budget), priced and integrated into the codebase.
- **[`docs/BOM-top20-groww-trackA.md`](docs/BOM-top20-groww-trackA.md)** — top-20 bill of materials for the IIT-B × Groww Track A submission.
- **[`docs/shopping-list.md`](docs/shopping-list.md)** — priced purchase sheet: full buy-list (110 BOM + 15 gap items + v2 upgrades + tools) with indicative India-market ₹ ranges.
- **[`deploy/README.md`](deploy/README.md)** — end-to-end Raspberry Pi deployment: MQTT TLS + auth, resilient systemd services, hardware watchdog, and SD-card protection.
- **[`SECURITY.md`](SECURITY.md)** — threat model and hardening (authenticated command link, MQTT TLS, secrets, ESP32 secure boot).
- **[`docs/field-challenges-and-solutions.md`](docs/field-challenges-and-solutions.md)** — running register of real-world field situations (weed height, heat/burnout, etc.) and the chosen solution + status for each.

## Hardware

The complete electrical design — power distribution, both pin maps, every bus,
the dosing sequence, and a coverage matrix accounting for all 110 BOM components
plus 15 gap-audit items — lives in [`docs/circuit-diagram.md`](docs/circuit-diagram.md).

## Status

**Production-intent prototype under construction.** The repository includes
software, firmware, CAD, wiring, BOMs, simulation and model artifacts. It does
not yet contain AgriRover field evidence for crop accuracy, productive
acres/day, reliability, chemical reduction, yield protection, willingness to
pay or payback.

Before a paid launch, the project must complete supervised physical traversal,
local tomato data collection, calibrated measurements and a 12-grower paired
pilot with KVK/agronomist review. The Hailo export path, row navigation,
sentinel/trap workflow, ruggedness and service economics remain validation work.
