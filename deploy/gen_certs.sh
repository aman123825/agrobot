#!/usr/bin/env bash
# AgriRover: generate a self-signed CA + Mosquitto broker server certificate
# and create the broker's password-file entry. Run as root ON THE PI, after
# `apt install mosquitto` (needed for mosquitto_passwd and the mosquitto user).
#
# Usage:
#   sudo ./gen_certs.sh                  # CA (10 y) + server cert (2 y) + passwd entry
#   sudo ./gen_certs.sh --host rover01   # override SAN hostname (default: $(hostname))
#   sudo ./gen_certs.sh --user agrorover # override broker username
#   sudo ./gen_certs.sh --force          # regenerate even if a CA already exists
#
# Idempotent: refuses to clobber an existing CA/server cert without --force.
# Non-interactive password: export MQTT_PASSWORD=... before running.
#
# Implements SECURITY.md ("Hijack MQTT" row) and docs/UPGRADES.md §10
# "Enable MQTT TLS + auth in deployment".
set -euo pipefail

CERT_DIR="${CERT_DIR:-/etc/mosquitto/certs}"
PASSWD_FILE="${PASSWD_FILE:-/etc/mosquitto/passwd}"
ROVER_HOST="${ROVER_HOST:-$(hostname)}"
MQTT_USER="${MQTT_USER:-agrorover}"
CA_DAYS=3650   # 10-year CA
SRV_DAYS=730   # 2-year server cert
FORCE=0

usage() {
  sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --force) FORCE=1 ;;
    --host)  ROVER_HOST="${2:?--host needs a value}"; shift ;;
    --user)  MQTT_USER="${2:?--user needs a value}"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: run as root (sudo)." >&2
  exit 1
fi
command -v openssl >/dev/null || { echo "ERROR: openssl not found." >&2; exit 1; }
command -v mosquitto_passwd >/dev/null || {
  echo "ERROR: mosquitto_passwd not found (apt install mosquitto)." >&2; exit 1
}

CA_KEY="$CERT_DIR/ca.key"
CA_CRT="$CERT_DIR/ca.crt"
SRV_KEY="$CERT_DIR/server.key"
SRV_CSR="$CERT_DIR/server.csr"
SRV_CRT="$CERT_DIR/server.crt"

mkdir -p "$CERT_DIR"
chmod 755 "$CERT_DIR"

# --- CA -----------------------------------------------------------------
if [ -f "$CA_CRT" ] && [ "$FORCE" -ne 1 ]; then
  echo "[*] CA already exists at $CA_CRT — keeping it (use --force to regenerate)."
else
  echo "[*] Generating CA key + self-signed CA cert (valid $CA_DAYS days)"
  openssl genrsa -out "$CA_KEY" 4096
  openssl req -x509 -new -key "$CA_KEY" -sha256 -days "$CA_DAYS" \
    -subj "/CN=AgriRover-CA/O=AgriRover" -out "$CA_CRT"
  # New CA invalidates any old server cert — force a re-issue below.
  rm -f "$SRV_CRT"
fi

# --- Broker server cert (SAN: localhost + rover hostname) ---------------
if [ -f "$SRV_CRT" ] && [ "$FORCE" -ne 1 ]; then
  echo "[*] Server cert already exists at $SRV_CRT — keeping it (use --force)."
else
  echo "[*] Generating server cert for SAN: localhost, $ROVER_HOST (valid $SRV_DAYS days)"
  openssl genrsa -out "$SRV_KEY" 2048
  openssl req -new -key "$SRV_KEY" -subj "/CN=$ROVER_HOST" -out "$SRV_CSR"
  SAN_FILE="$(mktemp)"
  printf 'subjectAltName = DNS:localhost, DNS:%s, IP:127.0.0.1\n' "$ROVER_HOST" > "$SAN_FILE"
  openssl x509 -req -in "$SRV_CSR" -CA "$CA_CRT" -CAkey "$CA_KEY" -CAcreateserial \
    -sha256 -days "$SRV_DAYS" -extfile "$SAN_FILE" -out "$SRV_CRT"
  rm -f "$SAN_FILE" "$SRV_CSR"
fi

# --- Ownership / permissions --------------------------------------------
echo "[*] Setting ownership and permissions"
chown root:root "$CA_KEY"
chmod 600 "$CA_KEY"                # CA key: root only — sign certs as root
chmod 644 "$CA_CRT" "$SRV_CRT"     # public certs: world-readable (clients pin ca.crt)
if id mosquitto >/dev/null 2>&1; then
  chown mosquitto:mosquitto "$SRV_KEY"
else
  echo "[!] WARNING: no 'mosquitto' user yet — re-run after installing mosquitto,"
  echo "    or chown $SRV_KEY to the broker user manually."
fi
chmod 600 "$SRV_KEY"

# --- Broker password entry ----------------------------------------------
PASSWD_CREATE_FLAG=""
[ -f "$PASSWD_FILE" ] || PASSWD_CREATE_FLAG="-c"
if [ -n "${MQTT_PASSWORD:-}" ]; then
  echo "[*] Writing password entry for '$MQTT_USER' (from \$MQTT_PASSWORD)"
  mosquitto_passwd $PASSWD_CREATE_FLAG -b "$PASSWD_FILE" "$MQTT_USER" "$MQTT_PASSWORD"
else
  echo "[*] Enter a password for broker user '$MQTT_USER':"
  mosquitto_passwd $PASSWD_CREATE_FLAG "$PASSWD_FILE" "$MQTT_USER"
fi
if id mosquitto >/dev/null 2>&1; then
  chown mosquitto:mosquitto "$PASSWD_FILE"
fi
chmod 600 "$PASSWD_FILE"

# --- Done ----------------------------------------------------------------
cat <<EOF

[done] Certs in $CERT_DIR, password entry for '$MQTT_USER' in $PASSWD_FILE.

Next steps:
  1. Install the broker config + ACL, then restart:
       sudo cp deploy/mosquitto.conf /etc/mosquitto/conf.d/agrirover.conf
       sudo cp deploy/acl /etc/mosquitto/acl
       sudo systemctl restart mosquitto
  2. Add a read-only dashboard user too (matches deploy/acl):
       sudo mosquitto_passwd $PASSWD_FILE dashboard
  3. Put this exact block in /etc/agrirover.env (chmod 600) — these are the
     env-var names pi/config.py reads and the systemd units load:

MQTT_TLS=1
MQTT_HOST=localhost
MQTT_PORT=8883
MQTT_CA_CERT=$CERT_DIR/ca.crt
MQTT_USERNAME=$MQTT_USER
MQTT_PASSWORD=${MQTT_PASSWORD:-<the password you just typed>}

EOF
