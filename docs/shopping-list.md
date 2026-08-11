# AgriRover — Priced Purchase Sheet (components × quantity × price)

Complete buy-list: original BOM (110) + 15 gap-audit items + v2 upgrade parts +
tools. Prices are **indicative India-market ranges in ₹** (vary by vendor/time —
verify before ordering). Line total = Qty × unit price range. Software is free.

> *(printed)* = made from PETG filament, not bought separately.
> *(opt)* = optional, not in the core total.

---

## 1. Brain & Compute
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| ESP32 DevKit V1 | 1 | 300–500 | 300–500 |
| ESP32-CAM (OV2640) | 1 | 400–600 | 400–600 |
| Raspberry Pi 5 (8GB) *(primary — Hailo AI HAT+ host)* | 1 | 7,200–8,000 | 7,200–8,000 |
| Raspberry Pi 4 (2GB) *(fallback/prototype — Coral host)* | 1 | 4,500–6,000 | (alt) |
| Pi 5 27W USB-C PSU | 1 | 700–1,200 | 700–1,200 |
| Pi 5 active cooler | 1 | 600–800 | 600–800 |
| 32GB microSD (Pi OS) | 1 | 400–600 | 400–600 |
| 16GB microSD (CAM) | 1 | 200–300 | 200–300 |
| CP2102 USB–serial | 1 | 80–150 | 80–150 |
| **Subtotal** | | | **9,880–11,850** |

## 2. Power
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| 4S LiFePO4 pack *(baseline — FC-02, matches firmware thresholds)* | 1 | 1,500–2,800 | 1,500–2,800 |
| 3S LiPo 2200mAh *(legacy bench-rig alt — needs firmware threshold overrides)* | 1 | 800–1,200 | (alt) |
| LM2596 buck | 1 | 100–200 | 100–200 |
| 10,000mAh power bank | 1 | 600–1,000 | 600–1,000 |
| INA219 | 1 | 100–200 | 100–200 |
| 1000µF 25V cap *(25 V rating for the 14.6 V LiFePO4 bus)* | 2 | 10–20 | 20–40 |
| 1N5819 diode | 4 | 10–20 | 40–80 |
| P6KE20A TVS *(P6KE15A only for the 11.1 V LiPo bench rig — 15 V part conducts on a full 14.6 V LiFePO4 bus)* | 2 | 10–20 | 20–40 |
| XT60 connector pair | 1 | 80–150 | 80–150 |
| Rocker switch 20A | 1 | 30–60 | 30–60 |
| 5W solar panel | 1 | 400–800 | 400–800 |
| TP4056+DW01 | 1 | 80–150 | 80–150 |
| Velcro strap + tray | 2 | 40–60 | 80–120 |
| **Subtotal** | | | **3,050–5,640** |

> **Battery chemistry (FC-02):** the **4S LiFePO4 pack is the baseline** — it
> tolerates 45 °C+ and will not catch fire, and it matches the firmware
> thresholds in `firmware/include/config.h` (14.6 V full / 12.8 V nominal /
> 11.0 V cutoff) and the SoC curve in `pi/sensors/fuel_gauge.py`. The 3S LiPo
> is the *legacy bench-rig alternative* — listed *(alt)*, excluded from the
> running total, and only valid if you also override the battery thresholds and
> the P6KE20A→P6KE15A TVS at build time. Either way, add the **10k pack NTC**
> (section 12) for the thermal guardian and keep the pack shaded/ventilated.

## 3. Motor & Drive
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| 12V DC gear motor | 4 | 200–400 | 800–1,600 |
| 2× BTS7960 (IBT-2) motor driver | 2 | 200–350 | 400–700 |
| Hall wheel encoder | 2 | 100–200 | 200–400 |
| Encoder magnet disc | 2 | 20–50 | 40–100 |
| Rubber wheels 65mm | 4 | 100–200 | 400–800 |
| Motor mounts *(printed)* | 4 | — | 0 |
| **Subtotal** | | | **1,840–3,600** |

