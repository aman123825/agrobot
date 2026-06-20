# AgriRover — Complete Shopping List (with quantities)

Everything needed to build the Full AI tier rover: original BOM (110) + the 15
gap-audit items + the v2 upgrade parts. Software (Layer 12) is free. Prices are
in [`upgrade pricing` / the original BOM]; this list is component + quantity.

> Legend: **Qty** = how many to buy. Items marked *(printed)* come from the PETG
> filament, not bought separately. *(kit)* = sold as an assortment.

---

## 1. Brain & Compute
| # | Component | Qty |
|---|-----------|-----|
| 1 | ESP32 DevKit V1 (38-pin, WROOM-32) | 1 |
| 2 | ESP32-CAM (OV2640) | 1 |
| 3 | Raspberry Pi 4 Model B (2GB) | 1 |
| 4 | 32GB microSD (Class 10, A1) — Pi OS | 1 |
| 5 | 16GB microSD (Class 10) — ESP32-CAM | 1 |
| 6 | CP2102 USB–Serial adapter | 1 |

## 2. Power
| # | Component | Qty |
|---|-----------|-----|
| 7 | 11.1V 3S LiPo 2200mAh (XT60) | 1 |
| 8 | LM2596 buck converter | 1 |
| 9 | 10,000mAh USB power bank (5V/3A) | 1 |
| 10 | INA219 current/voltage sensor | 1 |
| 11 | 1000µF 16V electrolytic cap | 2 |
| 12 | 1N5819 Schottky diode (motor flyback) | 4 |
| 13 | P6KE15A TVS diode | 2 |
| 14 | XT60 connector pair | 1 pair |
| 15 | Main rocker switch (20A) | 1 |
| 16 | 5W solar panel (6V) | 1 |
| 17 | TP4056 + DW01 LiPo charger module | 1 |
| 18 | Velcro strap + battery tray | 2 |

## 3. Motor & Drive
| # | Component | Qty |
|---|-----------|-----|
| 19 | 12V DC gear motor (150–300 RPM, metal gearbox) | 4 |
| 20 | L298N dual H-bridge module | 2 |
| 21 | Hall-effect wheel encoder | 2 |
| 22 | Encoder magnet disc (20-pole) | 2 |
| 23 | Rubber wheels (65mm, D-bore) | 4 |
| 24 | Motor mounts | 4 *(printed)* |

## 4. Sensing (ESP32 side)
| # | Component | Qty |
|---|-----------|-----|
| 25 | HC-SR04 ultrasonic (front) | 1 |
| 26 | HC-SR04 ultrasonic (rear) | 1 |
| 27 | SG90 micro servo (ultrasonic sweep) | 1 |
| 28 | Capacitive soil moisture sensor v1.2 | 1 |
| 29 | RS485 NPK 7-in-1 soil probe | 1 |
| 30 | MAX485 TTL↔RS485 module | 1 |
| 31 | DHT22 temp/humidity | 1 |
| 32 | DS18B20 waterproof temp probe | 1 |
| 33 | TDS meter sensor v1.0 | 1 |
| 34 | Rain sensor module (LM393) | 1 |
| 35 | MPU6050 IMU | 1 |
| 36 | Neo-6M GPS module | 1 |
| 37 | VL53L1X ToF distance sensor | 1 |

## 5. AI Sensing (Pi side)
| # | Component | Qty |
|---|-----------|-----|
| 38 | Raspberry Pi Camera Module v2 | 1 |
| 39 | Wide-angle M12 lens (160°) | 1 |
| 40 | Google Coral USB Accelerator | 1 |
| 41 | 30cm CSI ribbon cable | 1 |
| 42 | Pi GPIO extension header (stacking) | 1 |

