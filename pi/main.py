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
import logging
import os
import sys
import time

sys.path.append(os.path.dirname(__file__))
from actuators import Pcf8574  # noqa: E402
from ai.obstacle_detection import ObstacleDetector  # noqa: E402
from ai.weed_detection import WeedDetector  # noqa: E402
from ai.disease_detection import DiseaseClassifier  # noqa: E402
from ai.plant_tagging import CameraGeometry, tag_plant  # noqa: E402
from bridge.serial_bridge import SerialBridge  # noqa: E402
from control.imu import MPU6050  # noqa: E402
from data.plant_db import PlantDB  # noqa: E402
from data.recorder import BlackBox  # noqa: E402
from sensors.current_monitor import CurrentMonitor  # noqa: E402
from sensors.fuel_gauge import FuelGauge  # noqa: E402

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
        self.cap = _open_camera(camera_index)
        self._stopped = False
        self._frame_no = 0
        self._last_ping = 0.0
        self._last_fuel = 0.0
        # Rover pose (x, y, heading) and GPS datum for plant tagging.
        # Updated externally or via EKF; default to origin.
        self._rover_pose: tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._gps_datum: tuple[float, float] = (0.0, 0.0)

    def setup(self) -> None:
        self.obstacle.load()
        self.weed.load()
        self.disease.load()
        try:
            self.serial.open()
        except Exception as exc:
            logger.warning("serial link unavailable (%s); commands will be dropped", exc)
            self.serial = None  # type: ignore

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
            weed_result = self.weed.detect(frame)
            if weed_result:
                logger.info("WEED -> spray burst")
                self.actuators.spray()
                self.blackbox.log("spray", {"frame": self._frame_no})

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
