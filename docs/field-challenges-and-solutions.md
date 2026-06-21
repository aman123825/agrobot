# AgriRover — Field Challenges & Solutions Register

A running log of **real-world field situations** and the chosen solution for each,
kept in one place. We add a row as each situation is analysed; once the list is
complete we implement the open ones together in a single pass.

**Status key:** ✅ Implemented · 🛠 Proposed (ready to build) · 🔶 Decision pending (a hardware/chemistry choice needed) · 📌 Operational (handled by procedure, not parts)

---

## Index

| ID | Situation | Status |
|----|-----------|--------|
| FC-01 | Weeds grow at a different height than the pathway | ✅ Implemented (code) · hardware pending |
| FC-02 | High field temperature → thermal burnout / battery fire | ✅ Implemented (code) · hardware pending · LiFePO4 recommended |
| FC-03 | Linear actuator retraction type (spring vs DC) | ✅ Code-ready (compile flag) · wiring pending |
| FC-04 | Per-plant location precision with Neo-6M | ✅ Implemented (vision tagging) |
| FC-05 | Analog sensors over-volt the ESP32 ADC | ✅ Implemented (3.3V power) |
| FC-06 | Relays twitch ON at boot | ✅ Implemented (pull-ups + fail-safe) |
| FC-07 | Pi/ESP32 comms link drops mid-drive | ✅ Implemented (heartbeat dead-man) |
| FC-08 | Dust, dew, irrigation spray on electronics | ✅ Implemented (sealing + coating) |
| FC-09 | Wheel/cutter jam (stall) | ✅ Implemented (current/stall stop) |
| FC-10 | Motor driver under-spec (L298N) for soil load | ✅ Implemented (code: BTS7960) · hardware pending |

---

## FC-01 — Weeds at a different height than the pathway
**Situation:** The rover drives on the pathway, but weeds grow in the raised beds
at crop height. The grass cutter, V-blade, and misting nozzle are at fixed
heights and cannot reach a weed that is higher/lower than the tool.

**Analysis:** Mechanical cutting from the pathway can only reach **ground-level
weeds in the pathway itself**. Bed weeds at variable height need a tool that
*aims* rather than one fixed in place. The camera + YOLOv8n already know the
weed's position in the frame, so the right fix is **vision-guided aimed spraying**.

**Solution:**
- Hardware: mount the misting nozzle on a **pan/tilt** mount (2× SG90 servos).
  Tilt covers height; pan covers lateral offset.
- Software: convert the weed bounding-box (u,v) + camera geometry + **VL53L1X
  ToF** depth into pan/tilt angles, so the nozzle points exactly at the weed
  regardless of bed height (reuses the plant-tagging geometry).
- Scope note: keep grass cutter + V-blade for **pathway ground weeds only**; use
  the aimed sprayer for **bed weeds at height**. (A vertical lift actuator on the
  cutter is possible but adds weight/cost — avoid unless mechanical removal at
  height is mandatory.)

**Implemented (code) — hardware pending:** `pi/ai/spray_targeting.py`
(`aim_angles(bbox, img_w, img_h, hfov, vfov, depth) -> (pan_deg, tilt_deg)` +
`SprayTargeter`, clamped ±80°); `pi/control/servo_pwm.py` (guarded RPi.GPIO
pan/tilt driver on **GPIO13/19**, added to `pi/config.py`); `pi/main.py` weed
branch now aims the nozzle from the YOLO bbox (+ optional ToF depth) before
firing the mist relay (`WeedDetector.detect_best`). **Pending:** physically
mount the 2× SG90 pan/tilt and wire GPIO13/19 (circuit §3, §10.1).

---

## FC-02 — High field temperature → thermal burnout / battery fire
**Situation:** Indian field summers reach **40–45°C ambient**; a sealed
enclosure in sun can hit **60–70°C inside**. Risk of the rover overheating,
throttling, or — worst case — the battery igniting.

**Analysis (risk ranked):**
- 🔴 **LiPo = fire hazard.** At 45°C+ in sun a LiPo can swell/vent/ignite, and
  charging a hot pack is dangerous. The current design does **not** monitor pack
  temperature — the most serious gap.
- 🟠 **Raspberry Pi 4** throttles at ~80°C; heatsink + 30mm fan are marginal in a
  hot sealed box under Coral + inference load.
- 🟠 **L298N drivers** already run 80–90°C and will thermal-shutdown in heat.

**Solution:**
- 🔶 **Battery:** strongly consider **LiFePO4 instead of LiPo** for hot climates
  (tolerates heat, does not catch fire). If staying on LiPo: mount it **shaded +
  ventilated**, never in direct sun.
- Hardware: **10kΩ NTC thermistor on the battery pack → ADS1115 A2** (free
  channel); **reflective/white enclosure + sun canopy**; larger/second fan with a
  **dust-filtered intake**; raise enclosure off the hot soil.
- Software — **thermal guardian:**
  - ESP32 reads chip temp → reduce motor PWM, then halt if too hot.
  - Pi reads CPU temp (`/sys/class/thermal`) + pack NTC (ADS1115) + ambient
    (DHT22). Thresholds: CPU >75°C drop inference fps · >80°C pause+alert ·
    **pack >55°C STOP + disable charging + critical alert · >65°C safe shutdown.**
- 📌 Operational: **cool-hours-only** mission mode (auto-run early morning /
  evening; refuse to start in peak heat).

