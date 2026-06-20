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
| Raspberry Pi 4 (2GB) | 1 | 4,500–6,000 | 4,500–6,000 |
| 32GB microSD (Pi OS) | 1 | 400–600 | 400–600 |
| 16GB microSD (CAM) | 1 | 200–300 | 200–300 |
| CP2102 USB–serial | 1 | 80–150 | 80–150 |
| **Subtotal** | | | **5,880–8,150** |

## 2. Power
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| 3S LiPo 2200mAh | 1 | 800–1,200 | 800–1,200 |
| LM2596 buck | 1 | 100–200 | 100–200 |
| 10,000mAh power bank | 1 | 600–1,000 | 600–1,000 |
| INA219 | 1 | 100–200 | 100–200 |
| 1000µF 16V cap | 2 | 10–20 | 20–40 |
| 1N5819 diode | 4 | 10–20 | 40–80 |
| P6KE15A TVS | 2 | 10–20 | 20–40 |
| XT60 connector pair | 1 | 80–150 | 80–150 |
| Rocker switch 20A | 1 | 30–60 | 30–60 |
| 5W solar panel | 1 | 400–800 | 400–800 |
| TP4056+DW01 | 1 | 80–150 | 80–150 |
| Velcro strap + tray | 2 | 40–60 | 80–120 |
| **Subtotal** | | | **2,350–4,040** |

## 3. Motor & Drive
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| 12V DC gear motor | 4 | 200–400 | 800–1,600 |
| L298N module | 2 | 150–250 | 300–500 |
| Hall wheel encoder | 2 | 100–200 | 200–400 |
| Encoder magnet disc | 2 | 20–50 | 40–100 |
| Rubber wheels 65mm | 4 | 100–200 | 400–800 |
| Motor mounts *(printed)* | 4 | — | 0 |
| **Subtotal** | | | **1,740–3,400** |

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
| Google Coral USB | 1 | 3,000–4,500 | 3,000–4,500 |
| 30cm CSI ribbon | 1 | 100–150 | 100–150 |
| Pi GPIO header | 1 | 80–150 | 80–150 |
| **Subtotal** | | | **4,680–7,100** |

## 6. Actuation & Output
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| 12V linear actuator (150N) | 1 | 600–1,200 | 600–1,200 |
| 12V submersible pump | 1 | 150–300 | 150–300 |
| 2-channel relay module | 1 | 80–150 | 80–150 |
| Peristaltic pump *(opt)* | 1 | 500–1,200 | (opt) |
| 12V 775 grass-cutter motor | 1 | 200–400 | 200–400 |
| SG90 servo (seed sower) | 1 | 100–150 | 100–150 |
| Misting nozzle + tubing | 1 | 150–300 | 150–300 |
| Water/fertilizer tank 500ml | 1 | 100–200 | 100–200 |
| Float sensor | 1 | 50–80 | 50–80 |
| Silicone tubing 6mm (1m) | 1 | 50–100 | 50–100 |
| PCF8574 expander | 1 | 80–150 | 80–150 |
| **Subtotal** | | | **1,560–3,030** |

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
| LiPo balance charger (iMAX B6) | 1 | 800–1,500 | 800–1,500 |
| L298N heatsink (14×14mm) | 2 | 20–50 | 40–100 |
| Pi 4 heatsink kit | 1 | 150–300 | 150–300 |
| 30mm 5V fan | 1 | 80–150 | 80–150 |
| Loctite 243 (blue) | 1 | 150–250 | 150–250 |
| Conformal coating spray | 1 | 400–700 | 400–700 |
| Cable glands PG7+PG9 | 8–10 | 10–20 | 100–200 |
| Silicone RTV sealant | 1 | 100–200 | 100–200 |
| Ferrite bead pack | 1 | 30–60 | 30–60 |
| Rubber grommets pack | 1 | 30–60 | 30–60 |
| Nylon trimmer line 10m | 1 | 80–150 | 80–150 |
| **Subtotal** | | | **2,070–3,880** |

## 12. v2 UPGRADE parts (needed to use the new firmware/software)
| Component | Qty | Unit ₹ | Line ₹ |
|-----------|-----|--------|--------|
| ADS1115 16-bit I2C ADC | 1 | 150–300 | 150–300 |
| ACS712-30A current sensor | 2 | 100–180 | 200–360 |
| Logic level shifter (3.3↔5V) | 1 | 40–100 | 40–100 |
| TDS calibration solution (1413µS) | 1 | 200–400 | 200–400 |
| pH buffer solution (4.0 & 7.0) | 1 set | 150–350 | 150–350 |
| GPS-RX jumper wire | — | (from wire) | 0 |
| **Subtotal** | | | **740–1,510** |

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

---

## GRAND TOTAL (running budget)

| Section | ₹ range |
|---------|---------|
| 1. Brain & Compute | 5,880–8,150 |
| 2. Power | 2,350–4,040 |
| 3. Motor & Drive | 1,740–3,400 |
| 4. Sensing (ESP32) | 3,740–8,080 |
| 5. AI Sensing (Pi) | 4,680–7,100 |
| 6. Actuation | 1,560–3,030 |
| 7. Communication | 500–1,000 |
| 8. Interface | 480–870 |
| 9. Passives & wiring | 790–1,530 |
| 10. Chassis | 1,420–2,600 |
| 11. Safety/Thermal | 2,070–3,880 |
| 12. v2 Upgrade parts | 740–1,510 |
| 13. Tools | 1,410–2,760 |
| **TOTAL (Full AI build)** | **₹27,360 – 47,950** |

### Build-tier shortcuts
- **Core only (ITSP demo):** sections 2, 3, 6 (relay dosing), 9 + ESP32 + moisture + NPK ≈ **₹8,000–14,000**
- **Core + Navigation:** add GPS, encoders, INA219, OLED, safety ≈ **₹12,000–20,000**
- **Full AI (this sheet):** everything ≈ **₹27,000–48,000**

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
- The **only 5 things new vs. the original BOM**: ADS1115, 2× ACS712, level shifter, TDS solution, pH buffers (section 12).
- Software (FreeRTOS, Pi OS, OpenCV, TFLite, YOLOv8n, Mosquitto, Pathway, Streamlit, etc.) is **free**.
