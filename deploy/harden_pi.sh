#!/usr/bin/env bash
# Baseline hardening for the AgriRover Raspberry Pi. Review before running.
# Run as root on Raspberry Pi OS (Bookworm). Idempotent where practical.
set -euo pipefail

echo "[*] Updating packages"
apt-get update && apt-get -y upgrade

echo "[*] Installing firewall + intrusion tooling"
apt-get -y install ufw fail2ban

echo "[*] Firewall: deny inbound by default, allow SSH + MQTT-TLS from LAN only"
ufw default deny incoming
ufw default allow outgoing
ufw allow from 192.168.0.0/16 to any port 22 proto tcp
ufw allow from 192.168.0.0/16 to any port 8883 proto tcp
ufw --force enable

echo "[*] SSH: disable password + root login (key-based only)"
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh || systemctl restart sshd || true

echo "[*] Enable fail2ban for sshd"
systemctl enable --now fail2ban

echo "[*] Lock down secrets files if present"
[ -f /home/pi/agrobot/pi/.env ] && chmod 600 /home/pi/agrobot/pi/.env || true

cat <<'NOTE'
[done] Baseline hardening applied. Still recommended, manually:
  - Run AgriRover services as a non-root, least-privilege user via systemd.
  - Enable full-disk / overlay read-only root (raspi-config) so a stolen SD
    card yields no writable secrets.
  - Rotate AGRO_LINK_KEY and MQTT credentials periodically.
  - Keep the rover on an isolated WiFi VLAN/SSID, not the main network.
NOTE
