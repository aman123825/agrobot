"""Drop-in replacement for serial.Serial that speaks the HMAC-signed protocol.

Validates incoming command envelopes (v1|counter|cmd|hmac) using the same
AGRO_LINK_KEY as security.py, updates the rover model, and queues ACK/NAK
responses for the caller to read.

Usage:
    from sim.serial_sim import SimSerial
    ser = SimSerial()
    ser.open()
    ser.write(b"v1|123|FWD|<hmac>\\n")
    line = ser.readline()  # b"ACK FWD\\n"
"""
from __future__ import annotations

import hashlib
import hmac as hmac_mod
import os
import sys
import threading
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sim.rover_model import RoverSim  # noqa: E402

_KEY = os.getenv("AGRO_LINK_KEY", "").encode()
_TRUNC_HEX = 32  # 16 bytes, 32 hex chars

if not _KEY:
    import logging as _logging

    _logging.getLogger(__name__).warning(
        "AGRO_LINK_KEY is empty -- SimSerial will accept ANY correctly "
        "formatted envelope (HMAC computed with empty key). This is "
        "acceptable for local development but differs from production "
        "security.py which refuses to operate without the key."
    )


def _verify_envelope(raw: str) -> tuple[bool, str]:
    """Parse and verify an HMAC-signed command envelope.

    Returns (valid, command) where valid indicates HMAC check passed.
    """
    parts = raw.strip().split("|")
    if len(parts) != 4:
        return (False, "")
    version, counter_str, command, received_hmac = parts
    if version != "v1":
        return (False, "")
    # Verify HMAC
    msg = f"v1|{counter_str}|{command}"
    expected = hmac_mod.new(_KEY, msg.encode(), hashlib.sha256).hexdigest()[:_TRUNC_HEX]
    if not hmac_mod.compare_digest(expected, received_hmac):
        return (False, command)
    return (True, command)


class SimSerial:
    """Simulated serial port that mimics the ESP32 UART interface.

    Implements the subset of pyserial's Serial API used by SerialBridge:
        - write(data: bytes) -> int
        - readline() -> bytes
        - close() -> None

    Also exposes the underlying RoverSim for inspection.
    """

    def __init__(
        self,
        port: str = "/dev/null",
        baudrate: int = 115200,
        timeout: float | None = 0.1,
        rover: RoverSim | None = None,
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.rover = rover or RoverSim()
        self._rx_buffer: deque[bytes] = deque()
        self._lock = threading.Lock()
        self._last_counter = 0
        self._is_open = False

    # ------------------------------------------------------------------
    # pyserial-compatible interface
    # ------------------------------------------------------------------

    def open(self) -> None:
        """Open the simulated serial port (no-op, always succeeds)."""
        self._is_open = True

    @property
    def is_open(self) -> bool:
        return self._is_open

    def close(self) -> None:
        self._is_open = False

    def write(self, data: bytes) -> int:
        """Process an incoming command envelope.

        Validates HMAC, checks counter monotonicity, applies the command
        to the rover model, and queues an ACK or NAK response.
        """
        line = data.decode(errors="ignore").strip()
        if not line:
            return len(data)

        with self._lock:
            valid, command = _verify_envelope(line)
            if not valid:
                self._rx_buffer.append(b"NAK HMAC_FAIL\n")
                return len(data)

            # Check counter monotonicity
            parts = line.split("|")
            try:
                counter = int(parts[1])
            except (IndexError, ValueError):
                self._rx_buffer.append(b"NAK BAD_COUNTER\n")
                return len(data)

            if counter <= self._last_counter:
                self._rx_buffer.append(b"NAK REPLAY\n")
                return len(data)
            self._last_counter = counter

            # Apply command to rover model
            self.rover.apply_command(command)
            self._rx_buffer.append(f"ACK {command}\n".encode())

        return len(data)

    def readline(self) -> bytes:
        """Return the next queued response line, or empty bytes if none."""
        with self._lock:
            if self._rx_buffer:
                return self._rx_buffer.popleft()
        return b""

    # Alias used by some serial code
    def read_until(self, expected: bytes = b"\n", size: int | None = None) -> bytes:
        """Alias for readline (ignores expected/size for simplicity)."""
        return self.readline()
