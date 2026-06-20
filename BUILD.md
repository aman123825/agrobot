# AgriRover — Complete Build Guide (Start to Finish)

This is the full, ordered procedure to build the rover from a pile of parts to a
working field robot. Do the phases **in order** — several steps protect the
hardware and only work if earlier steps are done.

**Companion docs:**
- Wiring detail & pin maps → [`docs/circuit-diagram.md`](docs/circuit-diagram.md)
- Security setup → [`SECURITY.md`](SECURITY.md)
- Firmware notes → [`firmware/test/README.md`](firmware/test/README.md)

> ⚠️ **Three things that prevent hardware damage — never skip them** (details in
> their phases): (1) set the buck converter to 5.00 V *before* connecting the
> ESP32; (2) power the moisture + TDS sensors from **3.3 V, not 5 V**; (3) add
> **10 kΩ pull-ups** on the relay pins (GPIO13/26).

---

## Phase 0 — Plan & gather (before you touch anything)

- [ ] Read [`docs/circuit-diagram.md`](docs/circuit-diagram.md) end to end once.
- [ ] Decide your **build tier** (Core / Core+Navigation / Full AI) from the BOM.
- [ ] Procure all components for that tier (the BOM lists every part, qty, cost).
- [ ] Confirm the **linear actuator type**: spring-return (Branch A) or DC
      reversible (Branch B). Branch B needs one DPDT relay + one freed GPIO
      (circuit §5.2). This affects your wiring.
- [ ] Gather tools: soldering iron + 60/40 solder + flux, **digital multimeter**
      (non-negotiable), wire stripper/crimper, precision screwdrivers, heat-shrink,
      hot-air or lighter, zip ties, calipers, a LiPo balance charger (iMAX B6).
- [ ] Buy consumables from the gap audit: blade fuse + holder, anti-spark XT60,
      L298N + Pi heatsinks, 30 mm fan, Loctite 243, conformal coat, cable glands,
      grommets, ferrite bead, nylon trimmer line.

---

## Phase 1 — Bench prep & component test (before assembly)

Test each module on the bench so you never debug a bad part inside the chassis.

- [ ] Charge the 3S LiPo on the **balance charger** to storage (~11.4 V). Inspect
      for swelling — discard if puffy.
- [ ] Power each module individually from a bench supply / known-good 5 V and
      confirm it responds (servos sweep, OLED lights, relays click).
- [ ] Flash the **ESP32 "blink"** sketch to confirm the board + USB cable work.
- [ ] Boot the **Raspberry Pi** once from a freshly imaged card (Phase 7) to
      confirm it's healthy.
- [ ] Label every wire/connector as you go. Future-you will thank you.

---

## Phase 2 — Mechanical assembly (chassis & drive)

- [ ] Laser-cut / prepare the two acrylic chassis layers; deburr edges.
- [ ] Mount the **aluminum angle extrusion** perimeter frame (absorbs actuator
      reaction force — acrylic alone cracks).
- [ ] Bolt the 4 motor mounts; install the 4 gear motors. Apply **Loctite 243
      (blue)** to every motor-mount screw.
- [ ] Press the encoder magnet discs onto the two rear axles; mount the Hall
      encoders facing them.
- [ ] Fit the 4 wheels. Check the chassis rolls straight and square.
- [ ] Install the slide-and-lock rails (front + rear) and the NPK probe angle
      mount (45°, ±2°).
- [ ] Insert **rubber grommets** in every acrylic hole a wire will pass through.
- [ ] Mount standoffs for the electronics layer.

---

## Phase 3 — Power system (wire this FIRST, test before logic)

Follow the order in circuit-diagram **§1** and **§7**. Build the protected
battery bus before anything else.

- [ ] Wire LiPo **(+)** → **blade fuse (25–30 A)** → **anti-spark XT60** →
      **rocker switch** → 11.1 V main bus (screw terminals).
- [ ] Establish the **common ground star point** at the LiPo (−).
- [ ] Connect the **LM2596 buck** input to the bus. With the buck **disconnected
      from all logic**, power on and **adjust output to exactly 5.00 V with the
      multimeter.** Only then wire the 5 V logic rail.
