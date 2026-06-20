"""Camera intrinsic calibration + undistortion.

The 160-degree M12 lens has heavy barrel distortion; undistorting frames before
detection/measurement improves accuracy. Run `calibrate_from_images` once with
checkerboard photos to produce a .npz, then `Undistorter` applies it at runtime.

OpenCV/numpy are imported lazily/guarded so this module imports without them.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def calibrate_from_images(image_glob: str, board_cols: int = 9, board_rows: int = 6,
                          square_size_m: float = 0.025,
                          out_path: str = "models/camera_intrinsics.npz") -> bool:
    """Detect checkerboards and save (camera_matrix, dist_coeffs) to out_path."""
    try:
        import glob

        import cv2
        import numpy as np
    except Exception as exc:
        logger.warning("OpenCV/numpy unavailable (%s)", exc)
        return False

    objp = np.zeros((board_rows * board_cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:board_cols, 0:board_rows].T.reshape(-1, 2) * square_size_m
    obj_points, img_points = [], []
    shape = None
    for path in glob.glob(image_glob):
        img = cv2.imread(path)
        if img is None:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        shape = gray.shape[::-1]
        found, corners = cv2.findChessboardCorners(gray, (board_cols, board_rows))
        if found:
            obj_points.append(objp)
            img_points.append(corners)
    if len(obj_points) < 5 or shape is None:
        logger.warning("need >=5 good checkerboard views, got %d", len(obj_points))
        return False
    _, mtx, dist, _, _ = cv2.calibrateCamera(obj_points, img_points, shape, None, None)
    np.savez(out_path, camera_matrix=mtx, dist_coeffs=dist)
    logger.info("saved intrinsics to %s", out_path)
    return True


class Undistorter:
    def __init__(self, npz_path: str = "models/camera_intrinsics.npz"):
        self.ok = False
        self._mtx = None
        self._dist = None
        try:
            import numpy as np

            data = np.load(npz_path)
            self._mtx = data["camera_matrix"]
            self._dist = data["dist_coeffs"]
            self.ok = True
        except Exception as exc:
            logger.warning("no camera intrinsics (%s); passthrough", exc)

    def apply(self, frame):
        if not self.ok:
            return frame
        import cv2

        return cv2.undistort(frame, self._mtx, self._dist)