## 4. Sensing (ESP32 side)
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| HC-SR04 (front + rear) | 2 | 50–100 | 100–200 |
| SG90 servo (sweep) | 1 | 100–150 | 100–150 |
| Capacitive moisture v1.2 | 1 | 80–150 | 80–150 |
| RS485 NPK 7-in-1 probe | 1 | 2,000–5,000 | 2,000–5,000 |
| MAX485 module | 1 | 60–100 | 60–100 |
| DHT22 | 1 | 150–250 | 150–250 |
| DS18B20 waterproof | 1 | 200–400 | 200–400 |
| TDS meter v1.0 | 1 | 150–300 | 150–300 |
| Rain sensor LM393 | 1 | 50–80 | 50–80 |
| MPU6050 | 1 | 150–250 | 150–250 |
| Neo-6M GPS | 1 | 300–500 | 300–500 |
| VL53L1X ToF | 1 | 400–700 | 400–700 |
| **Subtotal** | | | **3,740–8,080** |

## 5. AI Sensing (Pi side)
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| Pi Camera v2 | 1 | 1,200–1,800 | 1,200–1,800 |
| Wide-angle M12 160° lens | 1 | 300–500 | 300–500 |
| AI HAT+ 26 TOPS (Hailo-8) *(primary — Pi 5 PCIe)* | 1 | 10,000–11,000 | 10,000–11,000 |
| Google Coral USB *(fallback/prototype — Pi 4/5 USB)* | 1 | 3,000–4,500 | (alt) |
| 30cm CSI ribbon | 1 | 100–150 | 100–150 |
| Pi GPIO header | 1 | 80–150 | 80–150 |
| **Subtotal** | | | **11,680–13,600** |

## 6. Actuation & Output
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| 12V linear actuator (150N) | 1 | 600–1,200 | 600–1,200 |
| 12V submersible pump | 1 | 150–300 | 150–300 |
| 2-channel relay module | 1 | 80–150 | 80–150 |
| Peristaltic pump *(opt)* | 1 | 500–1,200 | (opt) |
| 12V 775 grass-cutter motor | 1 | 200–400 | 200–400 |
| SG90 servo (seed sower) | 1 | 100–150 | 100–150 |
| SG90 servo (pan/tilt aimed spray, FC-01) | 2 | 100–150 | 200–300 |
| Misting nozzle + tubing | 1 | 150–300 | 150–300 |
| Water/fertilizer tank 500ml | 1 | 100–200 | 100–200 |
| Float sensor | 1 | 50–80 | 50–80 |
| Silicone tubing 6mm (1m) | 1 | 50–100 | 50–100 |
| PCF8574 expander | 1 | 80–150 | 80–150 |
| DPDT relay *(Branch B actuator only — see note)* | 1 | 60–120 | (cond) |
| **Subtotal** | | | **1,760–3,330** |

> **Open item — actuator retraction (FC-03, code-ready / wiring-pending):**
> Firmware now compiles **both** branches behind `config.h ACTUATOR_DC_REVERSIBLE`
> (default **0** = Branch A). Decide before ordering:
> - **Spring-return actuator (Branch A, default):** the 2-channel relay above is sufficient — **do not** buy the DPDT relay.
> - **DC-reversible actuator (Branch B):** add **1× DPDT relay** (polarity reversal for retract) + **1 control GPIO** (ESP32 **GPIO2** = `PIN_ACTUATOR_DIR`, freed by the BTS7960 swap). See `circuit-diagram.md` §5.2.
>
> **SG90 servo count:** the build now uses **4× SG90** total — 1 ultrasonic
> sweep (§4), 1 seed sower (§6), and **2 new pan/tilt** for the aimed spray
> (§6, FC-01). Buy accordingly.

### Dosing + soil-probe increment (paper §9 / Table 5 audit trail)

