"""Tests for navigation math: geo conversion, pose EKF, coverage planner."""
import math

from nav.ekf import PoseEKF
from nav.geo import latlng_to_local, local_to_latlng
from nav.path_planner import (
    boustrophedon,
    cross_track_error,
    heading_error,
    reached,
    target_heading,
)


class TestGeo:
    def test_round_trip(self):
        lat0, lng0 = 19.0760, 72.8777  # Mumbai
        east, north = latlng_to_local(19.0800, 72.8800, lat0, lng0)
        lat, lng = local_to_latlng(east, north, lat0, lng0)
        assert abs(lat - 19.0800) < 1e-9
        assert abs(lng - 72.8800) < 1e-9

    def test_north_offset_is_meters(self):
        # 0.001 deg latitude ~ 111.3 m north
        _, north = latlng_to_local(19.001, 72.0, 19.0, 72.0)
        assert 110 < north < 112


class TestPoseEKF:
    def test_straight_line_prediction(self):
        ekf = PoseEKF()
        for _ in range(10):
            ekf.predict(v=1.0, omega=0.0, dt=0.1)  # 1 m/s for 1 s heading east
        px, py, th = ekf.pose
        assert abs(px - 1.0) < 1e-9 and abs(py) < 1e-9 and abs(th) < 1e-9

    def test_turn_changes_heading(self):
        ekf = PoseEKF()
        ekf.predict(v=0.0, omega=math.pi / 2, dt=1.0)
        assert abs(ekf.pose[2] - math.pi / 2) < 1e-9

    def test_gps_update_pulls_position(self):
        ekf = PoseEKF()
        for _ in range(5):
            ekf.update_gps(2.0, 3.0, var=0.5)
        px, py, _ = ekf.pose
        assert abs(px - 2.0) < 0.3 and abs(py - 3.0) < 0.3

    def test_uncertainty_shrinks_with_updates(self):
        ekf = PoseEKF()
        p0 = ekf.P[0][0]
        ekf.update_gps(0.0, 0.0, var=1.0)
        assert ekf.P[0][0] < p0


class TestPathPlanner:
    def test_boustrophedon_covers_and_alternates(self):
        pts = boustrophedon(width_m=2.0, length_m=10.0, row_spacing_m=1.0)
        assert len(pts) == 6  # 3 rows x 2 endpoints
        assert pts[0] == (0.0, 0.0) and pts[1] == (0.0, 10.0)
        assert pts[2] == (1.0, 10.0) and pts[3] == (1.0, 0.0)  # reversed row

    def test_boustrophedon_invalid_inputs(self):
        assert boustrophedon(0, 10, 1) == []
        assert boustrophedon(2, 10, 0) == []

    def test_cross_track_sign(self):
        # path along +Y; a point to the path's left (-X side... left of
        # direction (0,1) is (-1,0)) must be positive per the convention.
        assert cross_track_error((0, 0), (0, 10), (-1.0, 5.0)) > 0
        assert cross_track_error((0, 0), (0, 10), (1.0, 5.0)) < 0

    def test_heading_helpers(self):
        assert abs(target_heading((0, 0), (0, 5)) - math.pi / 2) < 1e-9
        assert abs(heading_error(math.pi, -math.pi)) < 1e-6  # wraps
        assert reached((0, 0), (0.1, 0.1), tol_m=0.3)
        assert not reached((0, 0), (1.0, 1.0), tol_m=0.3)
