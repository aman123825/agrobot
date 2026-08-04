# AgriRover Basic Bot — ESP32-CAM video

Standalone firmware for an **AI-Thinker ESP32-CAM**. It joins the WiFi access point created by the main DevKit and serves live MJPEG video at a fixed address.

## Network

1. Power the main DevKit; it creates WiFi **`AgriRover-Control`**.
2. The camera joins that network automatically using the shared configuration in `../shared/network_config.h`.
3. The camera uses static IP **`192.168.4.2`**.
4. The mobile controller at **http://192.168.4.1/** embeds the video stream.

Endpoints:

- `http://192.168.4.2/` — camera page
- `http://192.168.4.2/stream` — multipart MJPEG stream
- `http://192.168.4.2/jpg` — single JPEG snapshot

## Build and flash

The ESP32-CAM has no USB. Use a 3.3 V USB-serial adapter for UART signaling while powering the board from a stable 5 V supply:

- CAM `5V` to 5 V, `GND` to GND
- CAM `U0R` to adapter TX, `U0T` to adapter RX
- Jumper `IO0` to `GND`, then power-cycle to enter the bootloader

```bash
cd basic-bot/camera
pio run -t upload
pio device monitor
```

Remove the `IO0` to `GND` jumper and reset to run. Serial output should show:

```text
Joining rover AP 'AgriRover-Control'...
CAM ready: http://192.168.4.2/
```

## Change credentials or addresses

Edit `../shared/network_config.h` and reflash **both** the DevKit and ESP32-CAM. Do not set credentials independently in this camera source.

## Notes

- The camera retries automatically if the rover WiFi is temporarily unavailable.
- Brown-outs during WiFi transmission are the usual cause of camera initialization failures or reboots. Use a solid 5 V supply and reseat the ribbon cable if initialization fails.
- The camera is a separate board and binary; it does not use any DevKit sensor or motor GPIOs.
