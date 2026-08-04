"""Tests for the per-acre chemical-savings tracker (docs §1.3)."""
import json

import pytest

from data.savings import SQM_PER_ACRE, SavingsTracker


def make_tracker(tmp_path, **kw):
    """Tracker with round numbers so the expected maths is obvious."""
    kw.setdefault("path", str(tmp_path / "savings.jsonl"))
    kw.setdefault("flow_ml_s", 100.0)            # 100 mL/s
    kw.setdefault("baseline_l_per_acre", 100.0)  # 100 L/acre broadcast
    kw.setdefault("price_inr_per_l", 500.0)
    kw.setdefault("swath_m", 0.5)
    return SavingsTracker(**kw)


def load_tenth_acre(t, sprays=20):
    """0.1 acre covered + `sprays` 1 s bursts -> 2 L used vs 10 L baseline."""
    t.update_distance(SQM_PER_ACRE / 5.0)  # x 0.5 m swath = 0.1 acre
    for _ in range(sprays):
        t.record_spray(1.0)


class TestVolumeMath:
    def test_volume_is_flow_times_duration(self, tmp_path):
        t = make_tracker(tmp_path)
        t.record_spray(0.5)
        t.record_spray(1.2)
        s = t.summary()
        assert s["sprays"] == 2
        assert s["litres_used"] == pytest.approx(0.17)  # 170 mL at 100 mL/s
        assert s["spray_seconds"] == pytest.approx(1.7)

    def test_nonpositive_duration_ignored(self, tmp_path):
        t = make_tracker(tmp_path)
        t.record_spray(0.0)
        t.record_spray(-1.0)
        assert t.summary()["sprays"] == 0

    def test_injected_timestamp_class_and_pose(self, tmp_path):
        t = make_tracker(tmp_path)
        t.record_spray(0.3, weed_class="parthenium", pose_xy=(1.0, 2.0),
                       timestamp=1000.0)
        s = t.summary()
        assert s["by_class"] == {"parthenium": 1}
        assert s["t_last_spray"] == 1000.0
        assert t.events[-1]["pose"] == [1.0, 2.0]


class TestAreaMath:
    def test_distance_times_swath_to_acres(self, tmp_path):
        t = make_tracker(tmp_path, swath_m=0.5)
        t.update_distance(SQM_PER_ACRE)  # m travelled x 0.5 m = half an acre
        assert t.area_m2 == pytest.approx(SQM_PER_ACRE / 2.0)
        assert t.area_acres == pytest.approx(0.5)

    def test_distance_accumulates_and_negative_ignored(self, tmp_path):
        t = make_tracker(tmp_path, swath_m=1.0)
        t.update_distance(100.0)
        t.update_distance(100.0)
        t.update_distance(-50.0)
        assert t.area_m2 == pytest.approx(200.0)


class TestSavingsMath:
    def test_percent_saved(self, tmp_path):
        t = make_tracker(tmp_path)
        load_tenth_acre(t)  # 2 L used vs 10 L baseline
        s = t.summary()
        assert s["baseline_litres"] == pytest.approx(10.0)
        assert s["litres_used"] == pytest.approx(2.0)
        assert s["litres_saved"] == pytest.approx(8.0)
        assert s["percent_saved"] == pytest.approx(80.0)

    def test_zero_area_guard(self, tmp_path):
        t = make_tracker(tmp_path)
        t.record_spray(1.0)  # sprayed but no distance yet
        s = t.summary()
        assert s["percent_saved"] == 0.0
        assert s["litres_saved"] == 0.0  # never negative
        assert s["inr_saved_per_acre"] == 0

    def test_rupee_math_chemical_only(self, tmp_path):
        t = make_tracker(tmp_path)
        load_tenth_acre(t)
        s = t.summary()
        assert s["chemical_inr_saved"] == 4000  # 8 L x Rs 500
        assert s["labour_inr_saved"] == 0       # off by default
        assert s["inr_saved"] == 4000

    def test_rupee_math_with_labour(self, tmp_path):
        t = make_tracker(tmp_path, labour_inr_per_acre=300.0)
        load_tenth_acre(t)
        s = t.summary()
        assert s["labour_inr_saved"] == 30      # 0.1 acre x Rs 300
        assert s["inr_saved"] == 4030

    def test_per_acre_figures(self, tmp_path):
        t = make_tracker(tmp_path)
        load_tenth_acre(t)
        s = t.summary()
        assert s["litres_used_per_acre"] == pytest.approx(20.0)
        assert s["litres_saved_per_acre"] == pytest.approx(80.0)
        assert s["inr_saved_per_acre"] == 40000


