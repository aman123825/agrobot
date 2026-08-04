# AgriRover — Project Audit & Understanding

**Audited:** 31 Jul 2026 · **Scope:** every file in this folder (build artifacts under `.pio/`, `__pycache__`, `.ruff_cache` excluded from review)

---

## 1. What this project is

**AgriRover** is a low-cost autonomous agricultural rover for Indian smallholder farms, built by a 4-person IIT Bombay team for the **IITB–Groww INV.ENT accelerator (Track A)**.

The pitch in one line: *86% of India's farms are under 2 hectares — too small for ₹7–17 lakh tractors and drones. AgriRover is a ₹27–49k rover that drives crop rows, tests soil on the spot, spots weeds/diseases with AI, and doses each plant individually.*

The folder is **not just a codebase** — it is a combined engineering repo + investor fundraising package. Two distinct bodies of work live side by side:

| Half | Contents |
|---|---|
| **Engineering** | ESP32 firmware, Raspberry Pi AI stack, ROS 2 nodes, hardware docs, CAD, training notebooks, deploy scripts |
| **Business** | 7 PowerPoint decks, 2 deck-generator codebases, team roster, budget sheets |

**Team (from `IDEAS_team_members.csv` + decks):** Hitanshu Kapadiya (chassis/CAD), Vivek Kumar Gupta (electronics, firmware, AI — the repo owner, from a farmer family in Jaunpur UP), Shreyash Wagh (structural integration), Pritish Nandy (dashboard, data, mechanical). The CSV lists only 3; the decks list 4 (Pritish Nandy is missing from the CSV).

---

## 2. System architecture

```
                        ┌──────────────────────────────┐
                        │  Farmer's phone / Telegram   │
                        └──────────────┬───────────────┘
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        │            RASPBERRY PI 4  —  "thinking brain"              │
        │  YOLOv8n weed + obstacle · MobileNetV2 disease (38 class)   │
        │  Coral Edge TPU → CPU TFLite fallback                       │
        │  EKF nav · snake path planner · Streamlit + Flask dashboard │
        │  Pathway stream pipeline · InfluxDB · black-box recorder    │
        └──────────────┬───────────────────────────┬──────────────────┘
                       │ UART (HMAC-signed)        │ MQTT/TLS :8883
                       │ v1|ctr|cmd|hmac           │
        ┌──────────────┴───────────────────────────┴──────────────────┐
        │          ESP32 DevKit V1 (FreeRTOS)  —  "acting brain"      │
        │  Core 1 @50 Hz: driveTask (safety-gated tank drive)         │
        │  Core 0 @5 Hz : sensorTask (NPK/RS485, DHT22, GPS, dosing)  │
        │  EventGroup: EVT_DRIVE_INHIBIT = halt|dosing|obstacle|      │
        │              low-batt|link-lost                             │
        └─────────────────────────────────────────────────────────────┘
                 2× BTS7960 drive · pump + linear actuator dosing
                 7-in-1 NPK probe · HC-SR04 on sweep servo · Neo-6M GPS
```

**The key safety idea:** the acting brain never waits for the thinking brain. If the camera, AI, or link fails, the rover stops. It cannot run away or overdose a plant. This is enforced in hardware (E-stop on ESP32 EN pin), firmware (event-group drive inhibit, relay boot fail-safe), and software (fail-safe stop when ToF distance is unavailable).

---

## 3. Directory map

| Path | Contents | Verdict |
|---|---|---|
| `firmware/` | ESP32 PlatformIO: main, drive, sensors, dosing, comms, secure_link, gps, servo, ota + host-mock unit tests | Complete, no stubs |
| `pi/` | ~70 Python files across ai/, bridge/, control/, nav/, data/, mission/, monitor/, sensors/, pipeline/, web/, dashboard/, alerts/, sim/, tests/ | Complete, 10 test modules |
| `ros2/` | ROS 2 package: `/cmd_vel` → signed serial, MQTT telemetry → ROS topics, AI + mission nodes | Complete |
| `basic-bot/` | **Separate simpler variant** — same BTS7960 drive, but WiFi web-page control from a laptop, servo-based dosing, **unauthenticated** plain-text commands, ESP32-CAM instead of Pi | Standalone "Core tier" build |
| `docs/` | 10 documents; `circuit-diagram.md` (761 lines) is the primary hardware reference; wiring SVG/DOT, mechanical layout, shopping list, field-challenge register | Very thorough |
| `models/` | **All 10 model binaries present** + 3 label files | See §5 |
| `training/` | 4 Colab notebooks (weed, obstacle, disease, dataset-builder) + 4 dataset prep scripts | Complete |
| `deploy/` | mosquitto TLS conf + ACL, `harden_pi.sh` (UFW, watchdog, OverlayFS), cert gen, 4 systemd units incl. model-OTA timer | Production-grade |
| `cad/` | Fusion 360 generator script — builds a to-scale 58-component 4-deck 3D model | Complete |
| `deck/`, `_ppt_build/` | **Two separate** deck-generator codebases (python-pptx) + rendered PNG assets + slide previews | See §6 |
| `.github/workflows/` | CI: Ruff lint + C++ host-mock compile | Present |

