# AgriRover Security

## Honest disclaimer

No connected device is "impossible to hack" — especially a robot an attacker can
physically touch. The goal here is **defense-in-depth**: authenticate and encrypt
every channel, keep secrets off the device and out of git, and make every
realistic attack require secrets the attacker does not have. This stops casual
and remote attackers outright and forces a determined attacker into difficult,
physical, well-resourced attacks.

## Threat model & mitigations

| Attack | Mitigation | Where |
|--------|------------|-------|
| Spoof / replay drive or dosing commands on the Pi↔ESP32 UART | HMAC-SHA256 signed envelopes + strictly-increasing, NVS-persisted anti-replay counter; fail-closed; lockout after repeated bad signatures + tamper alert | `firmware/src/secure_link.cpp`, `pi/security.py` |
| Hijack MQTT (inject commands / read telemetry) | Username/password auth, TLS (`:8883`) with pinned CA, topic ACLs, no anonymous, no plaintext listener | `firmware/src/comms.cpp`, `pi/bridge/mqtt_client.py`, `deploy/mosquitto.conf`, `deploy/acl` |
| Secrets leaked via source control | `secrets.h` / `.env` are gitignored; only `*.example` templates are committed | `.gitignore`, `*.example.*` |
| Firmware / key extraction from the chip | ESP32 **Flash Encryption** + **Secure Boot v2** (see below) | ops step |
| Pi compromise (SSH, exposed services) | key-only SSH, UFW firewall (LAN-scoped), fail2ban, least privilege, read-only root | `deploy/harden_pi.sh` |
| LoRa sniffing / spoofing | encrypt + authenticate payloads (AES-CCM / AES-CTR + HMAC) before transmit | guidance below |
| Physical emergency takeover | hardware E-stop on the ESP32 EN pin halts everything regardless of software | circuit §8 |

## Command link protocol (Pi → ESP32)

Envelope: `v1|<counter>|<command>|<hmac_hex>`

- `hmac = HMAC-SHA256(KEY, "v1|<counter>|<command>")`, truncated to 16 bytes (32 hex chars).
- `KEY` is a 32+ byte random shared secret: firmware `COMMAND_HMAC_KEY` == Pi `AGRO_LINK_KEY`.
- The ESP32 rejects any message whose `counter` is not strictly greater than the
  last accepted value (persisted in NVS), defeating replay even across reboots.
- After `CMD_FAIL_LOCK_THRESHOLD` bad signatures the link locks out for a cooldown
  and publishes a `tamper` alert.

Generate the key once and put it in **both** places (never commit it):

```bash
openssl rand -hex 32
```

## ESP32 firmware/key protection (do this for production)

Flash Encryption + Secure Boot make it infeasible to read firmware or secrets
off the device or to flash unsigned firmware. In `platformio.ini` / menuconfig:

- Enable **Secure Boot v2** (signed bootloader + app).
- Enable **Flash Encryption** in *release* mode (not development mode).
- Disable UART download mode (eFuse) once provisioned.

> These are one-way eFuse operations — read Espressif's docs and test on a
> sacrificial board first. Once burned, you cannot revert.

## Setup checklist

1. `openssl rand -hex 32` → set firmware `COMMAND_HMAC_KEY` and Pi `AGRO_LINK_KEY` to the same value.
2. `cp firmware/include/secrets.example.h firmware/include/secrets.h` and fill in (gitignored).
3. `cp pi/.env.example pi/.env`, fill in, `chmod 600 pi/.env`.
4. Configure the broker: `deploy/mosquitto.conf` + `mosquitto_passwd` + `deploy/acl` + TLS certs.
5. Run `sudo deploy/harden_pi.sh` on the Pi.
6. For production firmware, enable ESP32 Flash Encryption + Secure Boot.
7. Put the rover on an isolated WiFi VLAN/SSID.

## Reporting

Found a vulnerability? Open a private security advisory on the repository rather
than a public issue.
