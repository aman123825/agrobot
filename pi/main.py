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
from bridge.serial_bridge import SerialBridge  # noqa: E402

logger = logging.getLogger(__name__)


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
    def __init__(self, camera_index: int = 0, weed_every: int = 15):
        self.weed_every = weed_every
        self.obstacle = ObstacleDetector()
        self.weed = WeedDetector()
        self.actuators = Pcf8574()
        self.serial = SerialBridge()
        self.cap = _open_camera(camera_index)
        self._stopped = False
        self._frame_no = 0

    def setup(self) -> None:
        self.obstacle.load()
        self.weed.load()
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

        detections = self.obstacle.detect(frame)
        if self.obstacle.should_stop(detections):
            if not self._stopped:
                self._send("STOP")
                self._stopped = True
                logger.info("OBSTACLE -> STOP (%d detections)", len(detections))
        else:
            if self._stopped:
                self._send("RESUME")
                self._stopped = False
                logger.info("clear -> RESUME")

        # Spot-spray on weed detection, but never while halted for an obstacle.
        if not self._stopped and self._frame_no % self.weed_every == 0:
            if self.weed.detect(frame):
                logger.info("WEED -> spray burst")
                self.actuators.spray()

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
