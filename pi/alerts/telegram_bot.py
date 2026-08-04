"""Telegram push alerts + two-way control (BOM #106; docs/UPGRADES.md §9).

Outbound alerts to the farmer's phone, e.g.:
  "Low nitrogen at Zone 3 (GPS: 18.5N 73.8E)"
  "Moisture critical"
  "Battery 15% - returning to base"
  "Tank empty - refill required"

Inbound commands (docs/UPGRADES.md §9 "Two-way Telegram control"):
  /stop /go /resume /status /photo /summary /help
handled by `TelegramCommander`, a long-polling daemon thread that dispatches
to callbacks injected by the orchestrator - this module never imports it.

Security (per SECURITY.md: authenticate every channel, fail closed):
  - Only chat IDs on an explicit allowlist (TELEGRAM_ALLOWED_CHAT_IDS env,
    comma-separated) may issue commands. An empty allowlist disables inbound
    handling entirely, even when a bot token is configured.
  - Unknown chat IDs are logged and ignored; the "unauthorized" courtesy
    reply is limited to once per chat per hour so it cannot become a spam
    amplifier.
  - Outbound replies are rate-limited (default 20/min) per Telegram limits.
  - The bot token stays in the environment (pi/.env, gitignored) - never in
    source control.

Stdlib-only (urllib): no `requests` dependency, and the HTTP transport is
injectable so everything is unit-testable with zero network.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
import urllib.request
import uuid
from collections import deque
from collections.abc import Callable, Iterable

import config

logger = logging.getLogger(__name__)

API_BASE = "https://api.telegram.org"

# command -> callback name in the injected callbacks dict
COMMAND_CALLBACKS = {
    "/stop": "stop",
    "/go": "resume",
    "/resume": "resume",
    "/status": "status",
    "/photo": "photo",
    "/summary": "summary",
}
COMMAND_HELP = {
    "/stop": "emergency stop",
    "/go": "resume driving",
    "/resume": "resume driving",
    "/status": "current rover status",
    "/photo": "camera snapshot",
    "/summary": "mission/savings summary",
}
# Fallback confirmations when a callback returns nothing to say.
DEFAULT_REPLIES = {
    "stop": "STOP sent - rover halted.",
    "resume": "RESUME sent - rover moving.",
}


def _multipart_encode(fields: dict[str, str],
                      files: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    """Minimal multipart/form-data encoder (stdlib-only, for sendPhoto).

    `files` maps field name -> (filename, raw bytes, content type).
    Returns (body, content_type_header_value).
    """
    boundary = "----AgriRoverBoundary" + uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body += (f"--{boundary}\r\n"
                 f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                 f"{value}\r\n").encode("utf-8")
    for name, (filename, data, ctype) in files.items():
        body += (f"--{boundary}\r\n"
                 f'Content-Disposition: form-data; name="{name}"; '
                 f'filename="{filename}"\r\n'
                 f"Content-Type: {ctype}\r\n\r\n").encode("utf-8")
        body += bytes(data) + b"\r\n"
    body += f"--{boundary}--\r\n".encode("utf-8")
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def _http_api(method: str, params: dict | None = None, *,
              files: dict[str, tuple[str, bytes, str]] | None = None,
              token: str | None = None, timeout: float = 35.0) -> dict:
    """Default HTTP transport: POST a Bot API method, return the parsed JSON.

    Kept as a module-level function so tests (and `TelegramCommander`'s `api`
    constructor arg) can swap it for a fake with the same signature.
    """
    token = config.TELEGRAM_TOKEN if token is None else token
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN not configured")
    url = f"{API_BASE}/bot{token}/{method}"
    if files:
        fields = {k: str(v) for k, v in (params or {}).items()}
        body, content_type = _multipart_encode(fields, files)
    else:
        body = json.dumps(params or {}).encode("utf-8")
        content_type = "application/json"
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": content_type})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_alert(message: str) -> bool:
    """Send a message via the Telegram Bot API. Returns True on success.

    Existing outbound-alert entry point - pi/main.py imports exactly this.
    """
    if not config.TELEGRAM_TOKEN or not config.TELEGRAM_CHAT_ID:
        # No credentials configured - skip silently in dev.
        return False
    try:
        resp = _http_api("sendMessage",
                         {"chat_id": config.TELEGRAM_CHAT_ID, "text": message},
                         timeout=10)
        return bool(resp.get("ok"))
    except Exception as exc:
        logger.debug("telegram alert failed (%s)", exc)
        return False


def _parse_command(text: str | None) -> str | None:
    """First word of the message, lowercased, '@BotName' suffix stripped."""
    text = (text or "").strip()
    if not text:
        return None
    word = text.split()[0].lower()
    if "@" in word:
        word = word.split("@", 1)[0]
    return word


class TelegramCommander:
    """Two-way Telegram control: long-poll getUpdates, dispatch to callbacks.

    callbacks: {"stop": fn, "resume": fn, "status": fn -> str,
                "photo": fn -> bytes | path, "summary": fn -> str}
    Missing entries simply make that command reply "not available"; callback
    exceptions are caught and reported so the poll thread never dies.

    Auth is an allowlist of chat IDs (constructor arg, falling back to the
    TELEGRAM_ALLOWED_CHAT_IDS env var). Empty allowlist = inbound disabled
    (fail closed - see SECURITY.md).
    """

    def __init__(self,
                 callbacks: dict[str, Callable] | None = None,
                 allowed_chat_ids: Iterable[int | str] | None = None,
                 token: str | None = None,
                 api: Callable | None = None,
                 poll_timeout_s: int = 25,
                 max_backoff_s: float = 60.0,
                 max_replies_per_min: int = 20,
                 unauthorized_reply_interval_s: float = 3600.0):
        self.callbacks = dict(callbacks or {})
        self.token = config.TELEGRAM_TOKEN if token is None else token
        if allowed_chat_ids is None:
            raw = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS",
                            getattr(config, "TELEGRAM_ALLOWED_CHAT_IDS", ""))
            allowed_chat_ids = [p.strip() for p in raw.split(",") if p.strip()]
        self.allowed_chat_ids = frozenset(str(c) for c in allowed_chat_ids)
        self.poll_timeout_s = poll_timeout_s
        self.max_backoff_s = max_backoff_s
        self.max_replies_per_min = max_replies_per_min
        self.unauthorized_reply_interval_s = unauthorized_reply_interval_s
        if api is None:
            api = lambda method, params=None, files=None: _http_api(  # noqa: E731
                method, params, files=files, token=self.token,
                timeout=self.poll_timeout_s + 10)
        self._api = api
        self._offset = 0
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._reply_times: deque[float] = deque()
        self._unauth_last_reply: dict[str, float] = {}

    # ---- lifecycle ---------------------------------------------------------

    def start(self) -> bool:
        """Start the long-polling daemon thread. Returns True if running."""
        if not self.token:
            logger.info("telegram inbound disabled: no TELEGRAM_TOKEN")
            return False
        if not self.allowed_chat_ids:
            # Fail closed (SECURITY.md): a token alone must not open inbound.
            logger.warning("telegram inbound disabled: TELEGRAM_ALLOWED_CHAT_IDS "
                           "is empty (fail closed)")
            return False
        if self._thread is not None and self._thread.is_alive():
            return True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_loop,
                                        name="telegram-commander", daemon=True)
        self._thread.start()
        logger.info("telegram commander polling (%d allowed chats)",
                    len(self.allowed_chat_ids))
        return True

    def stop(self, timeout: float = 2.0) -> None:
        """Signal the poll thread to exit and wait briefly for it."""
        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            # A long poll may be mid-flight (up to poll_timeout_s); it's a
            # daemon thread, so a short join is enough for a clean shutdown.
            thread.join(timeout=timeout)
        self._thread = None

    # ---- polling -----------------------------------------------------------

    def _poll_once(self) -> int:
        """One getUpdates round-trip; handles each update. Returns count."""
        resp = self._api("getUpdates", {"offset": self._offset,
                                        "timeout": self.poll_timeout_s})
        updates = resp.get("result", []) if isinstance(resp, dict) else []
        for update in updates:
            self._handle_update(update)
        return len(updates)

    def _poll_loop(self) -> None:
        backoff = 1.0
        while not self._stop_event.is_set():
            try:
                handled = self._poll_once()
                backoff = 1.0
                if handled == 0:
                    # Real long polls block server-side; this only guards
                    # against hot-spinning if the API returns instantly.
                    self._stop_event.wait(0.05)
            except Exception as exc:
                logger.warning("telegram poll error (%s); retry in %.0fs",
                               exc, backoff)
                self._stop_event.wait(backoff)
                backoff = min(backoff * 2.0, self.max_backoff_s)

    # ---- update handling ---------------------------------------------------

    def _handle_update(self, update: dict, now: float | None = None) -> None:
        """Process a single getUpdates entry. Never raises."""
        now = time.time() if now is None else now
        update_id = update.get("update_id")
        if isinstance(update_id, int):
            self._offset = max(self._offset, update_id + 1)
        msg = update.get("message") or update.get("edited_message")
        if not isinstance(msg, dict):
            return
        chat_id = (msg.get("chat") or {}).get("id")
        if chat_id is None:
            return

        # AUTH (SECURITY.md): allowlist only; empty allowlist = fail closed.
        if not self.allowed_chat_ids:
            logger.debug("telegram inbound disabled; dropping update %s", update_id)
            return
        if str(chat_id) not in self.allowed_chat_ids:
            self._handle_unauthorized(chat_id, now)
            return

        command = _parse_command(msg.get("text"))
        if command is None:
            return
        logger.info("telegram command %s from chat %s", command, chat_id)
        if command == "/help":
            self._send_text(chat_id, self._help_text(), now=now)
            return
        name = COMMAND_CALLBACKS.get(command)
        if name is None:
            self._send_text(chat_id, f"Unknown command {command}. Try /help.",
                            now=now)
            return
        callback = self.callbacks.get(name)
        if callback is None:
            self._send_text(chat_id, f"{command} is not available on this rover.",
                            now=now)
            return
        try:
            result = callback()
        except Exception as exc:
            logger.exception("telegram callback %r failed", name)
            self._send_text(chat_id, f"Error running {command}: {exc}", now=now)
            return
        if name == "photo":
            self._send_photo(chat_id, result, now=now)
        else:
            text = result if isinstance(result, str) else \
                DEFAULT_REPLIES.get(name, "OK")
            self._send_text(chat_id, text, now=now)

    def _handle_unauthorized(self, chat_id, now: float) -> None:
        """Log + ignore; courtesy reply at most once per chat per hour."""
        logger.warning("telegram: ignoring command from unauthorized chat %s",
                       chat_id)
        key = str(chat_id)
        last = self._unauth_last_reply.get(key)
        if last is not None and now - last < self.unauthorized_reply_interval_s:
            return
        self._unauth_last_reply[key] = now
        self._send_text(chat_id, "Unauthorized.", now=now)

    def _help_text(self) -> str:
        lines = ["AgriRover commands:"]
        for cmd, name in COMMAND_CALLBACKS.items():
            note = "" if name in self.callbacks else " (not available)"
            lines.append(f"{cmd} - {COMMAND_HELP[cmd]}{note}")
        lines.append("/help - this list")
        return "\n".join(lines)

    # ---- outbound (rate-limited) -------------------------------------------

    def _outbound_ok(self, now: float) -> bool:
        """Sliding-window limiter: max_replies_per_min sends per 60 s."""
        window = self._reply_times
        while window and now - window[0] >= 60.0:
            window.popleft()
        if len(window) >= self.max_replies_per_min:
            return False
        window.append(now)
        return True

    def _send_text(self, chat_id, text: str, now: float | None = None) -> None:
        now = time.time() if now is None else now
        if not self._outbound_ok(now):
            logger.warning("telegram reply rate-limited; dropped: %.60s", text)
            return
        try:
            self._api("sendMessage", {"chat_id": chat_id, "text": text})
        except Exception as exc:
            logger.warning("telegram sendMessage failed (%s)", exc)

    def _send_photo(self, chat_id, photo, now: float | None = None) -> None:
        """Send a JPEG (bytes or file path) via sendPhoto multipart."""
        now = time.time() if now is None else now
        if photo is None:
            self._send_text(chat_id, "No photo available.", now=now)
            return
        if isinstance(photo, (str, os.PathLike)):
            try:
                with open(photo, "rb") as fh:
                    data = fh.read()
            except OSError as exc:
                logger.warning("telegram photo unreadable (%s)", exc)
                self._send_text(chat_id, "Photo unavailable.", now=now)
                return
        else:
            data = bytes(photo)
        if not self._outbound_ok(now):
            logger.warning("telegram photo rate-limited; dropped")
            return
        try:
            self._api("sendPhoto", {"chat_id": chat_id},
                      files={"photo": ("photo.jpg", data, "image/jpeg")})
        except Exception as exc:
            logger.warning("telegram sendPhoto failed (%s)", exc)


if __name__ == "__main__":
    print("sent" if send_alert("AgriRover test alert") else "not configured")
