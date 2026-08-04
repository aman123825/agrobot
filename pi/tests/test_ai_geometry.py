"""Tests for the pure-math AI geometry: aiming, tagging, dose scaling."""
import math

from ai.plant_tagging import CameraGeometry, pixel_to_ground, tag_plant
from ai.spray_targeting import SprayTargeter, aim_angles


class TestAimAngles:
    def test_center_bbox_aims_straight(self):
        assert aim_angles((300, 220, 340, 260), 640, 480, 160, 100) == (0.0, 0.0)

    def test_right_half_pans_right(self):
        pan, _ = aim_angles((480, 220, 640, 260), 640, 480, 160, 100)
        assert pan > 0

    def test_bottom_half_tilts_down(self):
        _, tilt = aim_angles((300, 360, 340, 480), 640, 480, 160, 100)
        assert tilt > 0

    def test_clamped_to_mechanical_limit(self):
        pan, tilt = aim_angles((630, 470, 640, 480), 640, 480, 400, 400)
        assert pan <= 80.0 and tilt <= 80.0

    def test_zero_size_image_raises(self):
        try:
            aim_angles((0, 0, 1, 1), 0, 480, 160, 100)
        except ValueError:
            return
        raise AssertionError("expected ValueError")

    def test_targeter_remembers_last_aim(self):
        st = SprayTargeter(img_w=640, img_h=480)
        aim = st.aim((480, 360, 640, 480))
        assert st.last_aim == aim and aim != (0.0, 0.0)


class TestPixelToGround:
    GEOM = CameraGeometry(height_m=0.30, pitch_deg=15.0, hfov_deg=160, vfov_deg=100)

    def test_image_center_hits_ground_ahead(self):
        ground = pixel_to_ground(320, 240, 640, 480, self.GEOM)
        assert ground is not None
        forward, lateral = ground
        # depression = pitch only (15 deg): forward = h / tan(15)
        assert abs(forward - 0.30 / math.tan(math.radians(15))) < 1e-9
        assert abs(lateral) < 1e-9

    def test_above_horizon_returns_none(self):
        # top of frame: ang_y = -50 deg, depression = 15-50 < 0 -> no ground hit
        assert pixel_to_ground(320, 0, 640, 480, self.GEOM) is None

    def test_lower_pixel_is_closer(self):
        far = pixel_to_ground(320, 260, 640, 480, self.GEOM)[0]
        near = pixel_to_ground(320, 460, 640, 480, self.GEOM)[0]
        assert near < far

    def test_tag_plant_east_of_datum_when_heading_east(self):
        datum = (19.0, 72.9)
        # rover at origin heading east (theta=0); bbox at image center-bottom
        pos = tag_plant((300, 400, 340, 460), 640, 480, self.GEOM,
                        (0.0, 0.0, 0.0), datum)
        assert pos is not None
        lat, lng = pos
        assert lng > datum[1]  # forward = +x = east
        assert abs(lat - datum[0]) < 1e-4


class TestSprayDuration:
    def test_scales_with_area_and_saturates(self):
        from main import SPRAY_BASE_S, SPRAY_MAX_S, spray_duration_s

        tiny = spray_duration_s((0, 0, 10, 10), 640, 480)
        mid = spray_duration_s((0, 0, 200, 200), 640, 480)
        huge = spray_duration_s((0, 0, 640, 480), 640, 480)
        assert SPRAY_BASE_S <= tiny < mid < huge
        assert huge == SPRAY_MAX_S
