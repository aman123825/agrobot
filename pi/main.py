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
from actuators import Pcf8574  # noqa: E402
from ai.obstacle_detection import ObstacleDetector  # noqa: E402
from ai.weed_detection import WeedDetector  # noqa: E402
from ai.disease_detection import DiseaseClassifier  # noqa: E402
from ai.plant_tagging import CameraGeometry, tag_plant  # noqa: E402
from ai.spray_targeting import SprayTargeter  # noqa: E402
from bridge.serial_bridge import SerialBridge  # noqa: E402
from control.imu import MPU6050  # noqa: E402
from control.servo_pwm import PanTiltServo  # noqa: E402
from data.plant_db import PlantDB  # noqa: E402
from data.recorder import BlackBox  # noqa: E402
from sensors.current_monitor import CurrentMonitor  # noqa: E402
from sensors.fuel_gauge import FuelGauge  # noqa: E402
from sensors.thermal_guardian import ThermalGuardian  # noqa: E402

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL_S = 0.4   # < firmware LINK_HEARTBEAT_TIMEOUT_MS (1500 ms)


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
        self.cap = _open_camera(camera_index)
        self._stopped = False
        self._frame_no = 0
        self._last_ping = 0.0
        self._last_fuel = 0.0
        self._last_thermal = 0.0
        self._ambient_c: float | None = None
        self._thermal_shutdown = False
        # Rover pose (x, y, heading) and GPS datum for plant tagging.
        # Updated externally or via EKF; default to origin.
        self._rover_pose: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._gps_datum: tuple[float, float] = (0.0, 0.0)

    def setup(self) -> None:
        self.obstacle.load()
        self.weed.load()
        self.disease.load()
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
        self._mqtt = None
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

    def _on_gps(self, payload: str) -> None:
        """Update the geo-tagging datum from a GPS telemetry message."""
        try:
            data = json.loads(payload)
        except (ValueError, TypeError):
            return
        if data.get("fix"):
            self._gps_datum = (float(data.get("lat", 0.0)),
                               float(data.get("lng", 0.0)))

    def _telegram_alert(self, message: str) -> None:
        """Best-effort Telegram push; never raises (FC-02 critical alerts)."""
        if self.telegram is None:
            return
        try:
            self.telegram(message)
        except Exception as exc:
            logger.debug("telegram alert failed (%s)", exc)

    def _read_target_depth(self) -> float | None:
        """Read VL53L1X ToF depth (m) for spray aiming. None if unavailable.

        Guarded: returns None on any failure so the pinhole aim still works
        (depth is advisory for the angle under a pinhole model).
        """
        reader = getattr(self, "_tof", None)
        if reader is None:
            return None
        try:
            mm = reader.range  # VL53L1X driver convention (mm)
            return mm / 1000.0 if mm and mm > 0 else None
        except Exception:
            return None

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

        # Combine all local stop reasons: AI obstacle, tilt, motor stall.
        detections = self.obstacle.detect(frame)
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
            if self._stopped:
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
            if weed_result:
                # FC-01: point the pan/tilt nozzle at the weed before spraying.
                bbox, _conf = weed_box
                depth_m = self._read_target_depth()
                pan_deg, tilt_deg = self.spray_targeter.aim(bbox, depth_m=depth_m)
                self.pan_tilt.point(pan_deg, tilt_deg)
                logger.info("WEED -> aim pan=%.1f tilt=%.1f -> spray burst",
                            pan_deg, tilt_deg)
                self.actuators.spray()
                self.blackbox.log("spray", {"frame": self._frame_no,
                                            "pan": round(pan_deg, 1),
                                            "tilt": round(tilt_deg, 1)})

            # Disease classification on the same frame.
            disease_class, confidence = self.disease.classify(frame)
            if confidence > 0.3:
                # Attempt to geo-tag the detection for plant DB.
                h, w = (frame.shape[0], frame.shape[1]) if hasattr(frame, "shape") else (480, 640)
                # Use center of frame as the bounding box (full-frame classify).
                bbox = (w * 0.25, h * 0.25, w * 0.75, h * 0.75)
                pos = tag_plant(bbox, w, h, self.cam_geom,
                                self._rover_pose, self._gps_datum)
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
            self.blackbox.log("fuel", {"soc": round(soc, 1)})

        # Thermal guardian ~1 Hz (FC-02): CPU + pack NTC + ambient.
        if now - self._last_thermal >= 1.0:
            self._last_thermal = now
            self._run_thermal_guard()

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
            self.actuators.all_off()
            self.pan_tilt.center()
            self.pan_tilt.close()
            self.plant_db.close()
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
