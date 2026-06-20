"""Command-link signing for the Pi -> ESP32 channel.

Mirrors firmware/src/secure_link.cpp: every command is wrapped as

    v1|<counter>|<command>|<hmac_hex>

where hmac = HMAC-SHA256(AGRO_LINK_KEY, "v1|<counter>|<command>") truncated to
16 bytes (32 hex chars). The counter strictly increases - seeded from epoch
milliseconds and persisted - so the ESP32 rejects replays.

The key comes from the AGRO_LINK_KEY environment variable and must match the
firmware's COMMAND_HMAC_KEY exactly. If it is not set, sign() refuses to run
(fail closed) rather than emitting an unsigned command the rover would reject.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import threading
import time

_KEY = os.getenv("AGRO_LINK_KEY", "").encode()
_TRUNC_HEX = 32  # 16 bytes * 2
_LOCK = threading.Lock()
_COUNTER_PATH = os.getenv(
    "AGRO_COUNTER_FILE", os.path.expanduser("~/.agrorover_counter")
)


def is_configured() -> bool:
    """True if a link key is present."""
    return len(_KEY) > 0


def _next_counter() -> int:
    """Monotonic counter: max(persisted+1, epoch_ms), persisted atomically."""
    with _LOCK:
        last = 0
        try:
            with open(_COUNTER_PATH, encoding="utf-8") as fh:
                last = int(fh.read().strip() or "0")
        except (OSError, ValueError):
            last = 0
        nxt = max(last + 1, int(time.time() * 1000))
        try:
            tmp = f"{_COUNTER_PATH}.tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(str(nxt))
            os.replace(tmp, _COUNTER_PATH)
        except OSError:
            pass
        return nxt


def sign(command: str) -> str:
    """Return the signed envelope for `command`. Raises if no key configured."""
    if not is_configured():
        raise RuntimeError(
            "AGRO_LINK_KEY not set; refusing to send unsigned command "
            "(the rover would reject it anyway)."
        )
    if "|" in command:
        raise ValueError("command must not contain '|'")
    counter = _next_counter()
    msg = f"v1|{counter}|{command}"
    tag = hmac.new(_KEY, msg.encode(), hashlib.sha256).hexdigest()[:_TRUNC_HEX]
    return f"{msg}|{tag}"
