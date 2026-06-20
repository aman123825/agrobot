# Agrobot Web Remote Control

A lightweight web-based remote control interface for the Agrobot rover. Built using only Python standard library on the server side, with vanilla HTML/CSS/JavaScript on the client.

## Quick Start

```bash
cd pi
python3 web/server.py --port 8080
```

Then open `http://<pi-ip>:8080` on your phone or computer.

## Command-Line Options

| Flag          | Default   | Description                          |
|---------------|-----------|--------------------------------------|
| `--host`      | 0.0.0.0   | Bind address                         |
| `--port`      | 8080      | Listen port                          |
| `--static-dir`| web/static| Path to the static files directory   |

## Features

- **Virtual Joystick** - Touch or mouse-based drive control (FWD/BACK/LEFT/RIGHT/STOP)
- **Live Telemetry** - Battery, GPS, NPK, speed, and mode displayed in real time
- **Mission Control** - Create, view, and cancel missions through the web UI
- **Plant Database** - Browse tracked plants with health observations
- **Camera Feed** - MJPEG stream or periodic JPEG capture (when available)
- **Responsive Design** - Works on mobile phones, tablets, and desktops

## WebSocket Protocol

The server exposes a WebSocket endpoint at `/ws`. Messages are JSON objects with a `type` field.

### Client to Server

```json
{"type": "drive", "cmd": "FWD"}
{"type": "drive", "cmd": "STOP"}
{"type": "setpwm", "left": 180, "right": 180}
{"type": "dose"}
{"type": "ping"}
```

Valid drive commands: `FWD`, `BACK`, `LEFT`, `RIGHT`, `STOP`, `DRIVE_STOP`, `RESUME`

### Server to Client

```json
{"type": "telemetry", "data": {"battery_pct": 85, "lat": 12.34, "lng": 56.78, "speed": 0.5, "mode": "auto", "npk": {"n": 10, "p": 5, "k": 8}}}
{"type": "mission_status", "data": {"current": {...}}}
{"type": "pong", "ts": 1718000000.0}
```

Telemetry is broadcast every 2 seconds to all connected clients.

## REST API

| Method | Endpoint              | Description              |
|--------|-----------------------|--------------------------|
| GET    | `/api/missions`       | List all missions        |
| POST   | `/api/missions`       | Create a new mission     |
| DELETE  | `/api/missions/<id>` | Cancel a mission         |
| GET    | `/api/plants`         | List all tracked plants  |
| GET    | `/api/status`         | Rover status summary     |

### POST /api/missions

```json
{
  "type": "scan",
  "zone": {"waypoints": [[12.34, 56.78]]},
  "params": {"speed": 0.5}
}
```

## Security Considerations

- This server is intended for **local network use only**
- There is no authentication or encryption built in
- Do not expose this port to the public internet
- For remote access, use a VPN or SSH tunnel
- Drive commands are forwarded to the serial bridge which applies HMAC signing

## Architecture

```
Browser <--WebSocket--> server.py <--serial--> ESP32
                           |
                           +--> mission/scheduler.py
                           +--> data/plant_db.py
```

The server uses Python `http.server` with `ThreadingMixIn` for concurrent connections. WebSocket framing follows RFC 6455 using only `hashlib`, `base64`, and `struct` from stdlib.