- [ ] Add bus protection: **P6KE15A TVS** across the 11.1 V bus; **1000 µF caps**
      across the 5 V rail; **ferrite bead** in series with the ESP32 VIN feed.
- [ ] Wire the **battery sense divider** (39 kΩ/10 kΩ) → ESP32 GPIO35. Confirm
      ~2.57 V at full charge with the meter (must be < 3.3 V).
- [ ] Power the **Raspberry Pi from its own 10,000 mAh power bank** — NEVER from
      the buck rail (ripple causes Pi undervoltage throttling).
- [ ] (Optional) Wire solar → TP4056 → LiPo trickle charge.

**Checkpoint:** main bus reads ~11–12.6 V; logic rail reads exactly 5.00 V;
everything else still disconnected.

---

## Phase 4 — Controllers, drive & protection

- [ ] Bond **14×14 mm heatsinks** to both L298N ICs; **heatsink kit + 30 mm fan**
      on the Pi.
- [ ] Wire both L298N per circuit **§2 / §5.1**: IN1=19, IN2=21, IN3=22, IN4=23,
      ENA=32, ENB=33. Drive 12 V from the bus; ENA/ENB to the PWM pins (not
      jumpered high).
- [ ] Add a **1N5819 flyback diode** across every motor terminal.
- [ ] Feed ESP32 **VIN from 5 V via the ferrite bead**; tie grounds to the star
      point.
- [ ] Wire the encoders to **Pi GPIO17 (left) / GPIO27 (right)**.

---

## Phase 5 — Sensors, actuation & interface wiring

Wire strictly to the pin tables in circuit **§2–§6**. Key safety points:

- [ ] **HC-SR04 front:** TRIG=GPIO25; ECHO through the **2.2k/3.9k divider** →
      GPIO18 (never feed raw 5 V echo to the pin).
- [ ] **Moisture + TDS sensors:** power from **3.3 V** (their analog output can
      exceed 3.3 V if run at 5 V and destroy the ADC pin). → GPIO34 / GPIO36.
- [ ] **NPK probe** via MAX485: DI=17, RO=16, DE/RE=4.
- [ ] **DHT22**=GPIO14 (10k pull-up); **GPS**=GPIO39 (RX only); **servo**=GPIO27.
- [ ] **Relays:** pump=GPIO26, actuator=GPIO13. Add a **10 kΩ pull-up to 3.3 V on
      each** so they stay OFF during boot (firmware also forces them off, but the
      pull-up covers the boot window).
- [ ] **I2C bus (Pi):** INA219, MPU6050, VL53L1X, OLED, PCF8574 — add external
      **4.7 kΩ pull-ups** on SDA/SCL.
- [ ] **PCF8574 (Pi):** grass cutter (P0), misting (P1), seed servo (P2), rear
      ultrasonic (P3/P4).
- [ ] **WS2812B → Pi GPIO18** (DMA-capable; level-shift 3.3→5 V).
- [ ] **E-stop** wired to the ESP32 **EN** pin (NC → GND).
- [ ] Mount DS18B20 (Pi GPIO24, 4.7k pull-up), float sensor (GPIO25), rain sensor
      (GPIO26), buttons (GPIO5/6/12/16), mode selector (GPIO20/21).
- [ ] **Branch B actuators only:** wire the DPDT direction relay + its control
      line now (see circuit §5.2) and update `pins.h`.

---

## Phase 6 — Pre-power-on electrical checks (do not skip)

With the **rocker switch OFF**:
- [ ] Continuity-check every ground back to the star point.
- [ ] Check for shorts between 5 V and GND, and 12 V and GND (should read open).
- [ ] Verify the fuse is seated and rated 25–30 A.
- [ ] Confirm relay pull-ups present; confirm moisture/TDS are on 3.3 V.

Then power on with **no firmware loaded**:
- [ ] Confirm 5.00 V rail and ~2.57 V battery-sense tap.
- [ ] Nothing should get hot. Power off if anything does.

---

## Phase 7 — Raspberry Pi OS setup

