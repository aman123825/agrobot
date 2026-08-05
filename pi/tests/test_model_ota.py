"""Tests for the model OTA updater (docs/UPGRADES.md §8) - all offline."""
import hashlib
import json
import os
import shutil
import subprocess

import pytest

from ai import model_ota
from ai.model_ota import (STATE_NAME, check_and_update, make_manifest,
                          rollback)

MANIFEST_URL = "https://example.test/releases/model_manifest.json"
BASE_URL = "https://github.com/acme/agrobot/releases/download/v2"

V1_FILES = {
    "disease_model_quant.tflite": b"disease-v1-weights",
    "weed_model_quant_edgetpu.tflite": b"weed-v1-weights",
    "weed_labels.txt": b"crop\nweed\n",
}
V2_FILES = {
    "disease_model_quant.tflite": b"disease-v2-weights-better",
    "weed_model_quant_edgetpu.tflite": b"weed-v2-weights-better",
    "weed_labels.txt": b"crop\nweed\n",  # labels unchanged between releases
}


def write_files(d, files):
    d.mkdir(parents=True, exist_ok=True)
    for name, blob in files.items():
        (d / name).write_bytes(blob)


def release(tmp_path, files, version):
    """Build a fake GitHub Release: manifest + injectable fetch + call log."""
    remote = tmp_path / f"release_{version}"
    write_files(remote, files)
    manifest = make_manifest(str(remote), version, BASE_URL)
    calls = []

    def fetch(url):
        calls.append(url)
        if url == MANIFEST_URL:
            return json.dumps(manifest).encode("utf-8")
        return (remote / url.rsplit("/", 1)[1]).read_bytes()

    return manifest, fetch, calls


class TestMakeManifest:
    def test_hashes_sizes_urls(self, tmp_path):
        d = tmp_path / "models"
        write_files(d, V1_FILES)
        (d / "README.md").write_text("docs, never shipped")
        (d / "weed_best.pt").write_bytes(b"checkpoint")

        manifest = make_manifest(str(d), "v1", BASE_URL + "/")
        assert manifest["schema"] == 1 and manifest["version"] == "v1"
        assert [f["name"] for f in manifest["files"]] == sorted(V1_FILES)
        for entry in manifest["files"]:
            blob = V1_FILES[entry["name"]]
            assert entry["sha256"] == hashlib.sha256(blob).hexdigest()
            assert entry["size"] == len(blob)
            assert entry["url"] == f"{BASE_URL}/{entry['name']}"
        # written into model_dir for uploading alongside the models
        on_disk = json.loads((d / "model_manifest.json").read_text())
        assert on_disk == manifest

    def test_include_pt_flag(self, tmp_path):
        d = tmp_path / "models"
        write_files(d, V1_FILES)
        (d / "weed_best.pt").write_bytes(b"checkpoint")
        names = [f["name"] for f in
                 make_manifest(str(d), "v1", BASE_URL, include_pt=True)["files"]]
        assert "weed_best.pt" in names

    def test_does_not_include_itself_or_bak(self, tmp_path):
        d = tmp_path / "models"
        write_files(d, V1_FILES)
        (d / "weed_labels.txt.bak").write_bytes(b"old")
        make_manifest(str(d), "v1", BASE_URL)   # writes model_manifest.json
        names = [f["name"] for f in make_manifest(str(d), "v2", BASE_URL)["files"]]
        assert "model_manifest.json" not in names
        assert "weed_labels.txt.bak" not in names

    def test_empty_dir_raises(self, tmp_path):
        d = tmp_path / "models"
        d.mkdir()
        with pytest.raises(ValueError):
            make_manifest(str(d), "v1", BASE_URL)