class TestPersistence:
    def test_save_and_reload(self, tmp_path):
        t = make_tracker(tmp_path)
        load_tenth_acre(t)
        t.save()
        hist = SavingsTracker.load_history(t.path)
        assert len(hist) == 1
        assert hist[0]["sprays"] == 20
        assert hist[0]["litres_saved"] == pytest.approx(8.0)

    def test_resave_dedupes_latest_wins(self, tmp_path):
        t = make_tracker(tmp_path)
        t.record_spray(1.0)
        t.save()
        t.record_spray(1.0)
        t.save()  # checkpoint again mid-mission
        hist = SavingsTracker.load_history(t.path)
        assert len(hist) == 1
        assert hist[0]["sprays"] == 2

    def test_two_missions_two_records(self, tmp_path):
        path = str(tmp_path / "savings.jsonl")
        for _ in range(2):
            t = make_tracker(tmp_path, path=path)
            t.record_spray(1.0)
            t.save()
        assert len(SavingsTracker.load_history(path)) == 2

    def test_corrupt_lines_skipped(self, tmp_path):
        t = make_tracker(tmp_path)
        load_tenth_acre(t)
        t.save()
        with open(t.path, "a", encoding="utf-8") as fh:
            fh.write("{oops not json\n")
            fh.write("\n")
            fh.write("[1,2,3]\n")  # valid JSON but not a mission dict
        hist = SavingsTracker.load_history(t.path)
        assert len(hist) == 1
        assert hist[0]["sprays"] == 20

    def test_missing_file_is_empty_history(self, tmp_path):
        assert SavingsTracker.load_history(str(tmp_path / "nope.jsonl")) == []


class TestSeasonTotals:
    def test_sums_across_missions(self, tmp_path):
        path = str(tmp_path / "savings.jsonl")
        for _ in range(2):
            t = make_tracker(tmp_path, path=path)
            load_tenth_acre(t)  # each mission: 0.1 acre, 8 L, Rs 4000 saved
            t.save()
        tot = SavingsTracker.season_totals(path)
        assert tot["missions"] == 2
        assert tot["area_acres"] == pytest.approx(0.2)
        assert tot["sprays"] == 40
        assert tot["litres_saved"] == pytest.approx(16.0)
        assert tot["inr_saved"] == 8000


class TestFormatSummary:
    def test_english_contains_key_numbers(self, tmp_path):
        t = make_tracker(tmp_path)
        load_tenth_acre(t)
        msg = t.format_summary(lang="en")
        assert "0.10" in msg          # acres
        assert "20 weeds" in msg      # spray count
        assert "8.0 L" in msg         # litres saved
        assert "80%" in msg
        assert "₹4000" in msg
        assert len(msg.splitlines()) <= 4

    def test_hindi_contains_key_numbers(self, tmp_path):
        t = make_tracker(tmp_path)
        load_tenth_acre(t)
        msg = t.format_summary(lang="hi")
        assert "एकड़" in msg and "खरपतवार" in msg
        assert "0.10" in msg and "8.0" in msg
        assert "₹4000" in msg
        assert len(msg.splitlines()) <= 4

    def test_season_line_sums_past_missions(self, tmp_path):
        path = str(tmp_path / "savings.jsonl")
        past = make_tracker(tmp_path, path=path)
        load_tenth_acre(past)
        past.save()  # Rs 4000 saved earlier this season
        t = make_tracker(tmp_path, path=path)
        load_tenth_acre(t)  # Rs 4000 saved today (unsaved yet)
        en = t.format_summary(lang="en", include_season=True)
        hi = t.format_summary(lang="hi", include_season=True)
        assert "Season total" in en and "16.0 L" in en and "₹8000" in en
        assert "सीज़न" in hi and "₹8000" in hi

    def test_saved_line_is_valid_json(self, tmp_path):
        t = make_tracker(tmp_path)
        load_tenth_acre(t)
        t.save()
        with open(t.path, encoding="utf-8") as fh:
            rec = json.loads(fh.readline())
        assert rec["mission_id"] == t.mission_id
        assert "t_saved" in rec
