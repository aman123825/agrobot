#!/usr/bin/env bash
# Baseline hardening + opt-in reliability sections for the AgriRover Pi.
# Run as root on Raspberry Pi OS (Bookworm). Idempotent — safe to re-run;
# every mutation is echoed before it happens.
#
# Usage:
#   sudo ./harden_pi.sh               # baseline only (firewall, SSH, fail2ban)
#   sudo ./harden_pi.sh --watchdog    # + hardware watchdog (auto-reboot on hang)
#   sudo ./harden_pi.sh --sd-protect  # + SD write reduction (noatime, tmpfs logs,
#                                     #   volatile journald) + OverlayFS guidance
#   sudo ./harden_pi.sh --all         # baseline + watchdog + sd-protect
#
# Implements docs/UPGRADES.md §10 (watchdogs) and the storage-durability
# software measures of docs/farmer-needs-and-durability.md §2.2.
set -euo pipefail

DO_WATCHDOG=0
DO_SDPROTECT=0

usage() {
  sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --watchdog)   DO_WATCHDOG=1 ;;
    --sd-protect) DO_SDPROTECT=1 ;;
    --all)        DO_WATCHDOG=1; DO_SDPROTECT=1 ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "ERROR: unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: run as root (sudo)." >&2
  exit 1
fi

# =========================================================================
# Baseline (always runs) — firewall, SSH, fail2ban, secrets perms
# =========================================================================
echo "=== Baseline hardening ==="

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
[ -f /home/agrobot/agrobot/pi/.env ] && chmod 600 /home/agrobot/agrobot/pi/.env || true
[ -f /etc/agrirover.env ] && chmod 600 /etc/agrirover.env || true

# =========================================================================
# Opt-in: hardware watchdog (--watchdog)  — docs/UPGRADES.md §10
# The BCM SoC watchdog reboots the Pi if the kernel/PID 1 hangs; systemd
# pets it every few seconds while healthy.
# =========================================================================
if [ "$DO_WATCHDOG" -eq 1 ]; then
  echo ""
  echo "=== Opt-in: hardware watchdog ==="

  CONFIG_TXT="/boot/firmware/config.txt"          # Bookworm location
  [ -f "$CONFIG_TXT" ] || CONFIG_TXT="/boot/config.txt"  # older images
  if [ ! -f "$CONFIG_TXT" ]; then
    echo "[!] WARNING: no config.txt found — skipping dtparam (not a Pi?)"
  elif grep -q '^dtparam=watchdog=on' "$CONFIG_TXT"; then
    echo "[*] $CONFIG_TXT: dtparam=watchdog=on already present"
  else
    echo "[*] Enabling BCM hardware watchdog in $CONFIG_TXT"
    printf '\n# AgriRover: hardware watchdog (harden_pi.sh --watchdog)\ndtparam=watchdog=on\n' >> "$CONFIG_TXT"
  fi

  echo "[*] Writing /etc/systemd/system.conf.d/10-watchdog.conf"
  mkdir -p /etc/systemd/system.conf.d
  cat > /etc/systemd/system.conf.d/10-watchdog.conf <<'EOF'
# AgriRover (harden_pi.sh --watchdog): systemd pets the BCM watchdog; if
# PID 1 stops responding for >15 s the SoC hard-resets the board. A hung
# reboot is itself bounded by RebootWatchdogSec.
[Manager]
RuntimeWatchdogSec=15
RebootWatchdogSec=2min
EOF

  echo "[*] Re-executing systemd to pick up watchdog settings"
  systemctl daemon-reexec || true
  echo "[*] NOTE: dtparam takes effect on next reboot."
fi