The paper quotes the dosing-and-soil increment over the scout configuration as
**₹3,600–8,300 (midpoint ₹5,850)**. That range is the sum of exactly these
line items (from §4 and §6 above, plus the needle head):

| Line item | ₹ range |
|-----------|---------|
| RS485 NPK 7-in-1 probe (§4) | 2,000–5,000 |
| MAX485 module (§4) | 60–100 |
| 12V linear actuator 150N, limit-switch backed (§6) | 600–1,200 |
| Peristaltic pump (§6) | 500–1,200 |
| 2-channel relay module (§6) | 80–150 |
| Water/fertilizer tank 500ml (§6) | 100–200 |
| Float sensor (§6) | 50–80 |
| Silicone tubing 6mm (§6) | 50–100 |
| Needle-injection head (needle, luer fittings, mount) | 160–270 |
| **Increment total** | **3,600–8,300** |

The probe alone (₹2,000–5,000) is the dominant swing item. The needle head is
fabricated from a blunt dosing needle plus luer fittings on a printed mount;
it is priced here and not elsewhere in this list.

## 7. Communication
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| LoRa SX1276 module | 1 | 400–800 | 400–800 |
| 868MHz SMA antenna | 1 | 100–200 | 100–200 |
| **Subtotal** | | | **500–1,000** |

## 8. Interface & Monitoring
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| OLED 0.96" SSD1306 | 1 | 150–250 | 150–250 |
| WS2812B strip (9 LEDs) | 1 | 100–200 | 100–200 |
| Emergency-stop button | 1 | 50–80 | 50–80 |
| Mode selector switch | 1 | 80–150 | 80–150 |
| Directional buttons | 4 | 5–10 | 20–40 |
| SD card module (SPI) | 1 | 80–150 | 80–150 |
| **Subtotal** | | | **480–870** |

## 9. Passive components & wiring
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| 2.2kΩ / 3.9kΩ / 39kΩ / 10kΩ / 4.7kΩ resistors | ~27 | (kit) | 50–100 |
| 100nF ceramic cap | 10 | 2–4 | 20–40 |
| 10µF electrolytic cap | 5 | 4–8 | 20–40 |
| 22AWG silicone wire (3m ×3 colors) | 9m | — | 200–400 |
| 26AWG ribbon cable (1m) | 2 | 40–75 | 80–150 |
| JST-PH 2.0 connectors | 20 pr | 5–10 | 100–200 |
| Screw terminal blocks | 10 | 8–15 | 80–150 |
| PCB / perfboard | 2 | 40–100 | 80–200 |
| Heat-shrink kit | 1 | 80–150 | 80–150 |
| Zip ties | 1 pk | 80–100 | 80–100 |
| **Subtotal** | | | **790–1,530** |

## 10. Chassis & mechanical
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| 4mm acrylic sheet 30×40cm | 2 | 100–200 | 200–400 |
| Aluminum angle extrusion 1m | 1 | 200–400 | 200–400 |
| M3 stainless screw kit | 1 | 80–150 | 80–150 |
| M4 bolt + captive-nut kit | 1 | 80–150 | 80–150 |
| 30mm M3 standoffs | 20 | 4–8 | 80–150 |
| PETG filament 500g | 1 | 500–800 | 500–800 |
| Foam sealing strip 2m | 1 | 80–150 | 80–150 |
| Clear-coat spray | 1 | 150–250 | 150–250 |
| TPU filament (small) *(opt)* | 1 | 400–700 | (opt) |
| Steel blade insert (weeder) | 1 | 50–150 | 50–150 |
| **Subtotal** | | | **1,420–2,600** |