---

## 4. Verified: pin map is consistent

`firmware/include/pins.h` is the declared single source of truth. I checked it against ESP32 hardware constraints and the docs:

| Function | GPIO | Check |
|---|---|---|
| Drive L/R RPWM+LPWM | 19, 21, 22, 23 | ✅ no conflicts, LEDC ch 0–3 @1 kHz |
| Ultrasonic trig / echo / servo | 25, 18, 27 | ✅ echo via 2.2k/3.9k divider; servo on separate LEDC timer @50 Hz |
| RS485 DI / RO / DE+RE | 17, 16, 4 | ✅ UART2 |
| Moisture / VBAT / TDS | 34, 35, 36 | ✅ correctly used as **input-only** ADC1 pins |
| DHT22 | 14 | ✅ |
| GPS RX / TX | 39, 15 | ✅ 39 input-only for RX; GPIO15 strapping pin documented as safe (boot-HIGH matches idle UART TX) |
| Relay pump / actuator / dir | 26, 13, 2 | ✅ GPIO2 strapping pin reserved for Branch B only |

**No duplicate assignments. No input-only pin used as an output. No flash pins (6–11) touched.** GPIO32/33 are deliberately freed by the BTS7960 swap.

**Secure link verified end-to-end:** `firmware/src/secure_link.cpp` and `pi/security.py` agree on the envelope `v1|<counter>|<command>|<hmac_hex>` — HMAC-SHA256 truncated to 16 bytes (32 hex chars), strictly-increasing counter persisted in ESP32 NVS and in `~/.agrorover_counter` on the Pi. Constant-time hex comparison, fail-closed on missing key, lockout + tamper alert after repeated bad signatures.

---

## 5. Models: README is out of date (good news)

The root `README.md` §Status says:

> *"The blocking item is model training: `models/` ships no binaries."*

**This is no longer true.** All models were trained and exported on 30–31 Jul 2026:

| File | Size | Date |
|---|---|---|
| `weed_model_quant.tflite` / `_edgetpu.tflite` | 3.2 MB / 3.6 MB | 31 Jul |
| `obstacle_model_quant.tflite` / `_edgetpu.tflite` | 3.2 MB / 3.6 MB | 31 Jul |
| `disease_model_quant.tflite` / `_edgetpu.tflite` / `_float16.tflite` | 3.0 / 3.3 / 5.1 MB | 30 Jul |
| `weed_best.pt`, `obstacle_best.pt` | 6.2 MB each | 31 Jul |

Label files cross-check **correctly** against the Pi inference code and the notebooks:
- `weed_labels.txt` = `crop`, `weed` — and `pi/ai/weed_detection.py` ignores `crop`/`negative`, so only `weed` can trigger a spray ✅
- `obstacle_labels.txt` = 7 classes in the exact ID order the notebook asserts ✅
- `plantvillage_labels.txt` = exactly 38 lines ✅

`models/README.md` is the accurate one (it documents the candidate-filename fallback chain and the OTA manifest workflow). **The root README is the stale file.**

---

## 6. The pitch decks — 7 files, 4 generations

| File | Slides | Size | Date | What it is |
|---|---|---|---|---|
| `AgriRover_Pitch.pptx` | 12 | 0.03 MB | 30 Jun | **Gen 1** — text-only first draft, no images |
| `AgriRover_GrowwxIITB.pptx` | 21 | 1.3 MB | 1 Jul | **Gen 2** — full deck + appendix, few images |
| `Precision-farming-for-every-small-farm (3).pptx` | 15 | 44.5 MB | 2 Jul | **Gen 3** — heavily illustrated redesign |
| `AgriRover_GrowwxIITB_TrackA_v2.pptx` | 16 | 38.5 MB | 4 Jul | **Gen 3b** — same design, resequenced + Thank You |
| `AgriRover_Investor_5Slides.pptx` | 5 | 8.4 MB | 6 Jul | **Gen 4 short** — 5-slide investor cut |
| `AgriRover_Investor_Full.pptx` | 10 | 10.9 MB | **8 Jul** | **Gen 4 full — the newest and strongest deck** |
| `Pitch Deck Template (3).pptx` | 6 | 0.11 MB | 7 Jul | Accelerator's blank template (4:3, not yours) |

**`AgriRover_Investor_Full.pptx` is the current canonical deck.** It is the only one with a named-competitor analysis (XMachines ₹17 L, Marut Drones ₹7–10 L, head-to-head table), a founder-story slide ("Why I'm building this" — Jaunpur), explicit pricing (₹75k own / ₹300 per acre-pass / ₹199 per month), a ₹1.0 lakh ask over 28 weeks, and a full budget sheet.

