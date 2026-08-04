# AgriRover Basic Bot — complete circuit connections

This guide matches the GPIO assignments in `firmware/include/pins.h`. It covers the ESP32 DevKit, two BTS7960 motor drivers, three HC-SR04 sensors, NPK/RS485 interface, moisture sensor, DHT22, battery sensing, pump relay, MG995 insertion servo, and the separate ESP32-CAM.

## Critical rules before powering anything

1. **Adjust the LM2596 output to exactly 5.00 V with a multimeter before connecting the ESP32, camera, servo, or sensors.**
2. Every low-voltage module must share one common ground with the ESP32 and battery negative.
3. Never connect an HC-SR04 ECHO pin directly to an ESP32 GPIO. Use the shown 10 kΩ/10 kΩ divider on every ECHO line.
4. Power the capacitive moisture sensor from **3.3 V**, not 5 V, because its analog output goes directly to GPIO34.
5. Put a 10 kΩ pull-up from relay input GPIO26 to 3.3 V so an active-low relay stays OFF during boot.
6. Power the MG995 from a strong separate 5 V branch. Do not power it from the ESP32 3.3 V pin or through the DevKit regulator.
7. Put a fuse close to battery positive and use an accessible master power switch.
8. Do not work on the motor or pump wiring while the battery is connected.

## Power distribution

Recommended 3S LiPo distribution:

```text
3S LiPo positive
   |
   +-- fuse -- master switch --+-- BTS7960 left B+
                               +-- BTS7960 right B+
                               +-- pump positive supply/relay contact
                               +-- LM2596 IN+

3S LiPo negative --------------+-- BTS7960 left B-
                               +-- BTS7960 right B-
                               +-- pump supply negative
                               +-- LM2596 IN-
                               +-- common logic GND

LM2596 5.00 V output -----------+-- ESP32 DevKit VIN/5V
                               +-- ESP32-CAM 5V
                               +-- HC-SR04 VCC (all three)
                               +-- MG995 red wire (use thick wire)
                               +-- relay module VCC if it is a 5 V module
                               +-- MAX485 VCC if using a 5 V MAX485 module
                               +-- NPK probe supply only if its datasheet permits 5 V

ESP32 DevKit 3.3 V ------------+-- BTS7960 logic VCC and R_EN/L_EN
                               +-- DHT22 VCC and data pull-up
                               +-- capacitive moisture VCC
                               +-- relay input pull-up

All grounds must be connected together.
```

### NPK supply warning

Many industrial 7-in-1 NPK probes require **9–24 V DC**, not 5 V. Power the probe from the voltage specified on its label/datasheet—often directly from the fused 12 V battery branch—and connect its supply negative to common ground. The MAX485 logic module remains on its rated logic supply.

### Noise protection recommendations

- Place a 470–1000 µF electrolytic capacitor plus 100 nF ceramic across the 5 V/GND rail near the MG995.
- Place a 470 µF capacitor near the ESP32-CAM 5 V input.
- Twist each motor pair and keep motor/pump wires away from ADC, DHT22, ultrasonic ECHO, and RS485 wires.
- Use a star-ground point near battery negative or the power distribution block; do not route servo/motor return current through the ESP32 ground lead.
- If the pump is a bare DC motor, add a flyback diode across the pump terminals: cathode/banded end to pump positive, anode to pump negative. A relay coil board normally has its own coil diode; the pump motor still benefits from suppression.
- For long RS485 cable, use twisted pair, one 120 Ω terminator at each physical end, and optionally a TVS device suitable for RS485.

## ESP32 DevKit pin connections

