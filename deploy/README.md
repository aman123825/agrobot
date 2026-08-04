# AgriRover Deployment (Raspberry Pi OS Bookworm)

End-to-end bring-up of a field rover Pi: MQTT TLS + auth, systemd services
that never give up, hardware watchdog, and SD-card protection. Implements
`docs/UPGRADES.md` §10 and `docs/farmer-needs-and-durability.md` §2.2;
security rationale in `SECURITY.md`.

## Fresh-Pi checklist (in order)

1. **Flash** Raspberry Pi OS (Bookworm) — prefer an **industrial pSLC microSD**
   (durability doc §2.2). Create user `agrobot`, enable SSH with a key.
2. **Clone + venv**
   ```bash
   git clone <repo> /home/agrobot/agrobot
   python3 -m venv /home/agrobot/agrobot/pi/.venv
   /home/agrobot/agrobot/pi/.venv/bin/pip install -r /home/agrobot/agrobot/pi/requirements.txt
   ```
3. **Harden the OS** (baseline always; watchdog + SD protection are opt-in flags)
   ```bash
   sudo /home/agrobot/agrobot/deploy/harden_pi.sh --all
   ```
   Flags: `--watchdog` (BCM hardware watchdog + systemd RuntimeWatchdogSec=15),
   `--sd-protect` (rootfs noatime, journald volatile, tmpfs /var/log, prints
   OverlayFS instructions). Safe to re-run.
4. **Broker + certs + credentials**
   ```bash
   sudo apt install -y mosquitto mosquitto-clients
   sudo /home/agrobot/agrobot/deploy/gen_certs.sh          # CA 10y, server 2y, passwd entry
   sudo mosquitto_passwd /etc/mosquitto/passwd dashboard   # read-only user (deploy/acl)
   sudo cp /home/agrobot/agrobot/deploy/mosquitto.conf /etc/mosquitto/conf.d/agrirover.conf
   sudo cp /home/agrobot/agrobot/deploy/acl /etc/mosquitto/acl
   sudo systemctl restart mosquitto
   ```
5. **Fill `/etc/agrirover.env`** (created as a template by `install_services.sh`
   if missing; `gen_certs.sh` prints the exact MQTT block). Keep `chmod 600`.
6. **Install services**
   ```bash
   sudo /home/agrobot/agrobot/deploy/install_services.sh
   sudo systemctl start agrobot-orchestrator agrobot-pipeline agrobot-dashboard
   ```
7. **Verify over TLS** (subscribe as `dashboard`; `agrorover` is write-only per ACL)
   ```bash
   mosquitto_sub -h localhost -p 8883 --cafile /etc/mosquitto/certs/ca.crt \
     -u dashboard -P '<dashboard password>' -t 'rover/#' -v
   # in another shell, prove auth+TLS+ACL end-to-end:
   mosquitto_pub -h localhost -p 8883 --cafile /etc/mosquitto/certs/ca.crt \
     -u agrorover -P '<agrorover password>' -t rover/rover01/status -m '{"ok":1}'
   # anonymous must FAIL:
   mosquitto_sub -h localhost -p 8883 --cafile /etc/mosquitto/certs/ca.crt -t 'rover/#'
   ```
8. **Reboot once** and confirm everything comes back:
   `systemctl status agrobot-* mosquitto` and `mount | grep -E '/var/log| / '`.
9. **(Later, once stable)** enable OverlayFS read-only root — instructions are
   printed by `harden_pi.sh --sd-protect`. First mount a writable data
   partition (e.g. `/data`) and point `CAPTURE_DIR` / `MODEL_DIR` /
   `PLANT_DB_PATH` at it in `/etc/agrirover.env`, or captures and model OTA
   land in RAM and vanish on reboot.

## Broker layout

- `:8883` TLS + user/password + ACL — anything off the Pi (LAN-scoped by ufw).
- `:1883` bound to `127.0.0.1` only — on-Pi services; auth still required.
- `allow_anonymous false` globally; topic ACL in `deploy/acl`
  (`agrorover` write-only telemetry, `dashboard` read-only).
- Client side (`pi/config.py`): `MQTT_TLS=1`, `MQTT_PORT=8883`,
  `MQTT_CA_CERT=/etc/mosquitto/certs/ca.crt`, `MQTT_USERNAME`, `MQTT_PASSWORD`.

## Field recovery (how the rover self-heals)

Per `docs/farmer-needs-and-durability.md` §2.2 — SD corruption and hangs are
what actually kill field electronics; each layer below covers one:

- **Process crash** → systemd `Restart=always`, `RestartSec=5`,
  `StartLimitIntervalSec=0`: retries every 5 s forever, never gives up.
- **Broker down** → orchestrator orders `After=mosquitto.service` and the MQTT
  client auto-reconnects; mosquitto itself is restarted by systemd.
- **Kernel / PID-1 hang** → BCM hardware watchdog (`--watchdog`): no pet for
  15 s ⇒ SoC hard-reset; a hung shutdown is bounded by `RebootWatchdogSec=2min`.
- **Power cut mid-write** → `--sd-protect` keeps routine writes off the card
  (noatime, volatile journal, tmpfs `/var/log`, hourly mosquitto autosave);
  with OverlayFS enabled the rootfs is read-only, so a yanked battery cannot
  corrupt it — the Pi just boots clean again.
- **Card death anyway** → carry a flashed spare SD (spares-kit line, §2.2);
  secrets live in `/etc/agrirover.env` + `/etc/mosquitto/`, so re-provision is
  those two paths plus this checklist from step 4.

## Model OTA (docs/UPGRADES.md §8)

Model binaries are gitignored; rovers pull them from GitHub Releases on a
weekly timer (`agrobot-model-ota.timer`, Sun ~03:17 + up to 1 h random delay,
`Persistent=true` so a powered-off rover catches up).

Release workflow (on the dev machine, after retraining):

```bash
py -3.14 pi/ai/model_ota.py make-manifest --model-dir models \
  --version v2026.07.31 \
  --base-url https://github.com/<owner>/<repo>/releases/download/v2026.07.31
# -> writes models/model_manifest.json
# create GitHub Release v2026.07.31; upload the model/label files AND the manifest
```

Rover side: set in `/etc/agrirover.env`

```
MODEL_MANIFEST_URL=https://github.com/<owner>/<repo>/releases/latest/download/model_manifest.json
```

Unset URL = the oneshot logs "OTA disabled" and exits 0, so the timer is safe
to leave enabled on every rover. The updater verifies sha256 + size of every
file **before** touching `models/`, swaps atomically with `os.replace`, keeps
the previous generation as `.bak` (`py pi/ai/model_ota.py rollback` restores
it), and `--restart` bounces `agrobot-orchestrator` so the detectors reload.

Manual test: `sudo systemctl start agrobot-model-ota.service` then
`journalctl -u agrobot-model-ota -n 20`.

Note for `--restart` under user `agrobot`: allow the single command via
sudoers (`agrobot ALL=NOPASSWD: /usr/bin/systemctl restart agrobot-orchestrator`)
or a polkit rule; otherwise the swap still succeeds and the new models load on
the next natural restart.