**Two independent generator codebases exist:** `deck/build_deck.py` and `_ppt_build/` (which contains `build_deck.py`, `build_deck2.py`, `make_pitch_v2/v3/v4.py`, asset builders, and a `verify.py`). `_ppt_build/` is the later iteration. Neither is wired to a single entry point — they are ad-hoc scripts.

---

## 7. Issues found

### Documentation inconsistencies (real, worth fixing)

1. **`BUILD.md` still tells you to wire L298N drivers.** Lines 33, 104, 106 instruct: *"Bond heatsinks to both L298N ICs"*, *"Wire both L298N: IN1=19, IN2=21, IN3=22, IN4=23, ENA=32, ENB=33"*. But `pins.h`, `drive.cpp`, `docs/circuit-diagram.md` §5.1, `docs/wiring-summary-v2.md`, the shopping list and CAD have all moved to **2× BTS7960 (IBT-2)** with RPWM/LPWM on 19/21/22/23 and GPIO32/33 freed. **Anyone following BUILD.md Phase 4 will wire the wrong driver and mis-map the pins.** This is the highest-priority fix.
2. **Root `README.md` line 23** describes drive as "2x L298N tank drive" — same stale reference.
3. **Root `README.md` §Status** claims models are missing (see §5) — now false.
4. **`docs/field-challenges-and-solutions.md`** correctly logs FC-10 as *"Implemented (code) · hardware pending"* — so the intent is clear, BUILD.md just was not updated with it.

### Engineering notes (not bugs, but worth knowing)

5. **ESP32 internal temperature** (`firmware/src/main.cpp:97`, `temperatureRead()`) is uncalibrated on original ESP32 silicon — treat as a relative trend, not an absolute °C reading.
6. **`sensorTask` blocks during the dosing sequence** (~10 s). Motors are safety-inhibited throughout, but telemetry and ultrasonic polling pause during that window.
7. **STOP is fire-and-forget** in `pi/main.py` — there is a PING heartbeat, but no per-command ACK check before the next loop iteration.
8. **`SERIAL_PORT` hardcoded** to `/dev/ttyUSB0` in `pi/config.py` — will pick the wrong device if multiple USB-serial adapters are attached. Prefer a `/dev/serial/by-id/...` path.
9. **Manual Modbus framing** in `sensors.cpp` (no library) — functional and lightweight, but lacks parity/timeout hardening.
10. **NVS counter persistence is throttled to 10 s** — a small replay window exists after an ungraceful power loss. Documented tradeoff to protect flash wear.
11. **Test coverage gaps:** no tests for real hardware I/O (I2C/UART) or for security-counter power-loss recovery.
12. **`pi/ai/camera_calib.py` is a passthrough** until `camera_intrinsics.npz` is generated — expected, not a defect.

### Housekeeping

13. **Not a git repository** — no `.git` directory, despite a `.gitignore`, a CI workflow, and SECURITY.md referencing "the repository". All version history is absent; the only change log is `.workbuddy-ai/memory/2026-07-30.md`.
14. **Duplicate 19.5 KB `deep-research.js`** in both `models/.claude/workflows/` and `training/.claude/workflows/` — stray tooling artifacts unrelated to the project.
15. **`AgriRover_Training_Fixes.zip`** (16 KB) is a redundant transfer bundle of files already present in the folder.
16. **`basic-bot/` uses unauthenticated plain-text commands** over a WiFi AP — fine for its stated private-network scope, but do not deploy it on a shared network.
17. **Build artifacts committed in place:** `.pio/` (vendored Arduino libraries + object files), `__pycache__`, `.ruff_cache`, `.pytest_cache` bloat the folder considerably.

---

## 8. Honest status assessment

| Layer | Status |
|---|---|
| ESP32 firmware | ✅ Complete, builds, no stubs, host-mock tests pass |
| Pi software stack | ✅ Complete — AI, nav, data, dashboard, alerts, simulator |
| ROS 2 layer | ✅ Complete |
| AI models | ✅ **Trained and exported** (weed, obstacle, disease) — 30–31 Jul |
| Hardware design | ✅ Fully specified: 110-part BOM + 15 gap items, verified circuit, CAD |
| Deploy/ops | ✅ TLS MQTT, hardened Pi, systemd, model OTA with rollback |
| **Physical rover** | ❌ **Not built.** Decks say "software validated in simulation; hardware integration is next" |
| **Field validation** | ❌ Not started. All savings figures (30–50%) are *targets to prove*, not measured results |

**Bottom line:** this is a genuinely mature software-and-design project with an unbuilt hardware prototype. The decks are honest about this — they say "hardware fully designed and costed" and frame the ₹1 lakh ask as funding the first physical build plus one season of pilot data. The engineering is well above typical student-project quality, particularly the security model (HMAC + anti-replay + TLS + hardened Pi) and the field-challenge register that tracks 10 real-world failure modes.

**If you fix one thing:** update `BUILD.md` Phase 4 and root `README.md` to BTS7960 before anyone follows the build guide with a soldering iron.
