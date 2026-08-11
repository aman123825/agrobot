# AgriRover - Mechanical Layout (to scale)

**Chassis:** double-decker, **320 mm (width) x 450 mm (length)** deck plates,
inter-deck height **~60-70 mm** (stacked M3 standoffs). Front = drive/camera direction.
Coordinates are **mm from the chassis front-left corner**; sizes are real part footprints.

> Visual: [`chassis-layout.svg`](chassis-layout.svg) - to-scale top view of all four decks.

## Why double-decker
- Fluid (tank/pumps) sits **below** electronics so leaks drain away.
- Battery-bus motor wiring + BTS7960 heat kept on the lower deck, away from Pi/I2C/camera.
- Heavy battery + tank low and centered = low CoG, stable on uneven fields.

### 1. Underside (ground-facing mechanicals)

| Component | Footprint (mm) | Position (x,y mm from front-left) | Zone |
|---|---|---|---|
| HC-SR04 front | 45 x 20 | (137, 4) | mech |
| Motor FL | 37 x 70 | (16, 70) | drive |
| Motor FR | 37 x 70 | (267, 70) | drive |
| Motor RL +enc | 37 x 70 | (16, 310) | drive |
| Motor RR +enc | 37 x 70 | (267, 310) | drive |
| Cutter / weeder | 70 x 60 | (125, 120) | mech |
| Linear actuator 150N | 40 x 40 | (140, 300) | drive |
| NPK probe head | 45 x 45 | (137, 345) | sensor |
| HC-SR04 rear | 45 x 20 | (137, 426) | mech |

### 2. Lower deck - power / drive / fluid

| Component | Footprint (mm) | Position (x,y mm from front-left) | Zone |
|---|---|---|---|
| Rocker SW | 20 x 20 | (10, 8) | power |
| XT60 | 22 x 16 | (34, 10) | power |
| Fuse 30A | 30 x 16 | (10, 32) | power |
| LM2596 buck | 43 x 21 | (10, 54) | power |
| INA219 | 26 x 18 | (60, 54) | power |
| Screw bus | 42 x 18 | (10, 80) | power |
| Pump | 60 x 40 | (105, 18) | fluid |
| Fertilizer tank 500ml | 90 x 70 | (178, 12) | fluid |
| Float | 16 x 16 | (250, 18) | fluid |
| Power bank 10Ah | 70 x 140 | (10, 150) | power |
| Battery: 4S LiFePO4 pack (or legacy 3S LiPo 2200mAh, 34 x 105) | 40 x 130 | (150, 165) | power |
| 2-ch Relay | 51 x 39 | (250, 150) | drive |
| ACS712 x2 | 34 x 22 | (250, 300) | drive |
| BTS7960 #1 | 50 x 50 | (95, 372) | drive |
| BTS7960 #2 | 50 x 50 | (175, 372) | drive |

### 3. Upper deck - compute / sensors / UI

| Component | Footprint (mm) | Position (x,y mm from front-left) | Zone |
|---|---|---|---|
| ESP32 DevKit | 55 x 28 | (24, 24) | compute |
| ESP32-CAM pcb | 40 x 27 | (24, 66) | compute |
| Raspberry Pi 4 | 85 x 56 | (120, 18) | compute |
| Coral TPU | 65 x 30 | (218, 20) | compute |
| 30mm fan | 30 x 30 | (148, 80) | compute |
| I2C board: MPU6050(CoG)+ADS1115+PCF8574+VL53L1X | 80 x 58 | (120, 150) | sensor |
| MAX485 | 22 x 15 | (214, 160) | sensor |
| LoRa SX1276 | 18 x 16 | (246, 160) | compute |
| OLED 0.96 | 27 x 27 | (18, 378) | ui |
| Mode SW | 20 x 20 | (66, 382) | ui |
| Buttons x4 | 50 x 14 | (100, 386) | ui |
| E-STOP | 28 x 28 | (180, 378) | ui |

### 4. Top & mast (above upper deck, sky/forward line-of-sight)

| Component | Footprint (mm) | Position (x,y mm from front-left) | Zone |
|---|---|---|---|
| GPS Neo-6M | 25 x 25 | (140, 12) | sensor |
| LoRa antenna | 10 x 70 | (288, 12) | compute |
| US sweep SG90 | 23 x 12 | (150, 78) | mech |
| Pi Camera + 160 lens | 26 x 24 | (147, 118) | sensor |
| DHT22 | 15 x 28 | (40, 60) | sensor |
| Rain sensor | 40 x 30 | (240, 120) | sensor |


## Placement rules
1. **MPU6050 at CoG**, square to axes (clean heading/tilt).
2. **GPS + LoRa antenna on the mast**, away from BTS7960/motors (RF noise).
3. **Encoders on the rear wheels** (Pi GPIO17/27).
4. **CSI ribbon + I2C on the upper deck only** - never parallel to battery-bus motor leads.
5. **NPK probe + actuator center-rear underside**; rover halts while dosing (EVT_DOSING).
6. **Tank slightly forward of the axle** so CoG barely shifts as it empties.
7. **BTS7960 x2 at the rear** of the lower deck: shortest motor leads + best airflow + heatsinks facing the fan intake.
8. Reflective/white top + sun canopy + rear fan intake (FC-02 thermal plan).
