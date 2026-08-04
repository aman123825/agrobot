# AgriRover — Hardware Bring-Up & Calibration Checklist

This is the path from *"the code compiles and the logic passes"* to *"the rover
behaves correctly on real hardware."* Software checks (below) are necessary but
**not sufficient** — every item in §2–§9 must be verified on the physical rover,
because correctness depends on wiring, calibration, power, and mechanics that no
code review can confirm.

Work top-to-bottom. **Keep the wheels off the ground and an e-stop within reach
until §9.** Tick each box only after you have *observed* the expected result.

---

## 0. Software verification status (dev machine)

Re-run these after any code change; all currently pass except lint (style-only).

| Check | Command | Result |
|---|---|---|
| Basic DevKit firmware builds | `cd basic-bot/firmware && pio run` | ✅ Flash 23.7% |
| Camera firmware builds | `cd basic-bot/camera && pio run` | ✅ Flash 26.3% |
| Advanced firmware builds | `cd firmware && pio run` | ✅ Flash 64.3% (placeholder secrets) |
| Firmware host tests | `g++ -std=gnu++17 -I test/mocks -I include -I src src/sensors.cpp src/gps.cpp test/test_modbus.cpp -o t && ./t` | ✅ Modbus CRC + GPS robust-mean |
| C++ syntax check (9 files) | `clang++/g++ -fsyntax-only … src/*.cpp` | ✅ all pass |
| Python + ROS2 compile | `python -m compileall pi ros2` | ✅ pass |
| Import smoke test | `cd pi && python -c "from sim.rover_model import RoverSim; …"` | ✅ Import OK |
| Rover simulator | `cd pi && python sim/run_sim.py --steps 10 --verbose` | ✅ ACKs cmds, telemetry, obstacle response |
| Notebooks well-formed | CI JSON check | ✅ 12/12/13 cells |
| Ruff lint | `python -m ruff check pi ros2` | ⚠️ 113 style issues (65 auto-fix) — non-functional |

> Lint note: results depend on the `ruff` version; the flagged items (import
> order, blind-except, empty `TYPE_CHECKING` block) are style, not bugs. Run
> `python -m ruff check --fix pi ros2` if you want them cleaned.

---

## 1. Before you power anything — the three damage rules

From `BUILD.md`, non-negotiable:

- [ ] **Set the LM2596 buck to 5.00 V with NO load** (multimeter on the output),
      *then* connect the ESP32/servo/sensors. Over-voltage kills the ESP32.
- [ ] **Power the capacitive moisture sensor from 3.3 V**, not 5 V.
- [ ] **Pull resistors on the boot-critical pins**: 10 k pull-**up** to 3.3 V on
      the pump relay (GPIO26); 10 k pull-**down** to GND on the servo signal
      (GPIO13) so it idles quiet until driven.
- [ ] Wheels off the ground; probe clear of soil; e-stop (EN→GND) wired and tested.

---

## 2. Power distribution

- [ ] 3S LiPo charged; pack voltage 11.1–12.6 V measured at the connector.
- [ ] Buck output confirmed 5.00 V under a small load.
- [ ] All grounds common (ESP32, BTS7960 logic gnd, servo, sensors, buck).
- [ ] Current headroom: motors + MG995 (stall ~1–2.5 A) + Pi/CAM within the
      buck/battery budget. A brown-out during a servo stall or WiFi TX is the
      most common "it resets randomly" cause.

---

## 3. ESP32 DevKit — flash & boot sanity (basic-bot)

- [ ] `cd basic-bot/firmware && pio run -t upload`
- [ ] Serial @115200 shows `BOOT agrirover-basic ready (type HELP)`.
- [ ] A `TLM {…}` line arrives ~1 Hz.
- [ ] **Relays stay silent at boot** (fail-safe working).
- [ ] `[TLM] … state` reads `OK` (not `LOW_BATT`/`OVERTEMP`/`HALT`).

---

## 4. Drive subsystem (2× BTS7960) — WHEELS OFF GROUND

- [ ] `cd basic-bot/laptop && python rover.py` connects; telemetry streams.
- [ ] Hold **W** → both sides forward; **S** → reverse; **A/D** → spin. Correct
      any reversed side by swapping that side's RPWM/LPWM pair (`pins.h`).
- [ ] Release key → motors stop within ~1 s (dead-man).
- [ ] Space / **STOP** button stops immediately.
- [ ] Trip a front ultrasonic (<25 cm) → forward is blocked, reverse/turn still
      work (`state` shows `OBSTACLE`).

---

## 5. Insertion servo (MG995) — calibrate before soil

File: `basic-bot/firmware/include/config.h`

- [ ] Servo powered from **5 V rail**, common ground, pull-down on GPIO13.
- [ ] Set `SERVO_INSERT_UP_DEG` so the probe is fully clear of the ground.
- [ ] Set `SERVO_INSERT_DOWN_DEG` so the probe seats without straining the servo
      or lifting the chassis. Approach in small steps; watch for stall/heat.
