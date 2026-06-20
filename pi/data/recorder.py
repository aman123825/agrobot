"""Black-box recorder: structured, size-rotated JSONL event log.

Records every command, sensor snapshot, safety event, and dosing action so a
field incident can be reconstructed afterwards. Pure stdlib; safe to run
anywhere.
"""
from __future__ import annotations

import json
import os
import time


class BlackBox:
    def __init__(self, path: str = "blackbox.jsonl", max_bytes: int = 5_000_000,
                 backups: int = 3):
        self.path = path
        self.max_bytes = max_bytes
        self.backups = backups

    def _rotate_if_needed(self) -> None:
        try:
            if os.path.exists(self.path) and os.path.getsize(self.path) >= self.max_bytes:
                for i in range(self.backups - 1, 0, -1):
                    src = f"{self.path}.{i}"
                    dst = f"{self.path}.{i + 1}"
                    if os.path.exists(src):
                        os.replace(src, dst)
                os.replace(self.path, f"{self.path}.1")
        except OSError:
            pass

    def log(self, event_type: str, data: dict) -> None:
        self._rotate_if_needed()
        record = {"t": time.time(), "type": event_type, **data}
        try:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, separators=(",", ":")) + "\n")
        except OSError:
            pass