| ESP32 DevKit pin | Connect to | Electrical note |
|---|---|---|
| VIN/5V | LM2596 5.00 V output | Verify voltage before connection |
| GND | Common ground | Shared with battery, drivers, sensors, camera, servo and pump supply |
| 3V3 | 3.3 V logic/sensor rail | Do not power motors or servo from this pin |
| GPIO19 | Left BTS7960 RPWM | Left motor forward PWM |
| GPIO21 | Left BTS7960 LPWM | Left motor reverse PWM |
| GPIO22 | Right BTS7960 RPWM | Right motor forward PWM |
| GPIO23 | Right BTS7960 LPWM | Right motor reverse PWM |
| GPIO25 | Left HC-SR04 TRIG | Direct connection |
| GPIO18 | Left HC-SR04 ECHO divider output | Never connect raw 5 V ECHO |
| GPIO32 | Center HC-SR04 TRIG | Direct connection |
| GPIO33 | Center HC-SR04 ECHO divider output | Never connect raw 5 V ECHO |
| GPIO15 | Right HC-SR04 TRIG | Direct connection; GPIO15 is a boot strapping pin, so ensure the sensor does not force it high/low at reset |
| GPIO39 | Right HC-SR04 ECHO divider output | Input-only GPIO; no internal pull resistor |
| GPIO17 (TX2) | MAX485 DI | ESP32 transmits Modbus request |
| GPIO16 (RX2) | MAX485 RO | See MAX485 5 V logic warning below |
| GPIO4 | MAX485 DE and /RE tied together | HIGH transmit, LOW receive; GPIO4 is a boot strapping pin, so do not add a strong external pull-up |
| GPIO14 | DHT22 DATA | Add 10 kΩ from DATA to 3.3 V |
| GPIO34 | Capacitive moisture AOUT | Sensor powered from 3.3 V; GPIO34 is input-only |
| GPIO35 | Battery divider midpoint | 39 kΩ from battery positive, 10 kΩ to ground |
| GPIO26 | Active-low pump relay IN | Add 10 kΩ from GPIO26 to 3.3 V |
| GPIO13 | MG995 signal | Add 10 kΩ from GPIO13 to GND; servo power is separate 5 V branch |
| EN | Leave on the DevKit reset circuit (optional momentary reset button to GND) | Do not use an NC EN-to-GND connection as the actuator E-stop; see note below |
| USB | Laptop | Optional USB serial control, telemetry, calibration, and flashing |

## Motor drivers — two BTS7960/IBT-2 modules

### Left driver

| BTS7960 pin/terminal | Connection |
|---|---|
| B+ / motor-power positive | Fused/switched battery positive |
| B- / motor-power negative | Battery negative/common ground |
| M+ and M- | Left-side motor(s) |
| VCC | ESP32 3.3 V logic rail |
| GND | Common ground |
| R_EN | ESP32 3.3 V |
| L_EN | ESP32 3.3 V |
| RPWM | GPIO19 |
| LPWM | GPIO21 |
| R_IS / L_IS | Not used; insulate or leave open according to module documentation |

### Right driver

| BTS7960 pin/terminal | Connection |
|---|---|
| B+ / motor-power positive | Fused/switched battery positive |
| B- / motor-power negative | Battery negative/common ground |
| M+ and M- | Right-side motor(s) |
| VCC | ESP32 3.3 V logic rail |
| GND | Common ground |
| R_EN | ESP32 3.3 V |
| L_EN | ESP32 3.3 V |
| RPWM | GPIO22 |
| LPWM | GPIO23 |
| R_IS / L_IS | Not used |

If one side rotates backward when Forward is pressed, swap that side’s M+ and M− motor wires. Do not change battery polarity.

## HC-SR04 ultrasonic sensors

Each sensor uses 5 V power. Connect VCC to 5 V and GND to common ground.

| Sensor | TRIG | ECHO input at ESP32 |
|---|---|---|
| Left | GPIO25 | GPIO18 through divider |
| Center | GPIO32 | GPIO33 through divider |
| Right | GPIO15 | GPIO39 through divider |

Build each ECHO divider separately:

```text
HC-SR04 ECHO ---- 10 kΩ ----+---- ESP32 ECHO GPIO
                            |
                           10 kΩ
                            |
                           GND
```

This changes the approximately 5 V ECHO pulse to approximately 2.5 V.

## DHT22

| DHT22 pin | Connection |
|---|---|
| VCC | ESP32 3.3 V |
| DATA | GPIO14 |
| GND | Common ground |

Add a 10 kΩ resistor between DATA and 3.3 V. On a bare four-pin DHT22 viewed from the front grille, the usual order is VCC, DATA, NC, GND; verify the marking on your module.

## Capacitive soil-moisture sensor

| Sensor pin | Connection |
|---|---|
| VCC | ESP32 3.3 V only |
| GND | Common ground |
| AOUT | GPIO34 |
| DOUT | Not used |

After assembly, run `python laptop/calibrate.py --only moisture` and paste the measured constants into `firmware/src/sensors.cpp`.

## Battery voltage divider

Use a 39 kΩ upper resistor and 10 kΩ lower resistor:

```text
Battery positive ---- 39 kΩ ----+---- GPIO35
                                |
                               10 kΩ
                                |
Battery negative / GND ----------+
```

At a fully charged 12.6 V battery, GPIO35 sees approximately 2.57 V. The resistor common point goes only to GPIO35. Calibrate using `python laptop/calibrate.py --only battery`.