- [ ] `DOSE` (key **F**): pre-soak → probe lowers → dwell → micro-dose → probe
      raises, with the **drive frozen** the whole time.
- [ ] No brown-out/reset during the servo sweep (if so, see §2 current headroom).

---

## 6. Sensor calibration — values you MUST measure on your hardware

| Sensor | Constant / function | File | How |
|---|---|---|---|
| Soil moisture | `MOIST_CAL_MV[]` | `basic-bot/firmware/src/sensors.cpp` | Note `moist_mv` in dry air and in water; put both in the curve |
| Battery voltage | `VBAT_DIVIDER_RATIO` | `basic-bot/firmware/include/config.h` | Compare `batt_v` to a multimeter; adjust ratio |
| NPK N/P/K order | mapping at end of `readNpk()` | `sensors.cpp` | Vendor-dependent register order; reorder per datasheet |
| Ultrasonics ×3 | `US_STOP_DISTANCE_CM` | `config.h` | Confirm `dist_l/c/r` read true distances; set stop threshold |
| DHT22 | — | — | Sanity-check air temp/RH against a reference |
| **(Adv.)** BTS7960 current | `BTS7960_IS_SENS_V_PER_A = 0.066  # placeholder` | `pi/sensors/current_monitor.py` | Calibrate to your IS sense resistor with a known load |
| **(Adv.)** Thermal NTC | divider assumption in header | `pi/sensors/thermal_guardian.py` | Verify Vcc–Rseries–NTC–GND wiring + beta/R25 |
| **(Adv.)** Fuel gauge | OCV→SoC curve | `pi/sensors/fuel_gauge.py` | Check against pack voltage at known charge points |

---

## 7. Camera (ESP32-CAM)

- [ ] `cd basic-bot/camera && pio run -t upload` (FTDI adapter, IO0→GND to flash).
- [ ] **Change `CAM_AP_PASS`** in `src/main.cpp` before field use.
- [ ] Join WiFi `AgriRover-CAM`; stream loads at `http://192.168.4.1/`.
- [ ] In `rover.py`, **c** / the **Camera** button opens the stream.

---

## 8. Advanced bot — Raspberry Pi + full firmware

This tier needs secrets, models, and the Pi stack before it does anything useful.

**Secrets (must match!)**
- [ ] `firmware/include/secrets.h` created from `secrets.example.h`: real WiFi,
      MQTT, and a 32+ byte `COMMAND_HMAC_KEY` (`openssl rand -hex 32`).
- [ ] `pi/.env` created from `.env.example`; **`AGRO_LINK_KEY` == firmware
      `COMMAND_HMAC_KEY`** exactly, or every command is rejected.
- [ ] MQTT creds set; TLS certs in place if `MQTT_TLS=1`.

**AI models (gitignored — supply them)**
- [ ] Drop into `models/`: `yolov8n_obstacle.tflite`,
      `plantvillage_mobilenetv2.tflite`, `deepweeds_yolov8n.tflite`.
- [ ] `pip install -r pi/requirements.txt` (+ `pycoral` if using the Coral TPU).
- [ ] On startup, detectors log a real backend — **not** "no backend; detect()
      returns …". If you see that, the model/lib is missing and AI is a no-op.

**Bring-up order**
- [ ] Local Mosquitto broker running on the Pi.
- [ ] `python pi/sim/run_sim.py` passes (logic OK) — set `AGRO_LINK_KEY` first.
- [ ] `cd firmware && pio run -t upload` (with secrets.h present).
- [ ] Serial bridge (`pi/bridge/serial_bridge.py`) links Pi↔ESP32; ACKs seen.
- [ ] Dashboard (`streamlit run pi/dashboard/app.py`) shows live telemetry.
- [ ] (Optional) Telegram alerts if `TELEGRAM_TOKEN`/`CHAT_ID` set.

> Reminder: root `README.md` marks this tier a **scaffold** — expect to flesh
> out and field-tune modules, not flash-and-go.

---

## 9. Integrated field trial (graduate slowly)

- [ ] First drive at low `SPEED`, wheels on ground, open area, e-stop in hand.
- [ ] Verify obstacle STOP live (walk in front at speed).
- [ ] Run one full `DOSE` cycle over real soil only after §5 angles are confirmed.
- [ ] Confirm low-battery cutoff and thermal inhibit trip at safe thresholds.
- [ ] Only then run an autonomous mission/route.

---

## 10. Sign-off

| Subsystem | Verified by | Date | Notes |
|---|---|---|---|
| Power (5.00 V, grounds) | | | |
| Drive (all directions, dead-man) | | | |
| Insertion servo (UP/DOWN angles) | | | |
| Moisture / battery / NPK / ultrasonic cal | | | |
| Camera stream | | | |
| Pi link (HMAC), MQTT, models loaded | | | |
| Field trial (obstacle, dose, cutoffs) | | | |

*Compiling and passing the sim/tests (§0) does not certify physical operation.
This checklist does — one observed tick at a time.*
