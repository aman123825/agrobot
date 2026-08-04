"""Model versioning & OTA (docs/UPGRADES.md §8).

Model binaries are gitignored (see `models/README.md`); they are distributed
via GitHub Releases together with a version manifest. On the rover a weekly
systemd timer (`deploy/systemd/agrobot-model-ota.timer`) runs this module as
a oneshot: it downloads the manifest, verifies sha256 + size of EVERY new
file *before* touching the model directory, then swaps the files atomically
(`os.replace`, staged inside the model dir so it is the same filesystem)
under the exact filenames the detectors probe for, keeping a `.bak` of each
replaced file for one generation. Any verification failure aborts the whole
update with the old models untouched.

Release workflow:
  1. retrain / re-export the models into `models/`
  2. `py -3.14 pi/ai/model_ota.py make-manifest --model-dir models \
         --version v2026.07.31 \
         --base-url https://github.com/<owner>/<repo>/releases/download/v2026.07.31`
  3. create GitHub Release `v2026.07.31`; upload the model/label files *and*
     `model_manifest.json` as assets
  4. rovers pull on the timer - set `MODEL_MANIFEST_URL` in
     `/etc/agrirover.env` to the manifest asset URL (unset = graceful no-op),
     or run `py -3.14 pi/ai/model_ota.py update --restart` by hand.

Stdlib only and standalone (env vars read directly with the same defaults as
`pi/config.py`, no `import config`) so it can run as a systemd oneshot
without the package path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import date, datetime, timezone

logger = logging.getLogger(__name__)

MANIFEST_NAME = "model_manifest.json"
STATE_NAME = ".ota_state.json"        # last applied version, lives in MODEL_DIR
MODEL_EXTS = (".tflite", ".txt")      # deployed models + label files
CHECKPOINT_EXTS = (".pt",)            # training checkpoints (opt-in, --include-pt)
RESTART_SERVICES = ("agrobot-orchestrator",)
FETCH_TIMEOUT_S = 30.0


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Manifest creation (run on the training machine before uploading a release)
# --------------------------------------------------------------------------

def make_manifest(model_dir: str, version: str, base_url: str,
                  include_pt: bool = False, notes: str = "") -> dict:
    """Hash every deployable model/label file in *model_dir* into a manifest.

    Includes ``*.tflite`` and ``*.txt`` (labels); ``*.pt`` checkpoints only
    with *include_pt*. README, the manifest itself, state and ``.bak`` files
    are skipped by the extension filter. Writes ``model_manifest.json`` into
    *model_dir* and returns the dict. URLs point at GitHub Release assets:
    ``<base_url>/<name>``.
    """
    exts = MODEL_EXTS + (CHECKPOINT_EXTS if include_pt else ())
    base = base_url.rstrip("/")
    files = []
    for name in sorted(os.listdir(model_dir)):
        path = os.path.join(model_dir, name)
        if not os.path.isfile(path) or not name.lower().endswith(exts):
            continue
        files.append({
            "name": name,
            "sha256": sha256_file(path),
            "size": os.path.getsize(path),
            "url": f"{base}/{name}",
        })
    if not files:
        raise ValueError(f"no model files ({'/'.join(exts)}) in {model_dir!r}")
    manifest = {
        "schema": 1,
        "version": version,
        "released": date.today().isoformat(),
        "files": files,
        "notes": notes,
    }
    out = os.path.join(model_dir, MANIFEST_NAME)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    logger.info("wrote %s (version %s, %d files)", out, version, len(files))
    return manifest


# --------------------------------------------------------------------------
# Updater (runs on the rover via agrobot-model-ota.timer)
# --------------------------------------------------------------------------

def _default_fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=FETCH_TIMEOUT_S) as resp:
        return resp.read()


def _load_state(state_path: str) -> dict:
    try:
        with open(state_path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _write_json_atomic(path: str, payload: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    os.replace(tmp, path)


def _valid_entry(entry: dict) -> bool:
    """Manifest entry sanity: flat filename + 64-hex sha + size + url."""
    name = entry.get("name", "")
    return (bool(name) and "/" not in name and "\\" not in name
            and ".." not in name and not name.startswith(".")
            and isinstance(entry.get("sha256"), str)
            and len(entry["sha256"]) == 64
            and isinstance(entry.get("size"), int) and entry["size"] >= 0
            and bool(entry.get("url")))


def check_and_update(manifest_url: str, model_dir: str | None = None,
                     state_path: str | None = None, fetch=None) -> dict:
    """Pull the manifest, and if its version differs from the last applied
    one, download + verify + atomically install the changed files.

    *fetch* is injectable for tests: ``fetch(url) -> bytes`` (default urllib
    with a ~30 s timeout). Same version as the state file = no-op; any other
    version is authoritative (that is also how a deliberately re-pointed
    older release rolls a fleet back). Files whose local sha256 already
    matches the manifest are not re-downloaded.
    """
    model_dir = model_dir or os.getenv("MODEL_DIR", "models")
    state_path = state_path or os.path.join(model_dir, STATE_NAME)
    fetch = fetch or _default_fetch
    result: dict = {"updated": False, "version": None, "changed": [], "errors": []}

    if not manifest_url:
        logger.info("MODEL_MANIFEST_URL not set - model OTA disabled, nothing to do")
        return result

    try:
        manifest = json.loads(fetch(manifest_url).decode("utf-8"))
    except Exception as exc:  # network / JSON - keep old models, report
        logger.error("manifest fetch failed (%s): %s", manifest_url, exc)
        result["errors"].append(f"manifest fetch failed: {exc}")
        return result

    entries = manifest.get("files")
    version = manifest.get("version")
    if manifest.get("schema") != 1 or not version or not isinstance(entries, list):
        logger.error("bad manifest (schema/version/files): %.200s", manifest)
        result["errors"].append("bad manifest: need schema=1, version, files[]")
        return result
    result["version"] = version
    bad = [e.get("name", "?") for e in entries if not _valid_entry(e)]
    if bad:
        logger.error("manifest has invalid entries: %s", bad)
        result["errors"].append(f"invalid manifest entries: {bad}")
        return result

    if _load_state(state_path).get("version") == version:
        logger.info("models already at %s - nothing to do", version)
        return result

    to_fetch = []
    for entry in entries:
        local = os.path.join(model_dir, entry["name"])
        if os.path.isfile(local) and sha256_file(local) == entry["sha256"]:
            continue  # already have this exact file
        to_fetch.append(entry)

    def _record_state(changed: list[str]) -> None:
        _write_json_atomic(state_path, {
            "version": version,
            "applied": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "changed": changed,
        })

    if not to_fetch:
        logger.info("version %s: all %d files already current - recording state",
                    version, len(entries))
        _record_state([])
        result["updated"] = True
        return result

    logger.info("updating to %s: %d of %d files changed", version,
                len(to_fetch), len(entries))
    os.makedirs(model_dir, exist_ok=True)
    # Stage inside model_dir so os.replace stays on one filesystem (atomic).
    tmp_dir = tempfile.mkdtemp(prefix=".ota_tmp_", dir=model_dir)
    try:
        staged = []
        for entry in to_fetch:
            try:
                blob = fetch(entry["url"])
            except Exception as exc:
                logger.error("download failed for %s (%s) - aborting, old "
                             "models untouched", entry["name"], exc)
                result["errors"].append(f"{entry['name']}: download failed: {exc}")
                return result
            tmp_path = os.path.join(tmp_dir, entry["name"])
            with open(tmp_path, "wb") as fh:
                fh.write(blob)
            staged.append((entry, tmp_path))

        # Verify EVERY file before touching model_dir.
        for entry, tmp_path in staged:
            size = os.path.getsize(tmp_path)
            digest = sha256_file(tmp_path)
            if size != entry["size"] or digest != entry["sha256"]:
                logger.error(
                    "verification failed for %s (size %d vs %d, sha %s.. vs "
                    "%s..) - aborting, old models untouched", entry["name"],
                    size, entry["size"], digest[:12], entry["sha256"][:12])
                result["errors"].append(f"{entry['name']}: sha256/size mismatch")
                return result

        # Atomic swap; keep a .bak of each replaced file for one generation.
        for entry, tmp_path in staged:
            target = os.path.join(model_dir, entry["name"])
            if os.path.isfile(target):
                os.replace(target, target + ".bak")
            os.replace(tmp_path, target)
            result["changed"].append(entry["name"])
            logger.info("installed %s (%d bytes)", entry["name"], entry["size"])

        _record_state(result["changed"])
        result["updated"] = True
        logger.info("model update %s applied (%d files)", version,
                    len(result["changed"]))
        return result
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def rollback(model_dir: str | None = None) -> dict:
    """Restore the previous model generation from the ``.bak`` files.

    Swaps each ``<file>.bak`` back over ``<file>`` (the replaced files become
    the new ``.bak``s, so a second rollback undoes the first). The state file
    keeps the applied version, so the weekly timer will NOT re-download the
    rolled-back release - the rollback sticks until a new version ships.
    """
    model_dir = model_dir or os.getenv("MODEL_DIR", "models")
    restored = []
    for name in sorted(os.listdir(model_dir)):
        if not name.endswith(".bak"):
            continue
        bak = os.path.join(model_dir, name)
        target = bak[:-len(".bak")]
        if os.path.isfile(target):
            tmp = target + ".ota_swap"
            os.replace(target, tmp)
            os.replace(bak, target)
            os.replace(tmp, bak)
        else:
            os.replace(bak, target)
        restored.append(os.path.basename(target))
        logger.info("rolled back %s", os.path.basename(target))
    if restored:
        state_path = os.path.join(model_dir, STATE_NAME)
        state = _load_state(state_path)
        if state:
            state["rolled_back"] = datetime.now(timezone.utc).isoformat(
                timespec="seconds")
            _write_json_atomic(state_path, state)
    else:
        logger.info("no .bak files in %s - nothing to roll back", model_dir)
    return {"restored": restored}


def restart_services(services: tuple[str, ...] = RESTART_SERVICES) -> bool:
    """Restart the detector services so they load the new models.

    Tolerates systemctl being absent (dev laptop) or denied - logs a warning
    and returns False; the new models are then picked up on the next service
    restart/boot.
    """
    ok = True
    for svc in services:
        try:
            proc = subprocess.run(["systemctl", "restart", svc],
                                  capture_output=True, text=True, timeout=60)
            if proc.returncode == 0:
                logger.info("restarted %s", svc)
            else:
                logger.warning("systemctl restart %s failed (rc=%d): %s", svc,
                               proc.returncode, (proc.stderr or "").strip())
                ok = False
        except (OSError, subprocess.SubprocessError) as exc:
            logger.warning("systemctl unavailable (%s) - %s not restarted; "
                           "new models load on next service start", exc, svc)
            ok = False
    return ok


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(
        description="Model versioning & OTA (docs/UPGRADES.md §8)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("make-manifest",
                       help="hash model_dir into model_manifest.json "
                            "(run before uploading a GitHub Release)")
    p.add_argument("--model-dir", default=os.getenv("MODEL_DIR", "models"))
    p.add_argument("--version", required=True,
                   help="release tag, e.g. v2026.07.31")
    p.add_argument("--base-url", required=True,
                   help="GitHub Release asset base, e.g. https://github.com/"
                        "<owner>/<repo>/releases/download/v2026.07.31")
    p.add_argument("--include-pt", action="store_true",
                   help="also ship *.pt training checkpoints")
    p.add_argument("--notes", default="", help="free-text release notes")

    p = sub.add_parser("update",
                       help="pull manifest, verify and atomically apply new models")
    p.add_argument("--manifest-url", default=os.getenv("MODEL_MANIFEST_URL", ""))
    p.add_argument("--model-dir", default=os.getenv("MODEL_DIR", "models"))
    p.add_argument("--restart", action="store_true",
                   help="restart agrobot-orchestrator after a successful swap")

    p = sub.add_parser("rollback",
                       help="restore the previous model generation from .bak files")
    p.add_argument("--model-dir", default=os.getenv("MODEL_DIR", "models"))

    args = parser.parse_args(argv)

    if args.cmd == "make-manifest":
        try:
            manifest = make_manifest(args.model_dir, args.version,
                                     args.base_url, include_pt=args.include_pt,
                                     notes=args.notes)
        except (OSError, ValueError) as exc:
            logger.error("make-manifest failed: %s", exc)
            return 1
        print(json.dumps(manifest, indent=2))
        return 0

    if args.cmd == "update":
        result = check_and_update(args.manifest_url, args.model_dir)
        print(json.dumps(result))
        if result["errors"]:
            return 1
        if args.restart and result["updated"] and result["changed"]:
            restart_services()
        return 0

    # rollback
    result = rollback(args.model_dir)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