## NPK probe and RS485 transceiver

### ESP32 to transceiver

| ESP32 | MAX485 module |
|---|---|
| GPIO17 TX2 | DI |
| GPIO16 RX2 | RO |
| GPIO4 | DE and /RE tied together |
| GND | GND |
| Supply | Module-rated VCC |

### Transceiver to probe

| MAX485 | NPK probe |
|---|---|
| A | A / D+ / 485+ according to probe label |
| B | B / D− / 485− according to probe label |
| GND | Probe supply negative/common ground if supported |

If the probe never responds, first confirm its supply voltage, slave address `1`, 9600 baud, and A/B labeling. Some manufacturers label A/B oppositely; swapping only A and B is a valid diagnostic.

### Important logic-level warning

A classic MAX485 powered at 5 V can drive RO close to 5 V, which is unsafe for ESP32 GPIO16. Use one of these safe options:

- Prefer a 3.3 V RS485 transceiver such as MAX3485/SP3485; or
- Add a level shifter/divider on MAX485 RO before GPIO16.

Do not assume every “MAX485 module” has 3.3 V-safe output.

## Pump relay and pump

### Relay control side

| Relay module pin | Connection |
|---|---|
| IN | GPIO26 |
| VCC | Module-rated supply, commonly 5 V |
| GND | Common ground |

Add a 10 kΩ resistor from GPIO26 to 3.3 V. The firmware assumes an **active-low** relay.

### Relay contact side

For a pump rated for the chosen supply voltage:

```text
Fused pump supply positive ---- relay COM
relay NO ---------------------- pump positive
pump negative ----------------- pump supply negative/common ground
```

Use the normally-open contact so the pump is unpowered when the controller is off. Do not route pump current through the ESP32 board.

## MG995 insertion servo

| MG995 wire | Connection |
|---|---|
| Red | Strong regulated 5 V servo branch |
| Brown/black | Common ground |
| Orange/yellow signal | GPIO13 |

Add 10 kΩ from GPIO13 to ground. Use thick power/ground wires and local bulk capacitance. Before attaching the probe linkage, test and tune `SERVO_INSERT_UP_DEG` and `SERVO_INSERT_DOWN_DEG` in `firmware/include/config.h`.

## ESP32-CAM

The camera is a separate board and requires only power during normal operation:

| ESP32-CAM pin | Connection |
|---|---|
| 5V | Stable LM2596 5 V branch |
| GND | Common ground |

It communicates with the DevKit and phone over WiFi, not by signal wires. The DevKit creates `AgriRover-Control`; the camera joins at `192.168.4.2`.

For flashing only, connect a USB-UART adapter:

| USB-UART | ESP32-CAM |
|---|---|
| TX | U0R |
| RX | U0T |
| GND | GND |
| IO0 jumper | IO0 to GND while resetting/flashing |

Use 3.3 V UART signal levels. Power the camera from a stable 5 V source rather than a weak adapter 3.3 V output. Remove IO0-to-GND after flashing and reset.

## Hardware emergency-stop note

The current README describes `EN` with a normally-closed switch to ground. On an ESP32, holding EN low keeps the controller in reset; a normally-closed contact directly from EN to ground would therefore keep the ESP32 permanently reset until the button is operated. It is not a suitable independent motor-power E-stop as written.

Use a proper **normally-closed, latching emergency-stop switch in series with the motor/pump power feed or with the coil of a suitably rated power contactor**. This physically removes actuator power while allowing the ESP32 logic supply to remain available for diagnostics. The mobile `STOP` command is a software safety feature, not a substitute for the hardware power disconnect.

## Bring-up order

1. Disconnect motors, pump, servo linkage, and NPK probe.
2. Set LM2596 to 5.00 V and verify polarity.
3. Power the DevKit only; confirm the relay remains off at boot.
4. Add sensors one at a time and check telemetry.
5. Add BTS7960 logic wiring, then motor power with wheels raised.
6. Verify Forward/Back/Left/Right at low speed.
7. Connect and tune the unloaded servo before installing the probe linkage.
8. Connect the relay without the pump; verify its switching sequence.
9. Connect the pump and confirm flyback/noise suppression.
10. Connect the NPK probe using its documented supply voltage.
11. Power the ESP32-CAM and verify video at `http://192.168.4.2/`.
12. Test mobile release-stop, WiFi-loss dead-man, obstacle blocking, latched software STOP, and the physical actuator-power E-stop before field use.