## 11. Safety / Thermal / Reliability (gap-audit)
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| Blade fuse 25–30A + holder | 1 | 30–60 | 30–60 |
| Anti-spark XT60 | 1 | 80–150 | 80–150 |
| Balance charger (iMAX B6 — has both LiFe and LiPo modes) | 1 | 800–1,500 | 800–1,500 |
| BTS7960 thermal pads / spare heatsink (IBT-2 ships with one) | 2 | 20–50 | 40–100 |
| Pi 4 heatsink kit | 1 | 150–300 | 150–300 |
| 30mm 5V fan | 1 | 80–150 | 80–150 |
| Loctite 243 (blue) | 1 | 150–250 | 150–250 |
| Conformal coating spray | 1 | 400–700 | 400–700 |
| Cable glands PG7+PG9 | 8–10 | 10–20 | 100–200 |
| Silicone RTV sealant | 1 | 100–200 | 100–200 |
| Ferrite bead pack | 1 | 30–60 | 30–60 |
| Rubber grommets pack | 1 | 30–60 | 30–60 |
| Nylon trimmer line 10m | 1 | 80–150 | 80–150 |
| Reflective enclosure wrap / sun canopy *(FC-02 thermal)* | 1 | 150–400 | 150–400 |
| **Subtotal** | | | **2,220–4,280** |

> **Note on the "15 gap-audit items":** the original gap-audit list has **13**
> items here. The other two — **4.7kΩ I2C pull-up resistors (G11)** and **100nF
> decoupling caps (G12)** — are bought as part of **Section 9 (Passives &
> wiring)**. 13 here + 2 in Section 9 = the full 15. (The **reflective sun
> canopy** above is a *new* FC-02 thermal addition, not one of the original 15.)

## 12. v2 UPGRADE parts (needed to use the new firmware/software)
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| ADS1115 16-bit I2C ADC | 1 | 150–300 | 150–300 |
| ACS712-30A current sensor *(optional if BTS7960 IS used — FC-10)* | 2 | 100–180 | 200–360 |
| 10kΩ NTC thermistor (battery pack temp — FC-02) | 1 | 20–60 | 20–60 |
| Logic level shifter (3.3↔5V) | 1 | 40–100 | 40–100 |
| TDS calibration solution (1413µS) | 1 | 200–400 | 200–400 |
| pH buffer solution (4.0 & 7.0) | 1 set | 150–350 | 150–350 |
| GPS-RX jumper wire | — | (from wire) | 0 |
| **Subtotal** | | | **760–1,570** |

## 13. Tools & consumables (one-time)
| Item | Qty | Unit ₹ | Line ₹ |
|------|-----|--------|--------|
| Soldering iron (25W+) | 1 | 300–600 | 300–600 |
| Rosin-core solder | 1 | 100–200 | 100–200 |
| Flux pen | 1 | 80–150 | 80–150 |
| Isopropyl alcohol 99% | 1 | 150–250 | 150–250 |
| Digital multimeter | 1 | 300–600 | 300–600 |
| Wire stripper + crimper | 1 | 150–300 | 150–300 |
| Spare blade fuses (5-pack) | 1 | 30–60 | 30–60 |
| Precision screwdriver set | 1 | 150–300 | 150–300 |
| Anti-static mat + strap | 1 | 150–300 | 150–300 |
| **Subtotal** | | | **1,410–2,760** |

