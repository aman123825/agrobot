"""Lightweight HTTP + WebSocket server for remote rover control.

Uses ONLY Python standard library. Provides:
- Static file serving from pi/web/static/
- REST-like API endpoints for mission and plant data
- WebSocket endpoint at /ws for real-time telemetry and drive commands

Usage::

    python3 web/server.py --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import logging
import os
import struct
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

# ---------------------------------------------------------------------------
# Adjust sys.path so we can import sibling pi/ modules when run as a script.
# ---------------------------------------------------------------------------
_PI_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PI_DIR not in sys.path:
    sys.path.insert(0, _PI_DIR)

# Optional imports -- graceful degradation when hardware libs are absent.
try:
    from mission.scheduler import MissionScheduler  # type: ignore[import-untyped]
except Exception:
    MissionScheduler = None  # type: ignore[assignment,misc]

try:
    from data.plant_db import PlantDB  # type: ignore[import-untyped]
except Exception:
    PlantDB = None  # type: ignore[assignment,misc]

try:
    from bridge.serial_bridge import SerialBridge  # type: ignore[import-untyped]
except Exception:
    SerialBridge = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# WebSocket constants (RFC 6455)
# ---------------------------------------------------------------------------
_WS_MAGIC_GUID = "258EAFA5-E914-47DA-95CA-5AB4085CD29E"
_WS_OPCODE_TEXT = 0x1
_WS_OPCODE_BINARY = 0x2
_WS_OPCODE_CLOSE = 0x8
_WS_OPCODE_PING = 0x9
_WS_OPCODE_PONG = 0xA

# Maximum WebSocket receive buffer size (bytes). Connections exceeding this
# limit are forcibly closed to prevent memory exhaustion attacks.
MAX_WS_BUFFER = 65536

# Authentication token for WebSocket connections. If set, the client must
# provide this token as a query parameter: /ws?token=<value>.
# If not set (empty string), authentication is disabled (development mode).
_WS_AUTH_TOKEN = os.getenv("AGROBOT_WEB_TOKEN", "")

# ---------------------------------------------------------------------------
# Globals (initialized in main)
# ---------------------------------------------------------------------------
_scheduler: MissionScheduler | None = None
_plant_db: PlantDB | None = None
_serial: object | None = None
_ws_clients: list[WebSocketClient] = []
_ws_clients_lock = threading.Lock()
_telemetry: dict = {
    "battery_pct": 0,
    "lat": 0.0,
    "lng": 0.0,
    "speed": 0.0,
    "mode": "idle",
    "npk": {"n": 0, "p": 0, "k": 0},
}
_telemetry_lock = threading.Lock()

# Default static directory relative to this file.
_DEFAULT_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


# ===========================================================================
# WebSocket helpers
# ===========================================================================


def _ws_accept_key(client_key: str) -> str:
    """Compute the Sec-WebSocket-Accept value per RFC 6455 section 4.2.2."""
    raw = client_key.strip() + _WS_MAGIC_GUID
    sha1 = hashlib.sha1(raw.encode("utf-8")).digest()
    return base64.b64encode(sha1).decode("utf-8")


def _ws_encode_frame(payload: bytes, opcode: int = _WS_OPCODE_TEXT) -> bytes:
    """Encode a WebSocket frame (server to client -- no masking)."""
    length = len(payload)
    frame = bytearray()
    frame.append(0x80 | opcode)  # FIN + opcode
    if length < 126:
        frame.append(length)
    elif length < 65536:
        frame.append(126)
        frame.extend(struct.pack("!H", length))
    else:
        frame.append(127)
        frame.extend(struct.pack("!Q", length))
    frame.extend(payload)
    return bytes(frame)


def _ws_decode_frame(data: bytes) -> tuple[int, bytes, int]:
    """Decode a single WebSocket frame from *data*.

    Returns (opcode, payload, total_bytes_consumed).
    Raises ValueError if incomplete.
    """
    if len(data) < 2:
        raise ValueError("incomplete frame header")

    opcode = data[0] & 0x0F
    masked = bool(data[1] & 0x80)
    payload_len = data[1] & 0x7F
    offset = 2

    if payload_len == 126:
        if len(data) < 4:
            raise ValueError("incomplete extended length")
        payload_len = struct.unpack("!H", data[2:4])[0]
        offset = 4
    elif payload_len == 127:
        if len(data) < 10:
            raise ValueError("incomplete extended length")
        payload_len = struct.unpack("!Q", data[2:10])[0]
        offset = 10

    if masked:
        if len(data) < offset + 4:
            raise ValueError("incomplete mask")
        mask_key = data[offset : offset + 4]
        offset += 4

    if len(data) < offset + payload_len:
        raise ValueError("incomplete payload")

    raw = data[offset : offset + payload_len]
    if masked:
        payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(raw))
    else:
        payload = raw

    return opcode, payload, offset + payload_len


# ===========================================================================
# WebSocket client wrapper
# ===========================================================================


class WebSocketClient:
    """Wraps a raw socket that has been upgraded to WebSocket."""

    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self._closed = False
        self._lock = threading.Lock()

    def send(self, message: str) -> None:
        """Send a text message to the client."""
        if self._closed:
            return
        frame = _ws_encode_frame(message.encode("utf-8"), _WS_OPCODE_TEXT)
        try:
            with self._lock:
                self.sock.sendall(frame)
        except OSError:
            self.close()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self.sock.close()
        except OSError:
            pass

    @property
    def closed(self) -> bool:
        return self._closed


def _broadcast_ws(message: str) -> None:
    """Send a message to all connected WebSocket clients."""
    with _ws_clients_lock:
        alive = []
        for client in _ws_clients:
            if not client.closed:
                client.send(message)
                alive.append(client)
        _ws_clients[:] = alive


# ===========================================================================
# WebSocket handler thread
# ===========================================================================


def _handle_ws_client(client: WebSocketClient) -> None:
    """Read loop for a single WebSocket client."""
    buf = bytearray()
    while not client.closed:
        try:
            chunk = client.sock.recv(4096)
            if not chunk:
                break
            buf.extend(chunk)
        except OSError:
            break

        # Guard against unbounded buffer growth (slow-loris / memory exhaustion).
        if len(buf) > MAX_WS_BUFFER:
            logger.warning(
                "WebSocket buffer exceeded %d bytes for %s; disconnecting",
                MAX_WS_BUFFER,
                client.addr,
            )
            break

        # Process all complete frames in buffer.
        while buf:
            try:
                opcode, payload, consumed = _ws_decode_frame(bytes(buf))
            except ValueError:
                break  # incomplete frame
            buf = buf[consumed:]

            if opcode == _WS_OPCODE_CLOSE:
                client.close()
                break
            elif opcode == _WS_OPCODE_PING:
                pong = _ws_encode_frame(payload, _WS_OPCODE_PONG)
                try:
                    client.sock.sendall(pong)
                except OSError:
                    client.close()
                    break
            elif opcode in (_WS_OPCODE_TEXT, _WS_OPCODE_BINARY):
                _handle_ws_message(client, payload)

    client.close()
    with _ws_clients_lock:
        if client in _ws_clients:
            _ws_clients.remove(client)
    logger.info("WebSocket client disconnected: %s", client.addr)


def _handle_ws_message(client: WebSocketClient, payload: bytes) -> None:
    """Process an incoming WebSocket text message."""
    try:
        msg = json.loads(payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return

    msg_type = msg.get("type")

    if msg_type == "drive":
        cmd = msg.get("cmd", "").upper()
        valid_cmds = {"FWD", "BACK", "LEFT", "RIGHT", "STOP", "DRIVE_STOP", "RESUME"}
        if cmd in valid_cmds:
            _send_serial_command(cmd)
            logger.info("Drive command: %s", cmd)
    elif msg_type == "setpwm":
        left = int(msg.get("left", 0))
        right = int(msg.get("right", 0))
        _send_serial_command(f"SETPWM {left} {right}")
        logger.info("SETPWM %d %d", left, right)
    elif msg_type == "dose":
        _send_serial_command("DOSE")
    elif msg_type == "ping":
        client.send(json.dumps({"type": "pong", "ts": time.time()}))


def _send_serial_command(cmd: str) -> None:
    """Send command to the serial bridge if available."""
    if _serial is not None:
        try:
            _serial.send(cmd)  # type: ignore[union-attr]
        except Exception as exc:  # noqa: BLE001
            logger.warning("Serial send failed: %s", exc)


# ===========================================================================
# HTTP Request Handler
# ===========================================================================

_MIME_TYPES: dict[str, str] = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff2": "font/woff2",
}


class RoverRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler with REST API and WebSocket upgrade support."""

    static_dir: str = _DEFAULT_STATIC_DIR

    def log_message(self, format, *args):
        logger.info("HTTP %s %s", self.address_string(), format % args)

    # ------------------------------------------------------------------
    # WebSocket upgrade
    # ------------------------------------------------------------------

    def _try_ws_upgrade(self) -> bool:
        """Attempt WebSocket upgrade. Returns True if upgrade was performed."""
        upgrade_header = self.headers.get("Upgrade", "").lower()
        if upgrade_header != "websocket":
            return False

        # Token authentication: if AGROBOT_WEB_TOKEN is set, require matching
        # token query parameter on the WebSocket URL.
        if _WS_AUTH_TOKEN:
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            token = qs.get("token", [""])[0]
            if token != _WS_AUTH_TOKEN:
                self.send_error(403, "Invalid or missing authentication token")
                return True

        key = self.headers.get("Sec-WebSocket-Key", "")
        if not key:
            self.send_error(400, "Missing Sec-WebSocket-Key")
            return True

        accept = _ws_accept_key(key)
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n"
            "\r\n"
        )
        self.wfile.write(response.encode("utf-8"))
        self.wfile.flush()

        # Hand off to WebSocket handler
        client = WebSocketClient(self.request, self.client_address)
        with _ws_clients_lock:
            _ws_clients.append(client)
        logger.info("WebSocket client connected: %s", self.client_address)
        _handle_ws_client(client)
        return True

    # ------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # WebSocket upgrade
        if path == "/ws":
            if self._try_ws_upgrade():
                return

        # API endpoints
        if path == "/api/missions":
            self._api_get_missions()
            return
        if path == "/api/plants":
            self._api_get_plants()
            return
        if path == "/api/status":
            self._api_get_status()
            return

        # Static files
        self._serve_static(path)

    # ------------------------------------------------------------------
    # POST
    # ------------------------------------------------------------------

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/missions":
            self._api_post_mission()
            return

        self.send_error(404)

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def do_DELETE(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # DELETE /api/missions/<id>
        if path.startswith("/api/missions/"):
            mission_id = path[len("/api/missions/"):]
            self._api_delete_mission(mission_id)
            return

        self.send_error(404)

    # ------------------------------------------------------------------
    # API implementations
    # ------------------------------------------------------------------

    def _api_get_missions(self) -> None:
        if _scheduler is None:
            self._json_response({"missions": [], "error": "scheduler not available"})
            return
        missions = _scheduler.list_missions(include_completed=True)
        self._json_response({"missions": missions})

    def _api_post_mission(self) -> None:
        if _scheduler is None:
            self._json_response(
                {"error": "scheduler not available"}, status=503
            )
            return
        body = self._read_body()
        if body is None:
            return
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self._json_response({"error": "invalid JSON"}, status=400)
            return

        mission_type = data.get("type", "")
        zone = data.get("zone", {})
        params = data.get("params", {})

        try:
            mid = _scheduler.add_mission(mission_type, zone, params)
        except ValueError as exc:
            self._json_response({"error": str(exc)}, status=400)
            return

        self._json_response({"id": mid, "status": "queued"}, status=201)

    def _api_delete_mission(self, mission_id: str) -> None:
        if _scheduler is None:
            self._json_response(
                {"error": "scheduler not available"}, status=503
            )
            return
        ok = _scheduler.cancel_mission(mission_id)
        if ok:
            self._json_response({"id": mission_id, "status": "cancelled"})
        else:
            self._json_response(
                {"error": "mission not found or already finished"}, status=404
            )

    def _api_get_plants(self) -> None:
        if _plant_db is None:
            self._json_response({"plants": {}, "error": "plant_db not available"})
            return
        plants = _plant_db.get_all_plants()
        self._json_response({"plants": plants})

    def _api_get_status(self) -> None:
        with _telemetry_lock:
            data = dict(_telemetry)
        data["ws_clients"] = len(_ws_clients)
        data["scheduler_available"] = _scheduler is not None
        data["plant_db_available"] = _plant_db is not None
        self._json_response(data)

    # ------------------------------------------------------------------
    # Static file serving
    # ------------------------------------------------------------------

    def _serve_static(self, path: str) -> None:
        if path == "/" or path == "":
            path = "/index.html"

        # Prevent path traversal
        safe = os.path.normpath(path.lstrip("/"))
        if safe.startswith("..") or os.path.isabs(safe):
            self.send_error(403)
            return

        filepath = os.path.join(self.static_dir, safe)
        if not os.path.isfile(filepath):
            self.send_error(404)
            return

        ext = os.path.splitext(filepath)[1].lower()
        content_type = _MIME_TYPES.get(ext, "application/octet-stream")

        try:
            with open(filepath, "rb") as fh:
                content = fh.read()
        except OSError:
            self.send_error(500)
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _json_response(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> bytes | None:
        length_str = self.headers.get("Content-Length", "0")
        try:
            length = int(length_str)
        except ValueError:
            self.send_error(400, "Invalid Content-Length")
            return None
        if length > 1_000_000:
            self.send_error(413, "Payload too large")
            return None
        return self.rfile.read(length)


# ===========================================================================
# Threaded HTTP server
# ===========================================================================


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTPServer that handles each request in a new thread."""

    daemon_threads = True
    allow_reuse_address = True


# ===========================================================================
# Telemetry broadcast thread
# ===========================================================================


def _telemetry_loop(interval: float = 2.0) -> None:
    """Periodically broadcast telemetry to all WebSocket clients."""
    while True:
        time.sleep(interval)
        with _telemetry_lock:
            data = dict(_telemetry)
        msg = json.dumps({"type": "telemetry", "data": data})
        _broadcast_ws(msg)

        # Also broadcast mission status if scheduler is available
        if _scheduler is not None:
            missions = _scheduler.list_missions(include_completed=False)
            current = None
            for m in missions:
                if m["status"] == "active":
                    current = m
                    break
            if current is None and missions:
                # Show next queued without promoting it
                current = missions[0]
            mission_msg = json.dumps({
                "type": "mission_status",
                "data": {"current": current},
            })
            _broadcast_ws(mission_msg)


# ===========================================================================
# Main
# ===========================================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Agrobot Web Remote Control Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address")
    parser.add_argument("--port", type=int, default=8080, help="Listen port")
    parser.add_argument(
        "--static-dir",
        default=_DEFAULT_STATIC_DIR,
        help="Path to static files directory",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Set up static dir on handler class
    RoverRequestHandler.static_dir = os.path.abspath(args.static_dir)

    # Initialize optional integrations
    global _scheduler, _plant_db, _serial

    if MissionScheduler is not None:
        try:
            _scheduler = MissionScheduler()
            logger.info("MissionScheduler initialized")
        except Exception as exc:  # noqa: BLE001
            logger.warning("MissionScheduler init failed: %s", exc)

    if PlantDB is not None:
        try:
            _plant_db = PlantDB()
            logger.info("PlantDB initialized")
        except Exception as exc:  # noqa: BLE001
            logger.warning("PlantDB init failed: %s", exc)

    if SerialBridge is not None:
        try:
            _serial = SerialBridge()
            _serial.open()  # required before send(); without it commands are dropped
            logger.info("SerialBridge initialized and opened")
        except Exception as exc:  # noqa: BLE001
            logger.warning("SerialBridge not available: %s", exc)
            _serial = None
    # NOTE: the serial port has a single owner. Run EITHER the orchestrator
    # (pi/main.py) OR this web server as the serial owner - not both against the
    # same /dev/ttyUSB0, or commands will interleave and corrupt.

    # Start telemetry broadcast thread
    telemetry_thread = threading.Thread(target=_telemetry_loop, daemon=True)
    telemetry_thread.start()

    # Start HTTP server
    server = ThreadedHTTPServer((args.host, args.port), RoverRequestHandler)
    logger.info("Server starting on http://%s:%d", args.host, args.port)
    logger.info("Static dir: %s", RoverRequestHandler.static_dir)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()

    if _plant_db is not None:
        _plant_db.close()


if __name__ == "__main__":
    main()