- [ ] Flash **Raspberry Pi OS Lite (64-bit, Bookworm)** to the 32 GB card.
- [ ] Enable SSH, set hostname, configure WiFi (or do headless via imager).
- [ ] First boot, then:
  ```bash
  sudo apt update && sudo apt -y full-upgrade
  sudo raspi-config         # enable I2C, SPI, Serial (login shell OFF, hw ON), Camera
  ```
- [ ] Enable OneWire for DS18B20: add `dtoverlay=w1-gpio` to `/boot/firmware/config.txt`.
- [ ] Reboot.

---

## Phase 8 — Security keys & secrets (do before flashing)

Full rationale in [`SECURITY.md`](SECURITY.md).

- [ ] Generate the shared command-link key **once**:
  ```bash
  openssl rand -hex 32
  ```
- [ ] Firmware: `cp firmware/include/secrets.example.h firmware/include/secrets.h`
      and fill in WiFi, MQTT user/pass, and `COMMAND_HMAC_KEY` = the key above.
- [ ] Pi: `cp pi/.env.example pi/.env`, fill in, set `AGRO_LINK_KEY` = the **same**
      key, then `chmod 600 pi/.env`.
- [ ] `secrets.h` and `.env` are gitignored — never commit them.

---

## Phase 9 — Flash the ESP32 firmware

```bash
cd firmware
python -m platformio run            # build (needs internet on first run)
python -m platformio run -t upload  # flash the ESP32
python -m platformio device monitor # watch boot logs @115200
```
- [ ] Confirm a clean build (you already saw `[SUCCESS]`) and that it boots
      without resets (good power = no brownout).
- [ ] You should see relays stay **OFF** at boot (fail-safe working).

---

## Phase 10 — Install Pi services

```bash
cd ~/agrobot/pi
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
set -a; source .env; set +a          # load secrets into the environment
```

Set up the **MQTT broker** (auth + TLS) per [`SECURITY.md`](SECURITY.md) and
`deploy/mosquitto.conf`:
```bash
sudo apt -y install mosquitto mosquitto-clients
sudo mosquitto_passwd -c /etc/mosquitto/passwd agrorover
sudo cp deploy/mosquitto.conf /etc/mosquitto/conf.d/agrorover.conf
sudo cp deploy/acl /etc/mosquitto/acl
# generate TLS certs into /etc/mosquitto/certs, then:
sudo systemctl restart mosquitto
```

Harden the Pi:
```bash
sudo deploy/harden_pi.sh
```

---

## Phase 11 — AI models (Full AI tier only)

- [ ] Train on Google Colab (free T4) using PlantVillage + DeepWeeds (see
      [`training/README.md`](training/README.md)).
- [ ] Export `.tflite` (+ Edge-TPU compiled variant for Coral) and `.pt` files.
- [ ] Copy them into `pi/models/` with the names referenced in
      [`models/README.md`](models/README.md).
