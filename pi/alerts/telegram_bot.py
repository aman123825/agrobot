"""Telegram push alerts (BOM #106).

Sends field alerts to the farmer's phone, e.g.:
  "Low nitrogen at Zone 3 (GPS: 18.5N 73.8E)"
  "Moisture critical"
  "Battery 15% - returning to base"
  "Tank empty - refill required"
"""
from __future__ import annotations

import requests

import config


def send_alert(message: str) -> bool:
    """Send a message via the Telegram Bot API. Returns True on success."""
    if not config.TELEGRAM_TOKEN or not config.TELEGRAM_CHAT_ID:
        # No credentials configured - skip silently in dev.
        return False
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        json={"chat_id": config.TELEGRAM_CHAT_ID, "text": message},
        timeout=10,
    )
    return resp.ok


if __name__ == "__main__":
    print("sent" if send_alert("AgriRover test alert") else "not configured")
