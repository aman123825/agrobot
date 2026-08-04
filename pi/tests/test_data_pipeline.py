"""Tests for the stream processor's windowed stats and the soil heatmap."""
from collections import deque

from data.heatmap import idw_grid, idw_interpolate
from mission.scheduler import MissionScheduler, within_operating_window
from pipeline.pathway_stream import NUTRIENTS, StreamProcessor


def make_processor():
    """Build a StreamProcessor without touching MQTT (skip __init__)."""
    sp = StreamProcessor.__new__(StreamProcessor)
    sp.alert_fn = None
    sp.csv_dir = "."
    sp._windows = {key: deque() for key in NUTRIENTS}
    sp._last_gps = {"lat": 19.0, "lng": 72.9, "fix": 1}
    return sp


class TestStreamProcessor:
    def test_row_carries_gps_and_values(self):
        sp = make_processor()
        row = sp._process(1000.0, {"n": 50, "p": 20, "k": 30, "ph": 6.5})
        assert row["lat"] == 19.0 and row["gps_fix"] == 1
        assert row["n"] == 50.0 and row["ph_avg30s"] == 6.5

    def test_stable_readings_are_not_anomalies(self):
        sp = make_processor()
        for i in range(10):
            row = sp._process(1000.0 + i, {"n": 50, "p": 20, "k": 30, "ph": 6.5})
        assert row["n_anomaly"] == 0

    def test_spike_is_flagged(self):
        sp = make_processor()
        for i in range(10):
            sp._process(1000.0 + i, {"n": 50 + (i % 2), "p": 20, "k": 30, "ph": 6.5})
        row = sp._process(1010.0, {"n": 500, "p": 20, "k": 30, "ph": 6.5})
        assert row["n_anomaly"] == 1
        assert row["p_anomaly"] == 0

    def test_old_samples_age_out_of_window(self):
        sp = make_processor()
        sp._process(1000.0, {"n": 100, "p": 0, "k": 0, "ph": 7})
        sp._process(1100.0, {"n": 50, "p": 0, "k": 0, "ph": 7})  # 100 s later
        assert len(sp._windows["n"]) == 1  # 30 s window dropped the old one


class TestHeatmap:
    POINTS = [(0.0, 0.0, 10.0), (10.0, 0.0, 20.0), (0.0, 10.0, 30.0)]

    def test_exact_at_data_point(self):
        assert idw_interpolate(self.POINTS, 0.0, 0.0) == 10.0

    def test_interpolated_value_within_range(self):
        v = idw_interpolate(self.POINTS, 5.0, 5.0)
        assert 10.0 < v < 30.0

    def test_grid_shape(self):
        grid = idw_grid(self.POINTS, bounds=(0, 0, 10, 10), nx=5, ny=4)
        assert len(grid) == 4 and len(grid[0]) == 5


class TestMissionScheduler:
    def test_lifecycle(self, tmp_path):
        sched = MissionScheduler(path=str(tmp_path / "missions.json"))
        mid = sched.add_mission("scan", zone={"name": "plot-a"})
        current = sched.get_current()
        assert current is not None and current["id"] == mid
        assert current["status"] == "active"
        sched.advance()
        assert sched.get_current() is None  # queue drained

    def test_persistence_across_instances(self, tmp_path):
        path = str(tmp_path / "missions.json")
        first = MissionScheduler(path=path)
        mid = first.add_mission("scan", zone={"name": "plot-b"})
        second = MissionScheduler(path=path)
        assert any(m["id"] == mid for m in second.list_missions())

    def test_operating_window(self):
        assert within_operating_window(23, 22, 6)      # wraps midnight
        assert within_operating_window(3, 22, 6)
        assert not within_operating_window(12, 22, 6)
        assert within_operating_window(12, 8, 8)       # degenerate = always
