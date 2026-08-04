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

# Canonical env-var home for all agrobot-* units (EnvironmentFile=-/etc/agrirover.env).
# Names match pi/config.py exactly. Created only if missing — never overwritten.
if [ ! -f /etc/agrirover.env ]; then
  echo "[*] Creating /etc/agrirover.env template (FILL IN the blanks, keep chmod 600) ..."
  cat > /etc/agrirover.env <<'EOF'
# AgriRover canonical environment — loaded by every agrobot-* systemd unit.
# Values here override pi/.env. Keep this file chmod 600, never commit it.
# MQTT (certs + password from deploy/gen_certs.sh):
MQTT_TLS=1
MQTT_HOST=localhost
MQTT_PORT=8883
MQTT_CA_CERT=/etc/mosquitto/certs/ca.crt
MQTT_USERNAME=agrorover
MQTT_PASSWORD=
ROVER_ID=rover01
# Pi->ESP32 HMAC link key (SECURITY.md: openssl rand -hex 32):
#AGRO_LINK_KEY=
# Telegram alerts (optional) + two-way control allowlist (empty = disabled):
#TELEGRAM_TOKEN=
#TELEGRAM_CHAT_ID=
#TELEGRAM_ALLOWED_CHAT_IDS=
# Model OTA manifest URL (docs/UPGRADES.md §8; unset = OTA disabled):
#MODEL_MANIFEST_URL=https://github.com/<owner>/<repo>/releases/latest/download/model_manifest.json
EOF
  chmod 600 /etc/agrirover.env
else
  echo "[*] /etc/agrirover.env already exists — leaving it untouched."
  chmod 600 /etc/agrirover.env
fi

echo "[*] Copying service units to /etc/systemd/system/ ..."
cp "$UNIT_DIR/agrobot-orchestrator.service" /etc/systemd/system/
cp "$UNIT_DIR/agrobot-pipeline.service" /etc/systemd/system/
cp "$UNIT_DIR/agrobot-dashboard.service" /etc/systemd/system/
cp "$UNIT_DIR/agrobot-model-ota.service" /etc/systemd/system/
cp "$UNIT_DIR/agrobot-model-ota.timer" /etc/systemd/system/

echo "[*] Reloading systemd daemon ..."
systemctl daemon-reload

echo "[*] Enabling services ..."
systemctl enable agrobot-orchestrator.service
systemctl enable agrobot-pipeline.service
systemctl enable agrobot-dashboard.service
# Weekly model OTA check (no-op until MODEL_MANIFEST_URL is set in
# /etc/agrirover.env — see deploy/README.md "Model OTA").
systemctl enable --now agrobot-model-ota.timer

echo "[*] Current status:"
systemctl status agrobot-orchestrator.service --no-pager || true
systemctl status agrobot-pipeline.service --no-pager || true
systemctl status agrobot-dashboard.service --no-pager || true

echo "[done] Services installed and enabled. They will start automatically on next boot."
echo "       To start them now:  sudo systemctl start agrobot-orchestrator agrobot-pipeline agrobot-dashboard"