# =========================================================================
# Opt-in: SD-card protection (--sd-protect)
# docs/farmer-needs-and-durability.md §2.2 — SD corruption is the #1 field
# killer. Cut routine writes: noatime, volatile journald, tmpfs /var/log.
# =========================================================================
if [ "$DO_SDPROTECT" -eq 1 ]; then
  echo ""
  echo "=== Opt-in: SD-card protection (farmer-needs-and-durability.md §2.2) ==="

  # -- 1. noatime on the root filesystem -----------------------------------
  if grep -E '^[^#[:space:]][^[:space:]]*[[:space:]]+/[[:space:]]' /etc/fstab | grep -q 'noatime'; then
    echo "[*] /etc/fstab: rootfs already mounted with noatime"
  else
    echo "[*] /etc/fstab: adding noatime to rootfs mount options"
    sed -i -E 's|^([^#[:space:]][^[:space:]]*[[:space:]]+/[[:space:]]+[^[:space:]]+[[:space:]]+)([^[:space:]]+)|\1noatime,\2|' /etc/fstab
  fi

  # -- 2. journald: RAM-only, bounded --------------------------------------
  echo "[*] journald: Storage=volatile, SystemMaxUse=32M (RAM-only logs)"
  mkdir -p /etc/systemd/journald.conf.d
  cat > /etc/systemd/journald.conf.d/10-agrirover-volatile.conf <<'EOF'
# AgriRover (harden_pi.sh --sd-protect): keep the journal in RAM only so
# routine logging never wears the SD card. Bounded so it cannot eat memory.
[Journal]
Storage=volatile
SystemMaxUse=32M
RuntimeMaxUse=32M
EOF
  systemctl restart systemd-journald || true

  # -- 3. /var/log on tmpfs -------------------------------------------------
  if grep -qE '^[[:space:]]*tmpfs[[:space:]]+/var/log[[:space:]]' /etc/fstab; then
    echo "[*] /etc/fstab: /var/log tmpfs entry already present"
  else
    echo "[*] /etc/fstab: mounting /var/log as tmpfs (64 MB, lost on reboot — by design)"
    echo 'tmpfs /var/log tmpfs defaults,noatime,nosuid,nodev,size=64m,mode=0755 0 0' >> /etc/fstab
  fi

  echo "[*] tmpfiles.d: recreate daemon log dirs inside tmpfs at every boot"
  cat > /etc/tmpfiles.d/agrirover-varlog.conf <<'EOF'
# AgriRover (harden_pi.sh --sd-protect): /var/log is tmpfs, so directories
# daemons expect must be recreated each boot.
d /var/log/mosquitto 0755 mosquitto mosquitto -
d /var/log/fail2ban  0755 root      root      -
EOF

  # -- 4. OverlayFS read-only root: PRINTED, not executed -------------------
  cat <<'OVERLAY'

[note] Full read-only root via OverlayFS — NOT applied automatically.
  This is the strongest SD protection (power cuts cannot corrupt a
  filesystem nobody writes to), but it changes the update workflow, so
  enable it manually once the rover is provisioned and stable:

      sudo raspi-config nonint do_overlayfs 0    # enable overlay (and boot RO)
      sudo reboot

  To make changes later (OS updates, model OTA, config edits), disable first:

      sudo raspi-config nonint do_overlayfs 1    # disable overlay
      sudo reboot
      # ...make changes... then re-enable and reboot again.

  WARNING: with OverlayFS on, ALL writes — captures/ (active-learning
  frames), model OTA downloads, plant_db.json, mosquitto persistence —
  land in RAM and VANISH on reboot. Before enabling, mount a writable
  data partition (second SD partition or a USB stick, e.g. at /data) and
  point CAPTURE_DIR / MODEL_DIR / PLANT_DB_PATH there via
  /etc/agrirover.env. See deploy/README.md.
OVERLAY

  echo "[*] SD-protect changes take full effect after a reboot."
fi

# =========================================================================
cat <<'NOTE'

[done] Hardening applied. Still recommended, manually:
  - Run AgriRover services as a non-root, least-privilege user via systemd
    (deploy/install_services.sh units run as user 'agrobot').
  - Use an industrial pSLC microSD (or SSD/NVMe boot) — see
    docs/farmer-needs-and-durability.md §2.2.
  - Enable OverlayFS read-only root once stable (instructions above,
    with --sd-protect).
  - Rotate AGRO_LINK_KEY and MQTT credentials periodically.
  - Keep the rover on an isolated WiFi VLAN/SSID, not the main network.
NOTE
