# AgriRover — Field Challenges & Solutions Register

A running log of **real-world field situations** and the chosen solution for each,
kept in one place. We add a row as each situation is analysed; once the list is
complete we implement the open ones together in a single pass.

**Status key:** ✅ Implemented · 🛠 Proposed (ready to build) · 🔶 Decision pending (a hardware/chemistry choice needed) · 📌 Operational (handled by procedure, not parts)

---

## Index

| ID | Situation | Status |
|----|-----------|--------|
| FC-01 | Weeds grow at a different height than the pathway | 🛠 Proposed |
| FC-02 | High field temperature → thermal burnout / battery fire | 🛠 Proposed + 🔶 battery choice |
| FC-03 | Linear actuator retraction type (spring vs DC) | 🔶 Decision pending |
| FC-04 | Per-plant location precision with Neo-6M | ✅ Implemented (vision tagging) |
| FC-05 | Analog sensors over-volt the ESP32 ADC | ✅ Implemented (3.3V power) |
| FC-06 | Relays twitch ON at boot | ✅ Implemented (pull-ups + fail-safe) |
| FC-07 | Pi/ESP32 comms link drops mid-drive | ✅ Implemented (heartbeat dead-man) |
| FC-08 | Dust, dew, irrigation spray on electronics | ✅ Implemented (sealing + coating) |
| FC-09 | Wheel/cutter jam (stall) | ✅ Implemented (current/stall stop) |

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

**To build:** `aim_nozzle(bbox, img_size, geom, depth) -> (pan_deg, tilt_deg)`,
pan/tilt servo driver (via PCF8574 / PWM), wire into the weed-detection branch.

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

**To build:** `pi/sensors/thermal_guardian.py` (CPU + NTC + ambient logic),
ESP32 chip-temp monitor, mission-scheduler cool-hours window; circuit diagram +
shopping list updates (NTC, pan/tilt servos, sun shade).

---

## Already-resolved situations (recorded for completeness)

### FC-03 — Actuator retraction type 🔶
Spring-return (Branch A) works with the 2-channel relay; DC-reversible (Branch B)
needs a **DPDT relay + 1 GPIO**. Decide before ordering. (shopping-list §6,
circuit §5.2; firmware has a `PIN_ACTUATOR_DIR` placeholder.)

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

---

## Pending build queue (open items to implement together at the end)
1. FC-01 vision-guided aimed spray (pan/tilt + targeting code)
2. FC-02 thermal guardian (firmware + Pi) + cool-hours scheduling
3. FC-02 hardware: pack NTC, sun shade, enclosure; **LiFePO4 vs LiPo decision**
4. FC-03 DPDT relay wiring **once actuator type is confirmed**

> Add new situations above this line as they come up; we will implement the whole
> open queue in one consolidated pass.
