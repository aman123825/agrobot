# Mobile control

The main ESP32 DevKit hosts a private WiFi network and a touch-friendly control page. The ESP32-CAM joins that same network, so one phone screen provides controls, telemetry, and live video without a router or installed app.

## Connect

1. Flash both `firmware/` and `camera/`.
2. Power the DevKit first, then the ESP32-CAM.
3. Join WiFi **AgriRover-Control** on the phone.
4. Enter password **agrirover123**.
5. Keep the connection when the phone warns that the network has no internet.
6. Open **http://192.168.4.1/**.

The camera is at **http://192.168.4.2/** and its MJPEG stream is embedded automatically.

## Controls

- Hold Forward, Back, Left, or Right to move. Release to stop.
- The speed slider changes motor PWM from 60 to 255.
- **EMERGENCY STOP** latches the firmware halt. Motion stays blocked until **RESUME** is pressed.
- **DOSE** runs presoak, probe insertion, fertilizer injection, and retraction. Driving is inhibited for the entire sequence.
- **Probe ↓ / Probe ↑** manually lower or raise the NPK probe (servo) by themselves. Lowering freezes the drive until you raise the probe again.
- **Disable pump** prevents dosing until re-enabled.
- **Refresh telemetry** requests an immediate reading.

## Safety behavior

The firmware, not the browser, owns safety. A 1-second dead-man stops the motors if drive commands stop arriving. Closing the page, hiding the page, losing WiFi, or switching off the phone therefore stops the rover. Obstacle, low-battery, overtemperature, dosing, and latched-halt interlocks remain active.

Only one drive controller owns the motors at a time. If the USB laptop console is driving, the phone receives `NAK controller_busy`, and vice versa. Emergency STOP is accepted from either interface at all times.

## Change WiFi credentials

Edit `shared/network_config.h` and flash both boards again. The password must contain at least eight characters. Both boards intentionally include the same shared file so their credentials and static IPs cannot drift apart.

## Addresses

| Device | Address |
|---|---|
| DevKit control page | `http://192.168.4.1/` |
| DevKit WebSocket | `ws://192.168.4.1/ws` |
| ESP32-CAM page | `http://192.168.4.2/` |
| ESP32-CAM stream | `http://192.168.4.2/stream` |

## Troubleshooting

- **Control page does not open:** confirm the phone is still connected to `AgriRover-Control`; disable mobile-data auto-switching for this WiFi network.
- **Controls connect but video is offline:** power-cycle the ESP32-CAM, verify its 5 V supply, and check its serial output for `CAM ready: http://192.168.4.2/`.
- **Phone says `controller_busy`:** stop/release the laptop controls or wait one second for the drive lease to expire.
- **Forward is rejected:** check the obstacle banner and the three ultrasonic distances. Reverse and in-place turning remain available.
- **DOSE is disabled:** re-enable the pump and wait for any existing dosing cycle to finish.
- **Frequent camera resets:** the camera supply is sagging during WiFi transmission. Use a stable 5 V rail and common ground.

## Required bench test

Keep the wheels off the ground for the first test. Verify direction, release-stop, WiFi-loss stop, emergency halt/resume, each safety interlock, servo travel, and pump timing before field operation.