class TestUpdate:
    def test_applies_new_version(self, tmp_path):
        local = tmp_path / "models"
        write_files(local, V1_FILES)
        _, fetch, _ = release(tmp_path, V2_FILES, "v2")

        res = check_and_update(MANIFEST_URL, str(local), fetch=fetch)
        assert res["updated"] is True and res["errors"] == []
        assert res["version"] == "v2"
        assert sorted(res["changed"]) == ["disease_model_quant.tflite",
                                          "weed_model_quant_edgetpu.tflite"]
        # files swapped under the exact detector filenames
        for name, blob in V2_FILES.items():
            assert (local / name).read_bytes() == blob
        # one .bak generation of each replaced file
        for name in res["changed"]:
            assert (local / (name + ".bak")).read_bytes() == V1_FILES[name]
        # state file records the applied version
        state = json.loads((local / STATE_NAME).read_text())
        assert state["version"] == "v2"
        assert sorted(state["changed"]) == sorted(res["changed"])

    def test_corrupted_download_aborts_untouched(self, tmp_path):
        local = tmp_path / "models"
        write_files(local, V1_FILES)
        _, good_fetch, _ = release(tmp_path, V2_FILES, "v2")

        def bad_fetch(url):
            blob = good_fetch(url)
            if url.endswith("weed_model_quant_edgetpu.tflite"):
                return b"garbage-not-the-model"
            return blob

        res = check_and_update(MANIFEST_URL, str(local), fetch=bad_fetch)
        assert res["updated"] is False and res["changed"] == []
        assert any("mismatch" in e for e in res["errors"])
        # model_dir completely untouched: old contents, no .bak, no state
        for name, blob in V1_FILES.items():
            assert (local / name).read_bytes() == blob
        assert not list(local.glob("*.bak"))
        assert not (local / STATE_NAME).exists()
        assert not list(local.glob(".ota_tmp_*"))  # staging cleaned up

    def test_same_version_is_noop(self, tmp_path):
        local = tmp_path / "models"
        write_files(local, V1_FILES)
        _, fetch, calls = release(tmp_path, V2_FILES, "v2")
        assert check_and_update(MANIFEST_URL, str(local), fetch=fetch)["updated"]

        calls.clear()
        res = check_and_update(MANIFEST_URL, str(local), fetch=fetch)
        assert res["updated"] is False and res["changed"] == []
        assert res["errors"] == []
        assert calls == [MANIFEST_URL]  # only the manifest, no file downloads

    def test_partial_change_downloads_only_changed(self, tmp_path):
        local = tmp_path / "models"
        write_files(local, V1_FILES)
        v2 = dict(V1_FILES)
        v2["weed_model_quant_edgetpu.tflite"] = b"weed-v2-only-this-changed"
        _, fetch, calls = release(tmp_path, v2, "v2")

        res = check_and_update(MANIFEST_URL, str(local), fetch=fetch)
        assert res["updated"] is True
        assert res["changed"] == ["weed_model_quant_edgetpu.tflite"]
        assert calls == [MANIFEST_URL,
                         f"{BASE_URL}/weed_model_quant_edgetpu.tflite"]
        # unchanged files untouched (no .bak), changed file swapped with .bak
        assert not (local / "disease_model_quant.tflite.bak").exists()
        assert (local / "weed_model_quant_edgetpu.tflite").read_bytes() == \
            v2["weed_model_quant_edgetpu.tflite"]
        assert (local / "weed_model_quant_edgetpu.tflite.bak").read_bytes() == \
            V1_FILES["weed_model_quant_edgetpu.tflite"]

    def test_version_bump_with_identical_files_records_state(self, tmp_path):
        local = tmp_path / "models"
        write_files(local, V1_FILES)
        _, fetch, _ = release(tmp_path, V1_FILES, "v1.0.1")
        res = check_and_update(MANIFEST_URL, str(local), fetch=fetch)
        assert res["updated"] is True and res["changed"] == []
        assert json.loads((local / STATE_NAME).read_text())["version"] == "v1.0.1"

    def test_manifest_fetch_failure_reports_error(self, tmp_path):
        local = tmp_path / "models"
        write_files(local, V1_FILES)

        def fetch(url):
            raise OSError("no network")

        res = check_and_update(MANIFEST_URL, str(local), fetch=fetch)
        assert res["updated"] is False
        assert any("manifest fetch failed" in e for e in res["errors"])

    def test_missing_manifest_url_is_graceful_noop(self, tmp_path, monkeypatch):
        local = tmp_path / "models"
        write_files(local, V1_FILES)
        res = check_and_update("", str(local))
        assert res == {"updated": False, "version": None,
                       "changed": [], "errors": []}
        # CLI exits 0 so the systemd oneshot never fails on unconfigured rovers
        monkeypatch.delenv("MODEL_MANIFEST_URL", raising=False)
        assert model_ota.main(["update", "--model-dir", str(local)]) == 0


class TestRollback:
    def test_restores_bak_generation(self, tmp_path):
        local = tmp_path / "models"
        write_files(local, V1_FILES)
        _, fetch, _ = release(tmp_path, V2_FILES, "v2")
        changed = check_and_update(MANIFEST_URL, str(local), fetch=fetch)["changed"]

        res = rollback(str(local))
        assert sorted(res["restored"]) == sorted(changed)
        for name in changed:
            assert (local / name).read_bytes() == V1_FILES[name]
            # swap keeps the rolled-back version as the new .bak
            assert (local / (name + ".bak")).read_bytes() == V2_FILES[name]
        # state keeps the version so the timer doesn't re-pull the bad release
        state = json.loads((local / STATE_NAME).read_text())
        assert state["version"] == "v2" and "rolled_back" in state

    def test_nothing_to_roll_back(self, tmp_path):
        local = tmp_path / "models"
        write_files(local, V1_FILES)
        assert rollback(str(local)) == {"restored": []}
        for name, blob in V1_FILES.items():
            assert (local / name).read_bytes() == blob


class TestRestartServices:
    def test_tolerates_missing_systemctl(self, monkeypatch):
        def boom(*a, **k):
            raise FileNotFoundError("systemctl not found")

        monkeypatch.setattr(model_ota.subprocess, "run", boom)
        assert model_ota.restart_services() is False  # warns, never raises


def test_install_services_script_syntax():
    # Resolve bash via PATH and invoke it by full path: a bare "bash" makes
    # CreateProcess search System32 first, which finds the WSL stub instead
    # of Git Bash on Windows. Forward slashes: bash mangles backslash paths.
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash not available")
    if "system32" in bash.lower():
        pytest.skip("only WSL bash on PATH; needs a native bash for -n")
    script = os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))),
        "deploy", "install_services.sh")
    proc = subprocess.run([bash, "-n", script.replace(os.sep, "/")],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
