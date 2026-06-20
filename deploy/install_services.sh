#!/bin/bash
# Install AgriRover systemd service units and enable auto-start on boot.
# Must be run with sudo.
set -euo pipefail

if [ "$EUID" -ne 0 ]; then
  echo "ERROR: This script must be run as root (use sudo)." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_DIR="$SCRIPT_DIR/systemd"

echo "[*] Copying service units to /etc/systemd/system/ ..."
cp "$UNIT_DIR/agrobot-orchestrator.service" /etc/systemd/system/
cp "$UNIT_DIR/agrobot-pipeline.service" /etc/systemd/system/
cp "$UNIT_DIR/agrobot-dashboard.service" /etc/systemd/system/

echo "[*] Reloading systemd daemon ..."
systemctl daemon-reload

echo "[*] Enabling services ..."
systemctl enable agrobot-orchestrator.service
systemctl enable agrobot-pipeline.service
systemctl enable agrobot-dashboard.service

echo "[*] Current status:"
systemctl status agrobot-orchestrator.service --no-pager || true
systemctl status agrobot-pipeline.service --no-pager || true
systemctl status agrobot-dashboard.service --no-pager || true

echo "[done] Services installed and enabled. They will start automatically on next boot."
echo "       To start them now:  sudo systemctl start agrobot-orchestrator agrobot-pipeline agrobot-dashboard"