## 6. Actuation & Output
| # | Component | Qty |
|---|-----------|-----|
| 43 | 12V micro linear actuator (150N, limit switches) | 1 |
| 44 | 12V mini submersible pump | 1 |
| 45 | 2-channel 5V relay module (opto-isolated) | 1 |
| 46 | Peristaltic pump (optional upgrade to #44) | 1 (opt) |
| 47 | 12V 775 high-RPM motor (grass cutter) | 1 |
| 48 | SG90 micro servo (seed sower) | 1 |
| 49 | Misting nozzle + 1m PU tubing | 1 |
| 50 | Water/fertilizer tank (500ml HDPE) | 1 |
| 51 | Float sensor (tank level, NC) | 1 |
| 52 | Silicone tubing (6mm ID, food-safe) | 1m |
| 53 | PCF8574 I2C GPIO expander | 1 |

## 7. Communication
| # | Component | Qty |
|---|-----------|-----|
| 54 | LoRa SX1276 module (433/868MHz) | 1 |
| 55 | 868MHz SMA antenna (3dBi) | 1 |

## 8. Interface & Monitoring
| # | Component | Qty |
|---|-----------|-----|
| 56 | OLED 0.96" SSD1306 (I2C) | 1 |
| 57 | WS2812B RGB strip (9 LEDs / ~0.15m) | 1 |
| 58 | Emergency-stop button (40mm latching, NC) | 1 |
| 59 | Mode selector switch (3-position rotary) | 1 |
| 60 | Tactile directional buttons (6mm) | 4 |
| 61 | SD card module (SPI) | 1 |

## 9. Passive components & wiring
| # | Component | Qty |
|---|-----------|-----|
| 62 | 2.2kΩ resistor (1/4W 1%) | 5 |
| 63 | 3.9kΩ resistor | 5 |
| 64 | 39kΩ resistor | 2 |
| 65 | 10kΩ resistor (dividers + relay/button pull-ups) | 10 |
| 66 | 4.7kΩ resistor (I2C + DS18B20 pull-ups) | 5 |
| 67 | 100nF ceramic cap (per-IC decoupling) | 10 |
| 68 | 10µF electrolytic cap | 5 |
| 69 | 22AWG silicone wire (red/black/yellow) | 3m each |
| 70 | 26AWG ribbon cable (1m) | 2 |
| 71 | JST-PH 2.0 connectors (assorted) | 20 pairs |
| 72 | Screw terminal blocks (5.08mm) | 10 |
| 73 | PCB / perfboard (7×9cm) | 2 |
| 74 | Heat-shrink tubing assortment | 1 *(kit)* |
| 75 | Zip ties (100/200mm) | 1 pack |

## 10. Chassis & mechanical
| # | Component | Qty |
|---|-----------|-----|
| 76 | 4mm clear acrylic sheet (30×40cm) | 2 |
| 77 | Aluminum angle extrusion (20×20mm, 1m) | 1 |
| 78 | M3 stainless screws + nuts | 1 *(kit)* |
| 79 | M4 bolts + T-slot captive nuts | 1 *(kit)* |
| 80 | 30mm M3 standoffs (M-F) | 20 |
| 81 | PETG filament (1.75mm, 500g) | 1 |
| 82 | Foam weather-sealing strip (2m) | 1 roll |
| 83 | Clear-coat spray (UV-resistant) | 1 can |
| 84 | TPU filament (camera bumper) — small qty | 1 (opt) |
| 85 | Steel blade insert (weeder V-blade) | 1 |

> 3D-printed parts (grass-cutter housing, seed funnel, weeder bracket, NPK mount,
> camera housing, enclosure lid, motor mounts) are printed from #81 PETG.

## 11. Safety / Thermal / Reliability (gap-audit items)
| # | Component | Qty |
|---|-----------|-----|
| 86 | Blade fuse 25–30A + inline holder | 1 |
| 87 | Anti-spark XT60 connector (or 10Ω 5W pre-charge resistor) | 1 |
| 88 | LiPo balance charger (iMAX B6 or equiv.) | 1 |
| 89 | L298N heatsink (14×14mm, thermal tape) | 2 |
| 90 | Raspberry Pi 4 aluminum heatsink kit | 1 |
| 91 | 30mm 5V DC fan | 1 |
| 92 | Loctite 243 (blue) threadlock | 1 |
| 93 | Conformal coating spray | 1 |
| 94 | Cable glands PG7 + PG9 (IP68) | 8–10 |
| 95 | Silicone RTV sealant (clear) | 1 |
| 96 | Ferrite bead (clip/inline) | 1 pack |
| 97 | Rubber grommets (8mm) | 1 pack (20) |
| 98 | Nylon trimmer line (2.0–2.4mm, 10m) | 1 |

## 12. v2 UPGRADE parts (required to use the new firmware/software)
| # | Component | Qty |
|---|-----------|-----|
| 99 | ADS1115 16-bit I2C ADC module | 1 |
| 100 | ACS712-30A current sensor module | 2 |
| 101 | Logic level shifter (3.3↔5V, for WS2812B data) | 1 |
| 102 | TDS calibration solution (1413 µS/cm) | 1 |
| 103 | pH buffer solution (4.0 & 7.0) | 1 set |
| — | GPS-RX jumper wire (ESP32 GPIO15 → Neo-6M RX) | from #69 |

## 13. Tools & consumables (one-time)
| # | Item | Qty |
|---|------|-----|
| 104 | Soldering iron (25W+, fine tip) | 1 |
| 105 | Rosin-core solder (60/40, 0.8mm) | 1 |
| 106 | Flux pen (no-clean) | 1 |
| 107 | Isopropyl alcohol 99% (IPA) | 1 |
| 108 | Digital multimeter | 1 |
| 109 | Wire stripper + crimping tool | 1 |
| 110 | Spare blade fuses (25A, 5-pack) | 1 |
| 111 | Precision screwdriver set | 1 |
| 112 | Anti-static mat + wrist strap | 1 |

## 14. Optional future upgrades (NOT required)
| Component | Qty | For |
|-----------|-----|-----|
| u-blox ZED-F9P RTK board + multi-band antenna | 1 + 1 | cm-level per-plant positioning |
| NDVI/multispectral camera (NoIR+filter or MAPIR) | 1 | crop-health imaging |
| RPLIDAR A1 / OAK-D Lite | 1 | mapping / SLAM |
| Jetson Orin Nano | 1 | heavier on-board AI |

---

### Software (Layer 12) — ₹0
FreeRTOS, PlatformIO, Raspberry Pi OS, Python, OpenCV, TFLite, YOLOv8n, PyCoral,
Mosquitto, Pathway, Streamlit, Node-RED, Telegram, PySerial, paho-mqtt,
TinyGPS++, Google Colab — all free/open-source.