## 14. Durability pack — multi-season hardening (see `farmer-needs-and-durability.md`)
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| Industrial pSLC microSD 32GB (Pi boot — replaces consumer card as #1 field-failure fix) | 1 | 800–1,500 | 800–1,500 |
| Gore-type membrane vent (enclosure condensation) | 1 | 100–300 | 100–300 |
| Silica-gel desiccant packs | 4 | 10–25 | 40–100 |
| GX12/M12 aviation screw-lock connector pairs (all inter-enclosure cables) | 8 | 60–150 | 480–1,200 |
| Rubber anti-vibration standoff/grommet kit (Pi + ESP32 mounts) | 1 | 100–250 | 100–250 |
| Field spares kit (spare SD, ESP32 board, 1× BTS7960, pump+nozzle, fuses, connector pigtails) | 1 | 2,500–4,000 | 2,500–4,000 |
| **Subtotal** | | | **4,020–7,350** |

> Already covered elsewhere (do NOT re-buy): conformal coating, cable glands,
> RTV sealant, Loctite 243, heatsinks, grommets — Section 11. Software side of
> durability (read-only rootfs/OverlayFS, tmpfs logs, low-battery clean
> shutdown, health telemetry) is free — see `farmer-needs-and-durability.md` §2.2.

---

## GRAND TOTAL (running budget)

| Section | ₹ range |
|---------|---------|
| 1. Brain & Compute | 9,880–11,850 |
| 2. Power | 3,050–5,640 |
| 3. Motor & Drive | 1,840–3,600 |
| 4. Sensing (ESP32) | 3,740–8,080 |
| 5. AI Sensing (Pi) | 11,680–13,600 |
| 6. Actuation | 1,760–3,330 |
| 7. Communication | 500–1,000 |
| 8. Interface | 480–870 |
| 9. Passives & wiring | 790–1,530 |
| 10. Chassis | 1,420–2,600 |
| 11. Safety/Thermal | 2,220–4,280 |
| 12. v2 Upgrade parts | 760–1,570 |
| 13. Tools | 1,410–2,760 |
| 14. Durability pack | 4,020–7,350 |
| **TOTAL (Full AI build + durability)** | **₹43,550 – 68,060** |

> **Compute (primary vs fallback):** the total uses the **Pi 5 + Hailo-8 AI HAT+**
> primary platform (`docs/accelerator-alternatives.md` Tier B). The **Pi 4** and
> **Coral USB** lines are marked *(alt)* and excluded — they are the working
> prototype/fallback path (swap in, not add on). Choosing the **Hailo-8L 13 TOPS**
> HAT (~₹6,350) instead of the 26-TOPS Hailo-8 trims ~₹4,000.

### Build-tier shortcuts
- **Core only (ITSP demo):** sections 2, 3, 6 (relay dosing), 9 + ESP32 + moisture + NPK ≈ **₹8,700–15,600**
- **Core + Navigation:** add GPS, encoders, INA219, OLED, safety ≈ **₹12,700–21,600**
- **Full AI, Pi 4 + Coral fallback:** everything on the prototype path ≈ **₹28,700–50,600**
- **Full AI, Pi 5 + Hailo primary:** everything on the production path ≈ **₹39,700–62,600**
- **Field-deployable (Pi 5 + Hailo + §14 durability pack):** ≈ **₹43,500–68,000** — the only tier meant to survive 5+ seasons with a farmer

### Optional future upgrades (NOT in total)
| Component | Qty | ₹ | For |
|-----------|-----|---|-----|
| u-blox ZED-F9P RTK + antenna | 1+1 | 17,500–30,000 | cm per-plant GPS |
| NDVI/multispectral camera | 1 | 1,500–55,000 | crop-health imaging |
| RPLIDAR A1 / OAK-D Lite | 1 | 7,000–18,000 | SLAM/mapping |
| Jetson Orin Nano | 1 | 40,000–55,000 | heavier on-board AI |

---

### Notes
- Prices are **indicative** (Indian maker vendors) and not live quotes — verify before ordering. The Coral, Pi 4, and NPK probe are the biggest swing items.
- The **v2 upgrade additions vs. the original BOM**: ADS1115, 2× ACS712 (now
  optional if BTS7960 IS is used), level shifter, TDS solution, pH buffers
  (section 12), plus the field-challenge build-queue parts — **2× BTS7960**
  replacing the L298N pair (FC-10), a **10k pack NTC** + **reflective sun
  canopy** (FC-02), and **2× pan/tilt SG90** for the aimed spray (FC-01).
- Software (FreeRTOS, Pi OS, OpenCV, TFLite, YOLOv8n, Mosquitto, Pathway, Streamlit, etc.) is **free**.
