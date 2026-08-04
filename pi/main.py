"""AgriRover Raspberry Pi orchestrator.

Ties together the vision pipeline and the ESP32 link:
  - grabs camera frames (Pi Camera / USB)
  - runs YOLOv8n obstacle detection -> sends STOP / RESUME to the ESP32
  - runs weed detection periodically -> fires the misting relay (spot spray)
  - reads ESP32 telemetry/ACK lines for logging

Every external dependency (camera, models, serial, I2C) is guarded so the
orchestrator starts and logs clearly even when a piece is missing, instead of
crashing. The MQTT->CSV telemetry path runs separately in
pipeline/pathway_stream.py.

Run:  python pi/main.py
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
import time

sys.path.append(os.path.dirname(__file__))
import config
from actuators import Pcf8574
from ai.camera_calib import Undistorter
from ai.disease_detection import DiseaseClassifier
from ai.frame_capture import FrameCapture
from ai.obstacle_detection import ObstacleDetector
from ai.plant_tagging import CameraGeometry, tag_plant
from ai.spray_targeting import SprayTargeter
from ai.weed_detection import WeedDetector
from bridge.serial_bridge import SerialBridge
from control.encoders import Encoders
from control.imu import MPU6050
from control.servo_pwm import PanTiltServo
from data.plant_db import PlantDB
from data.recorder import BlackBox
from data.savings import SavingsTracker
from monitor.health import HealthMonitor
from nav.ekf import PoseEKF
from nav.geo import latlng_to_local
from sensors.current_monitor import CurrentMonitor
from sensors.fuel_gauge import FuelGauge
from sensors.thermal_guardian import ThermalGuardian
from sensors.tof import TofSensor

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL_S = 0.4   # < firmware LINK_HEARTBEAT_TIMEOUT_MS (1500 ms)

# Weed-size-scaled spray dose (docs/UPGRADES.md §6): burst duration grows with
# the detection's share of the frame, saturating at SPRAY_FULL_AREA_FRAC.
SPRAY_BASE_S = 0.3
SPRAY_MAX_S = 1.2
SPRAY_FULL_AREA_FRAC = 0.25


def spray_duration_s(bbox: tuple[float, float, float, float],
                     img_w: int, img_h: int) -> float:
    """Burst duration for a weed bbox - bigger weed, longer burst."""
    area = max(0.0, (bbox[2] - bbox[0])) * max(0.0, (bbox[3] - bbox[1]))
    frac = area / float(max(1, img_w * img_h))
    scale = min(1.0, frac / SPRAY_FULL_AREA_FRAC)
    return round(SPRAY_BASE_S + (SPRAY_MAX_S - SPRAY_BASE_S) * scale, 2)


def _open_camera(index: int):
    try:
        import cv2

        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            logger.warning("camera %s did not open", index)
            return None
        return cap
    except Exception as exc:
        logger.warning("OpenCV/camera unavailable (%s)", exc)
        return None


class Orchestrator:
    def __init__(self, camera_index: int = 0, weed_every: int = 15,
                 plant_db_path: str = "plant_db.json"):
        self.weed_every = weed_every
        self.obstacle = ObstacleDetector()
        self.weed = WeedDetector()
        self.disease = DiseaseClassifier()
        self.actuators = Pcf8574()
        self.serial = SerialBridge()
        self.imu = MPU6050()
        self.current_mon = CurrentMonitor()
        self.fuel = FuelGauge()
        self.blackbox = BlackBox()
        self.plant_db = PlantDB(path=plant_db_path)
        self.cam_geom = CameraGeometry()
        # FC-01 aimed spray: pan/tilt nozzle + bbox->angle targeting.
        self.spray_targeter = SprayTargeter(hfov_deg=self.cam_geom.hfov_deg,
                                            vfov_deg=self.cam_geom.vfov_deg)
        self.pan_tilt = PanTiltServo()
        # FC-02 thermal guardian (CPU + pack NTC + ambient).
        self.thermal = ThermalGuardian()
        self.telegram = None
        # Lens undistortion (160-deg barrel distortion; passthrough until
        # models/camera_intrinsics.npz exists - see ai/camera_calib.py).
        self.undistort = Undistorter(os.path.join(config.MODEL_DIR,
                                                  "camera_intrinsics.npz"))
        # Forward ToF distance for the 400 mm stop rule + spray target depth.
        self.tof = TofSensor()
        # Odometry -> EKF pose so plant tags are relative to the field datum,
        # not just the latest raw GPS fix.
        self.encoders = Encoders()
        self.ekf = PoseEKF()
        # Active-learning capture: save low-confidence + periodic frames.
        self.capture = FrameCapture()
        # Field-health telemetry (farmer-needs-and-durability.md §2.2).
        self.health = HealthMonitor(boot_file=config.BOOT_COUNTER_PATH,
                                    disk_path=config.HEALTH_DISK_PATH)
        # Chemical-savings proof for the farmer (same doc §1.3).
        self.savings = SavingsTracker(flow_ml_s=config.SPRAY_FLOW_ML_S,
                                      baseline_l_per_acre=config.BASELINE_L_PER_ACRE,
                                      price_inr_per_l=config.CHEMICAL_PRICE_INR_L,
                                      swath_m=config.SPRAY_SWATH_M,
                                      labour_inr_per_acre=config.LABOUR_INR_PER_ACRE,
                                      path=config.SAVINGS_PATH)
        self.commander = None
        self._mqtt = None
        self.cap = _open_camera(camera_index)
        self._stopped = False
        # Latched by Telegram /stop; step()'s obstacle-clear auto-resume must
        # not undo it — only /go (or /resume) releases it.
        self._remote_stopped = False
        self._frame_no = 0
        self._last_ping = 0.0
        self._last_fuel = 0.0
        self._last_thermal = 0.0
        self._last_health = 0.0
        self._last_health_status = "ok"
        self._last_soc: float | None = None
        self._last_frame = None
        self._last_odom: float | None = None
        self._ambient_c: float | None = None
        self._thermal_shutdown = False
        # GPS datum (first fix) anchoring the EKF's local frame for tagging.
        self._datum: tuple[float, float] | None = None

    def setup(self) -> None:
        self.obstacle.load()
        self.weed.load()
        self.disease.load()
        self.tof.start()
        self.encoders.start()
        # Optional Telegram alerter for critical events (FC-02). Guarded so a
        # missing 'requests' dependency or credentials never breaks startup.
        try:
            from alerts.telegram_bot import send_alert

            self.telegram = send_alert
            logger.info("Telegram alerter available")
        except Exception as exc:
            logger.warning("Telegram alerter unavailable (%s)", exc)
            self.telegram = None
        try:
            self.serial.open()
        except Exception as exc:
            logger.warning("serial link unavailable (%s); commands will be dropped", exc)
            self.serial = None  # type: ignore

        # Optional GPS feed so plant tagging uses REAL coordinates (datum =
        # latest fix). Without it, tags fall back to the (0,0) origin.
        try:
            import config as _cfg
            from bridge.mqtt_client import MqttClient

            self._mqtt = MqttClient()
            self._mqtt.connect()
            self._mqtt.subscribe(_cfg.TOPICS["gps"], self._on_gps)
            threading.Thread(target=self._mqtt.loop_forever, daemon=True).start()
            logger.info("GPS feed subscribed for plant geo-tagging")
        except Exception as exc:
            logger.warning("GPS feed unavailable (%s); plant tags use origin", exc)

        # Two-way Telegram control (docs/UPGRADES.md §9): /stop /go /status
        # /photo /summary. start() refuses (fail closed) unless both a token
        # and TELEGRAM_ALLOWED_CHAT_IDS are configured.
        try:
            from alerts.telegram_bot import TelegramCommander

            self.commander = TelegramCommander(callbacks={
                "stop": self._remote_stop,
                "resume": self._remote_resume,
                "status": self._status_text,
                "photo": self._photo_jpeg,
                "summary": lambda: self.savings.format_summary(
                    lang=config.SUMMARY_LANG, include_season=True),
            })
            if self.commander.start():
                logger.info("Telegram two-way control active")
        except Exception as exc:
            logger.warning("Telegram commander unavailable (%s)", exc)
            self.commander = None

    def _remote_stop(self) -> None:
        """Telegram /stop: latch a halt that obstacle-clear cannot undo."""
        self._remote_stopped = True
        if not self._stopped:
            self._send("STOP")
            self._stopped = True
        logger.info("STOP (remote command)")
        self.blackbox.log("stop", {"reason": "remote"})

    def _remote_resume(self) -> None:
        """Telegram /go: release the remote latch and resume."""
        self._remote_stopped = False
        if self._stopped:
            self._send("RESUME")
            self._stopped = False
        logger.info("RESUME (remote command)")
        self.blackbox.log("resume", {"reason": "remote"})

    def _status_text(self) -> str:
        """One-line rover status for the Telegram /status reply."""
        state = ("STOPPED (remote)" if self._remote_stopped
                 else "STOPPED" if self._stopped else "running")
        soc = f"{self._last_soc:.0f}%" if self._last_soc is not None else "?"
        s = self.savings.summary()
        return (f"frame {self._frame_no} | {state} | SoC {soc} | "
                f"{s['sprays']} sprays, {s['area_acres']} acres")

    def _photo_jpeg(self) -> bytes | None:
        """Latest undistorted frame as JPEG for the Telegram /photo reply."""
        if self._last_frame is None:
            return None
        try:
            import cv2

            ok, buf = cv2.imencode(".jpg", self._last_frame)
            return buf.tobytes() if ok else None
        except Exception:
            return None

    def _on_gps(self, payload: str) -> None:
        """Feed GPS fixes into the EKF (first fix anchors the local datum)."""
        try:
            data = json.loads(payload)
        except (ValueError, TypeError):
            return
        if not data.get("fix"):
            return
        lat = float(data.get("lat", 0.0))
        lng = float(data.get("lng", 0.0))
        if self._datum is None:
            self._datum = (lat, lng)
            logger.info("GPS datum set: %.6f, %.6f", lat, lng)
            return
        east, north = latlng_to_local(lat, lng, self._datum[0], self._datum[1])
        self.ekf.update_gps(east, north, var=config.GPS_VAR_M2)

    def _telegram_alert(self, message: str) -> None:
        """Best-effort Telegram push; never raises (FC-02 critical alerts)."""
        if self.telegram is None:
            return
        try:
            self.telegram(message)
        except Exception as exc:
            logger.debug("telegram alert failed (%s)", exc)

    def _read_target_depth(self) -> float | None:
        """VL53L1X ToF depth (m) for spray aiming. None if unavailable.

        Depth is advisory for the angle under a pinhole model, so None is fine.
        """
        mm = self.tof.read_mm()
        return mm / 1000.0 if mm else None

    def _update_odometry(self, now: float) -> None:
        """Dead-reckon the EKF from wheel encoders (differential drive)."""
        if self._last_odom is None:
            self._last_odom = now
            return
        dt = now - self._last_odom
        self._last_odom = now
        if not 0.0 < dt < 5.0:  # clock jump / long pause -> skip this step
            return
        v_left, v_right = self.encoders.velocity_mm_s()
        v = (v_left + v_right) / 2000.0                     # mm/s -> m/s
        omega = (v_right - v_left) / 1000.0 / config.TRACK_WIDTH_M
        self.ekf.predict(v, omega, dt)
        # Area covered feeds the chemical-savings proof (distance x swath).
        self.savings.update_distance(abs(v) * dt)

    def _run_thermal_guard(self) -> None:
        """Evaluate thermal state; on a pack-critical reading STOP + alert (FC-02)."""
        decision = self.thermal.check(ambient_c=self._ambient_c)
        action = decision["action"]
        if action == "ok":
            return
        self.blackbox.log("thermal", {"action": action,
                                      "reasons": decision["reasons"]})
        # pack-critical (stop/shutdown) -> halt the rover + critical alert.
        if action in ("stop", "shutdown"):
            if not self._stopped:
                self._send("STOP")
                self._stopped = True
            if action == "shutdown":
                self._thermal_shutdown = True
            reasons = "; ".join(decision["reasons"])
            logger.error("THERMAL %s: %s", action.upper(), reasons)
            self._telegram_alert(f"AgriRover thermal {action}: {reasons}")
        elif action == "pause":
            if not self._stopped:
                self._send("STOP")
                self._stopped = True
            logger.warning("THERMAL pause: %s", "; ".join(decision["reasons"]))
            self._telegram_alert("AgriRover thermal pause: " +
                                 "; ".join(decision["reasons"]))
        elif action == "throttle":
            logger.info("THERMAL throttle: %s", "; ".join(decision["reasons"]))

    def _send(self, cmd: str) -> None:
        if self.serial is not None:
            try:
                self.serial.send(cmd)
            except Exception as exc:
                logger.warning("serial send failed (%s)", exc)

    def _read_acks(self) -> None:
        if self.serial is None:
            return
        try:
            line = self.serial.read_line()
            if line:
                logger.debug("esp32: %s", line)
        except Exception:
            pass

    def step(self, frame) -> None:
        self._frame_no += 1
        now = time.time()

        # Heartbeat: keep the firmware dead-man satisfied while we're alive.
        if now - self._last_ping >= HEARTBEAT_INTERVAL_S:
            self._send("PING")
            self._last_ping = now

        # Undistort (160-deg lens) and dead-reckon the pose every frame.
        frame = self.undistort.apply(frame)
        self._last_frame = frame  # for the Telegram /photo reply
        self._update_odometry(now)

        # Combine all local stop reasons: AI obstacle, tilt, motor stall.
        # Real ToF distance makes should_stop() use the 400 mm rule instead
        # of the fail-safe stop-on-any-detection.
        detections = self.obstacle.detect(frame, distance_mm=self.tof.read_mm())
        tilt = self.imu.tilt_unsafe()
        stall = self.current_mon.check_stall(now)
        stop = self.obstacle.should_stop(detections) or tilt or stall

        if stop:
            if not self._stopped:
                reason = "tilt" if tilt else "stall" if stall else "obstacle"
                self._send("STOP")
                self._stopped = True
                logger.info("STOP (%s, %d detections)", reason, len(detections))
                self.blackbox.log("stop", {"reason": reason, "detections": len(detections)})
        else:
            if self._stopped and not self._remote_stopped:
                self._send("RESUME")
                self._stopped = False
                logger.info("clear -> RESUME")
                self.blackbox.log("resume", {})

        # Spot-spray on weed detection, but never while halted.
        # Also run disease classification and record the observation in the
        # per-plant database for health history tracking.
        if not self._stopped and self._frame_no % self.weed_every == 0:
            weed_box = self.weed.detect_best(frame)
            weed_result = weed_box is not None
            fh, fw = (frame.shape[0], frame.shape[1]) if hasattr(frame, "shape") else (480, 640)
            if weed_result:
                # FC-01: point the pan/tilt nozzle at the weed before spraying.
                bbox, weed_conf = weed_box
                depth_m = self._read_target_depth()
                pan_deg, tilt_deg = self.spray_targeter.aim(bbox, depth_m=depth_m)
                self.pan_tilt.point(pan_deg, tilt_deg)
                # Dose scaled to weed size: bigger weed, longer burst.
                burst_s = spray_duration_s(bbox, fw, fh)
                logger.info("WEED -> aim pan=%.1f tilt=%.1f -> spray %.2fs",
                            pan_deg, tilt_deg, burst_s)
                self.actuators.spray(duration_s=burst_s)
                x, y, _ = self.ekf.pose
                self.savings.record_spray(burst_s, weed_class="weed",
                                          pose_xy=(x, y))
                self.blackbox.log("spray", {"frame": self._frame_no,
                                            "pan": round(pan_deg, 1),
                                            "tilt": round(tilt_deg, 1),
                                            "burst_s": burst_s})
                # Feed the weed detection to the active-learning capture too.
                detections = detections + [{"label": "weed", "conf": weed_conf,
                                            "bbox": bbox}]

            # Disease classification on the same frame.
            disease_class, confidence = self.disease.classify(frame)
            if confidence > 0.3:
                # Geo-tag via the EKF pose in the datum-anchored local frame.
                # Use center of frame as the bounding box (full-frame classify).
                bbox = (fw * 0.25, fh * 0.25, fw * 0.75, fh * 0.75)
                pos = tag_plant(bbox, fw, fh, self.cam_geom,
                                self.ekf.pose, self._datum or (0.0, 0.0))
                if pos is not None:
                    lat, lng = pos
                    pid = self.plant_db.record_observation(
                        lat=lat, lng=lng,
                        disease_class=disease_class,
                        confidence=confidence,
                        notes="weed" if weed_result else "",
                    )
                    self.blackbox.log("plant_obs", {
                        "plant_id": pid,
                        "disease": disease_class,
                        "conf": round(confidence, 3),
                        "lat": round(lat, 7),
                        "lng": round(lng, 7),
                    })
                    logger.debug("plant %s: %s (%.0f%%)", pid,
                                 disease_class, confidence * 100)

        # Battery fuel gauge (coulomb counting) ~1 Hz.
        if now - self._last_fuel >= 1.0:
            soc = self.fuel.update()
            self._last_fuel = now
            self._last_soc = soc
            self.blackbox.log("fuel", {"soc": round(soc, 1)})

        # Thermal guardian ~1 Hz (FC-02): CPU + pack NTC + ambient.
        if now - self._last_thermal >= 1.0:
            self._last_thermal = now
            self._run_thermal_guard()

        # Field-health telemetry (farmer-needs-and-durability.md §2.2):
        # publish vitals over MQTT; Telegram only on status *transitions* so
        # a stuck warn/critical state can't spam the farmer.
        if now - self._last_health >= config.HEALTH_PERIOD_S:
            self._last_health = now
            h = self.health.sample()
            self.blackbox.log("health", h)
            if self._mqtt is not None:
                try:
                    self._mqtt.publish(config.TOPICS["health"], json.dumps(h))
                except Exception as exc:
                    logger.debug("health publish failed (%s)", exc)
            if h["status"] != self._last_health_status:
                alert = self.health.format_alert(h)
                if alert:
                    self._telegram_alert(alert)
            self._last_health_status = h["status"]

        # Active learning: save frames worth labelling (rate/file-capped).
        self.capture.consider(frame, self._frame_no, detections)

        self._read_acks()

    def run(self, max_frames: int | None = None) -> None:
        if self.cap is None:
            logger.error("no camera; orchestrator idle. Connect a camera and restart.")
            return
        import cv2

        logger.info("orchestrator running (obstacle=%s weed=%s)",
                    self.obstacle.backend, self.weed.backend)
        try:
            while True:
                ok, frame = self.cap.read()
                if not ok:
                    logger.warning("frame grab failed; retrying")
                    time.sleep(0.1)
                    continue
                self.step(frame)
                if max_frames is not None and self._frame_no >= max_frames:
                    break
        except KeyboardInterrupt:
            logger.info("shutting down")
        finally:
            self._send("STOP")
            if self.commander is not None:
                self.commander.stop()
            self.actuators.all_off()
            self.pan_tilt.center()
            self.pan_tilt.close()
            self.encoders.stop()
            self.tof.stop()
            self.plant_db.close()
            # Mission proof: persist the savings line and push the
            # farmer-facing summary (§1.3 — this number IS the sales pitch).
            try:
                s = self.savings.summary()
                if s["sprays"] or s["distance_m"] > 0:
                    self.savings.save()
                    self._telegram_alert(self.savings.format_summary(
                        lang=config.SUMMARY_LANG, include_season=True))
            except Exception as exc:
                logger.warning("savings summary failed (%s)", exc)
            self.cap.release()
            cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="AgriRover Pi orchestrator")
    parser.add_argument("--camera", type=int, default=0, help="camera index")
    parser.add_argument("--weed-every", type=int, default=15, help="run weed model every N frames")
    parser.add_argument("--max-frames", type=int, default=None, help="stop after N frames (test)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    orch = Orchestrator(camera_index=args.camera, weed_every=args.weed_every)
    orch.setup()
    orch.run(max_frames=args.max_frames)


if __name__ == "__main__":
    main()