**Implemented (code) — hardware pending:** `pi/sensors/thermal_guardian.py`
(`ntc_temp_c` beta model, `evaluate(cpu, pack, ambient)` with CPU>75 throttle /
>80 pause, pack>55 STOP+no-charge / >65 shutdown; guarded CPU sysfs + ADS1115
**A2** NTC reads). ESP32 firmware reads the die temp (`temperatureRead()`),
asserts `EVT_OVERTEMP` >85 °C / clears <80 °C (`config.h ESP32_OVERTEMP_C`),
publishing one alert. `pi/main.py` runs the guardian ~1 Hz → pack-critical sends
STOP + black-box log + Telegram alert. Cool-hours gating via
`mission/scheduler.py within_operating_window()`. **Pending hardware:** 10k pack
NTC → ADS1115 A2, reflective enclosure / sun canopy, second/larger fan;
**LiFePO4 strongly recommended** over LiPo for hot climates (shopping §2).

---

## Already-resolved situations (recorded for completeness)

### FC-03 — Actuator retraction type ✅ code-ready / 🔶 wiring pending
Spring-return (Branch A) works with the 2-channel relay; DC-reversible (Branch B)
needs a **DPDT relay + 1 GPIO**. **Both branches now compile** behind
`config.h ACTUATOR_DC_REVERSIBLE` (default **0** = Branch A). When set to 1,
`dosing.cpp` drives `PIN_ACTUATOR_DIR` (**ESP32 GPIO2**, freed by the BTS7960
swap) to reverse polarity for the retract phase. **Decide actuator type before
ordering** the DPDT relay (shopping-list §6, circuit §5.2).

### FC-04 — Per-plant precision with Neo-6M ✅
Neo-6M is ~1 m. Solved with SBAS/GAGAN + stationary averaging + EKF + **vision
plant geo-tagging** (~10–20 cm relative). RTK is the optional hardware path to cm.

### FC-05 — Analog sensor over-voltage ✅
Moisture + TDS powered from **3.3V** (5V output could exceed the ESP32 ADC max).

### FC-06 — Relay boot twitch ✅
**10kΩ pull-ups on GPIO13/26** + firmware forces relays OFF first thing at boot.

### FC-07 — Comms link loss ✅
**Heartbeat dead-man:** ESP32 halts the drive if no authenticated command arrives
within the timeout; Pi sends periodic `PING`.

### FC-08 — Dust / dew / spray ✅
Conformal-coated PCBs, **cable glands + RTV** at enclosure entries, foam-gasket
lid, grommets on chassis pass-throughs.

### FC-09 — Wheel / cutter jam ✅
**ADS1115 + ACS712** current sensing detects a stall → STOP + alert before a motor
burns.

### FC-10 — Motor driver under-spec for soil load ✅ Implemented (code) / hardware pending
**Situation:** The L298N (2 A/channel, 2–4 V drop, BJT) drives 2 soil-loaded
gear motors per channel — it crowds its current limit, wastes torque/runtime to
heat, and thermal-shuts-down in a hot field (feeds FC-02).

**Analysis:** Motors draw ~1.5–2.5 A each at stall; paired per channel exceeds
the L298N. MOSFET drivers (low Rds(on), low drop) are the fix.

**Solution (recommended):** **2× BTS7960 / IBT-2** (one per side, ~43 A peak,
~₹250 each). Low drop = more torque + runtime; thermal headroom solves the
field-heat shutdown. **Bonus:** its current-sense (IS) output can feed the
**ADS1115**, potentially **replacing the 2× ACS712** (FC-09).
- Alt premium: **2× Cytron MD10C** (~30 A, PWM+DIR, fewest pins, robotics-grade).
- Avoid **DRV8871** here (3.6 A too low for paired soil-loaded motors).

**Implemented (code) — hardware pending:** `drive.cpp` `applySide()` rewritten
for BTS7960 dual-PWM (fwd=RPWM, rev=LPWM, stop=both 0); `pins.h` remapped
(LEFT RPWM19/LPWM21, RIGHT RPWM22/LPWM23, 4 LEDC channels, R_EN/L_EN→3.3V,
GPIO32/33 freed); public drive API unchanged so `main.cpp`/`comms.cpp` compile
untouched. `pi/sensors/current_monitor.py` gains an optional BTS7960 **IS**
current source (`use_bts7960_is`, `bts7960_is_amps`) keeping ACS712 as default.
Circuit §5.1 + shopping §3 updated. **Pending:** swap in the 2× BTS7960 boards
and (optionally) route IS → ADS1115 to drop the ACS712s.

---

## Pending build queue (status after the consolidated implementation pass)
1. ✅ FC-01 vision-guided aimed spray — **code done** (`spray_targeting.py`,
   `servo_pwm.py`, `main.py` weed branch). Hardware: mount 2× SG90 pan/tilt on
   GPIO13/19.
2. ✅ FC-02 thermal guardian — **code done** (firmware `EVT_OVERTEMP` +
   `thermal_guardian.py` + `main.py` ~1 Hz loop + cool-hours window).
3. 🔶 FC-02 hardware: pack NTC (ADS1115 A2), sun canopy, enclosure; **LiFePO4
   recommended over LiPo** (documented; not yet purchased/installed).
4. ✅ FC-03 actuator Branch B — **code-ready** behind `ACTUATOR_DC_REVERSIBLE`
   (default off). Wire the DPDT relay + GPIO2 once actuator type is confirmed.
5. ✅ FC-10 motor-driver swap to **BTS7960** — **code done** (`drive.cpp`,
   `pins.h`, optional IS→ADS1115). Hardware: fit the 2× BTS7960 boards.

> Remaining work is **physical assembly/wiring**, not code. Add new situations
> above this line as they come up.