- [ ] Without models, detection degrades gracefully (the orchestrator logs
      "no backend" and simply doesn't trigger stop/spray).

---

## Phase 12 — Bring-up testing (incremental — wheels OFF the ground)

Test one subsystem at a time. **Put the rover on a stand so wheels spin free.**

1. [ ] **Telemetry:** subscribe and confirm data flows:
   ```bash
   mosquitto_sub -h localhost -u agrorover -P <pass> -t 'rover/#' -v
   ```
   You should see `rover/npk`, `rover/gps`, `rover/status` JSON.
2. [ ] **Authenticated commands:** from the Pi, send a signed command and confirm
   the ESP32 monitor prints `ACK FWD`:
   ```bash
   cd pi && source .venv/bin/activate && set -a; source .env; set +a
   python3 -c "import sys;sys.path.append('.');from bridge.serial_bridge import SerialBridge as S;b=S();b.open();b.send('FWD');print(b.read_line())"
   ```
   Send an unsigned/garbage line manually → ESP32 must reply `NAK auth`.
3. [ ] **Drive:** `FWD/BACK/LEFT/RIGHT/DRIVE_STOP` move the wheels correctly. Fix
   any reversed motor by swapping its two output wires.
4. [ ] **E-stop:** press it — all motion stops instantly.
5. [ ] **Obstacle:** wave a hand in front of the HC-SR04 → rover halts (EVT_OBSTACLE).
6. [ ] **Dosing:** send `DOSE` → pump pre-soak, actuator extends, doses, retracts,
   and the **drive stays frozen** the whole time.
7. [ ] **Vision (Full AI):** `python pi/main.py --max-frames 50 --verbose` and
   confirm obstacle/weed logging.
8. [ ] **Dashboard:** `streamlit run pi/dashboard/app.py` and check metrics/map.

---

## Phase 13 — Calibration

- [ ] **Buck:** re-confirm 5.00 V under load.
- [ ] **Moisture:** read raw ADC in dry air and in water; set `MOIST_RAW_DRY` /
      `MOIST_RAW_WET` in `firmware/include/config.h`.
- [ ] **Battery %:** compare GPIO35 reading to the meter; trim the map if needed.
- [ ] **NPK:** verify the register order matches your probe's datasheet; adjust
      the mapping in `sensors.cpp` if values look swapped.
- [ ] **Servo sweep / seed timing:** confirm the SG90 centers and sweeps; tune
      seed-drop offset against measured wheel velocity.

---

## Phase 14 — Weatherproofing & final mechanical

- [ ] Apply **conformal coating** to all PCBs (avoid connectors & SD slots).
- [ ] Install **cable glands + RTV** at every enclosure pass-through.
- [ ] Foam-seal the enclosure lid; clear-coat the acrylic.
- [ ] Loctite 243 on all remaining M3/M4 after final alignment.
- [ ] Wind **nylon trimmer line** onto the grass-cutter hub; fit the safety shield.
- [ ] Secure the LiPo with the Velcro strap as actuator-side ballast.

---

## Phase 15 — Field operation

- [ ] Charge the LiPo on the balance charger; inspect before every outing.
- [ ] Power on with the rocker switch; confirm OLED + status LED.
- [ ] Select mode (AUTO / MANUAL / SCAN) on the rotary switch.
- [ ] Keep the rover on its own isolated WiFi VLAN/SSID.
- [ ] Watch battery %; the rover auto-flags low battery (return-to-base) below
      9.9 V.
- [ ] First reach for the **E-stop** if anything goes wrong.

---

## Phase 16 — Maintenance

- [ ] After every 2–3 sessions: replace trimmer line, check fasteners (vibration),
      inspect tubing.
- [ ] Periodically: re-balance-charge the LiPo, clean sensors, re-check 5.00 V,
      rotate `AGRO_LINK_KEY` + MQTT credentials (SECURITY.md).
- [ ] Store the LiPo at ~3.8 V/cell; never store fully charged or fully drained.

---

## Production hardening (recommended once stable)

- [ ] Enable ESP32 **Flash Encryption + Secure Boot v2** (SECURITY.md) so firmware
      and the link key can't be extracted from the chip.
- [ ] Run Pi services as a non-root user via systemd units that auto-start on boot.
- [ ] Enable read-only root on the Pi so a stolen SD card yields no writable secrets.

---

## Quick troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| ESP32 random resets | brownout / motor noise | check 5.00 V under load, ferrite bead, flyback diodes, 1000 µF caps |
| Relay clicks at power-on | floating relay pin at boot | add 10 kΩ pull-ups on GPIO13/26 |
| ADC pin dead / garbage | sensor run at 5 V into 3.3 V pin | power moisture/TDS from 3.3 V or divide AOUT |
| `NAK auth` on every command | key mismatch | `COMMAND_HMAC_KEY` (firmware) must equal `AGRO_LINK_KEY` (Pi) |
| No telemetry in dashboard | MQTT auth / broker down | check `mosquitto` service, credentials, TLS CA path |
| Pi throttling / slow inference | overheating | confirm heatsinks + 30 mm fan; check enclosure airflow |
| LED strip dark | wrong Pi pin | WS2812B must be on GPIO18 (DMA), with level shifter |
| NPK reads invalid | RS485 wiring / register order | check A/B + DE/RE timing; verify register map vs datasheet |
