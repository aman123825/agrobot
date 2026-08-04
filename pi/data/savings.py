"""Per-acre chemical-savings tracker -- the number that sells the rover.

docs/farmer-needs-and-durability.md §1.3: "add per-acre chemical-saved
logging so we can *prove* savings to farmers -- that number is the sales
pitch."  Every weed-size-scaled burst (0.3-1.2 s, ``spray_duration_s`` in
pi/main.py) becomes litres and rupees the farmer can check against the
commercial benchmarks in §1.2: John Deere See & Spray 50-59% herbicide
savings; ICAR precision-weeding trials ~65% weed-management cost cut.

Baseline assumptions (constructor defaults, all overridable):

- **Broadcast baseline 100 L/acre** of spray mix -- a conservative,
  defensible figure for knapsack blanket spraying (typical Indian
  practice is 100-200 L/acre), so the "saved" number understates rather
  than oversells.
- **Pump flow 30 mL/s** is a bench figure.  CALIBRATE PER NOZZLE: run
  the pump into a measuring jug for 60 s and set ``flow_ml_s`` -- the
  whole pitch rests on this number being honest.
- **Chemical price Rs 500/L** of mix-equivalent; set the real per-crop
  figure.  **Labour savings default to 0** (off until configured with a
  local Rs/acre rate).

Farmers don't want dashboards (§1.3, data-logging row) -- the product
output is :meth:`SavingsTracker.format_summary`, a 3-4 line Hindi or
English message for Telegram/WhatsApp.  Mission summaries append to a
JSONL history (one line per save; re-saves of the same mission dedupe on
reload) so season-to-date savings survive power cuts and can be proven
across visits.  Pure stdlib; runs anywhere, including Windows.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid

logger = logging.getLogger(__name__)

# 1 acre = 4046.86 m^2
SQM_PER_ACRE = 4046.86

DEFAULT_FLOW_ML_S = 30.0          # calibrate per nozzle (see module docstring)
DEFAULT_BASELINE_L_PER_ACRE = 100.0  # knapsack broadcast mix, conservative
DEFAULT_PRICE_INR_PER_L = 500.0
DEFAULT_SWATH_M = 0.3             # effective treated width of the sprayer pass
DEFAULT_PATH = "savings.jsonl"


class SavingsTracker:
    """Accumulates spot-spray volume vs the broadcast baseline for one mission.

    Feed it every spray burst (:meth:`record_spray`) and incremental
    distance from the EKF/encoders (:meth:`update_distance`); ask it for
    :meth:`summary` numbers or the farmer-facing :meth:`format_summary`
    string, and :meth:`save` one JSONL line at mission end.
    """

    def __init__(self,
                 flow_ml_s: float = DEFAULT_FLOW_ML_S,
                 baseline_l_per_acre: float = DEFAULT_BASELINE_L_PER_ACRE,
                 price_inr_per_l: float = DEFAULT_PRICE_INR_PER_L,
                 swath_m: float = DEFAULT_SWATH_M,
                 labour_inr_per_acre: float = 0.0,
                 path: str = DEFAULT_PATH,
                 autosave_interval_s: float = 0.0):
        self.flow_ml_s = flow_ml_s
        self.baseline_l_per_acre = baseline_l_per_acre
        self.price_inr_per_l = price_inr_per_l
        self.swath_m = swath_m
        self.labour_inr_per_acre = labour_inr_per_acre
        self.path = path
        # 0 = autosave off; >0 = also checkpoint every N seconds so a power
        # cut mid-mission still leaves a provable line (dedup on reload).
        self.autosave_interval_s = autosave_interval_s

        self.mission_id = "S-" + uuid.uuid4().hex[:8]
        self._lock = threading.Lock()
        self._t_start = time.time()
        self._t_last_spray: float | None = None
        self._spray_count = 0
        self._spray_seconds = 0.0
        self._volume_ml = 0.0
        self._distance_m = 0.0
        self._by_class: dict[str, int] = {}
        # Lightweight per-burst log (not persisted) for a future spray map.
        self.events: list[dict] = []
        self._last_autosave = self._t_start

    # ------------------------------------------------------------------
    # Accumulation
    # ------------------------------------------------------------------

    def record_spray(self, duration_s: float, weed_class: str | None = None,
                     pose_xy: tuple[float, float] | None = None,
                     timestamp: float | None = None) -> None:
        """Log one spray burst: volume = duration x pump flow rate."""
        if duration_s <= 0:
            return
        ts = time.time() if timestamp is None else timestamp
        cls = weed_class or "weed"
        with self._lock:
            self._spray_count += 1
            self._spray_seconds += duration_s
            self._volume_ml += duration_s * self.flow_ml_s
            self._by_class[cls] = self._by_class.get(cls, 0) + 1
            self._t_last_spray = ts
            self.events.append({"ts": ts, "duration_s": duration_s,
                                "weed_class": cls,
                                "pose": list(pose_xy) if pose_xy else None})
        self._maybe_autosave()

    def update_distance(self, meters: float) -> None:
        """Add incremental distance travelled; area = distance x swath."""
        if meters <= 0:
            return
        with self._lock:
            self._distance_m += meters
        self._maybe_autosave()

    @property
    def area_m2(self) -> float:
        with self._lock:
            return self._distance_m * self.swath_m

    @property
    def area_acres(self) -> float:
        return self.area_m2 / SQM_PER_ACRE

    # ------------------------------------------------------------------
    # Summary numbers
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Mission-to-now numbers: litres, percent and rupees saved."""
        with self._lock:
            area_acres = (self._distance_m * self.swath_m) / SQM_PER_ACRE
            litres_used = self._volume_ml / 1000.0
            baseline_l = area_acres * self.baseline_l_per_acre
            litres_saved = max(0.0, baseline_l - litres_used)
            percent_saved = (100.0 * litres_saved / baseline_l
                             if baseline_l > 0 else 0.0)
            chemical_inr = litres_saved * self.price_inr_per_l
            labour_inr = area_acres * self.labour_inr_per_acre
            if area_acres > 0:
                used_pa = litres_used / area_acres
                saved_pa = litres_saved / area_acres
                inr_pa = (chemical_inr + labour_inr) / area_acres
            else:
                used_pa = saved_pa = inr_pa = 0.0
            return {
                "mission_id": self.mission_id,
                "t_start": round(self._t_start, 3),
                "t_last_spray": self._t_last_spray,
                "distance_m": round(self._distance_m, 1),
                "area_acres": round(area_acres, 3),
                "sprays": self._spray_count,
                "spray_seconds": round(self._spray_seconds, 2),
                "by_class": dict(self._by_class),
                "litres_used": round(litres_used, 3),
                "baseline_litres": round(baseline_l, 2),
                "litres_saved": round(litres_saved, 2),
                "percent_saved": round(percent_saved, 1),
                "chemical_inr_saved": round(chemical_inr),
                "labour_inr_saved": round(labour_inr),
                "inr_saved": round(chemical_inr + labour_inr),
                "litres_used_per_acre": round(used_pa, 2),
                "litres_saved_per_acre": round(saved_pa, 2),
                "inr_saved_per_acre": round(inr_pa),
            }

    def format_summary(self, lang: str = "en",
                       include_season: bool = False) -> str:
        """Farmer-facing 3-4 line message for Telegram/WhatsApp.

        This string IS the product output (§1.3: farmers don't want
        dashboards).  ``lang="hi"`` gives simple Devanagari phrasing.
        """
        s = self.summary()
        tot = None
        if include_season:
            others = [m for m in self.load_history(self.path)
                      if m.get("mission_id") != self.mission_id]
            tot = self._sum(others + [s])
        if lang == "hi":
            lines = [
                f"आज खेत में: {s['area_acres']:.2f} एकड़ कवर, "
                f"{s['sprays']} खरपतवार पर छिड़काव",
                f"दवा लगी {s['litres_used']:.1f} लीटर, पूरे छिड़काव के "
                f"{s['baseline_litres']:.1f} लीटर की जगह",
                f"बचत: {s['litres_saved']:.1f} लीटर दवा "
                f"({s['percent_saved']:.0f}%), ₹{s['inr_saved']}",
            ]
            if tot is not None:
                lines.append(f"इस सीज़न में कुल: {tot['litres_saved']:.1f} लीटर, "
                             f"₹{tot['inr_saved']} की बचत")
        else:
            lines = [
                f"Today in the field: {s['area_acres']:.2f} acre covered, "
                f"{s['sprays']} weeds sprayed",
                f"Chemical used {s['litres_used']:.1f} L instead of "
                f"{s['baseline_litres']:.1f} L blanket spray",
                f"Saved: {s['litres_saved']:.1f} L "
                f"({s['percent_saved']:.0f}%), ₹{s['inr_saved']}",
            ]
            if tot is not None:
                lines.append(f"Season total: {tot['litres_saved']:.1f} L saved, "
                             f"₹{tot['inr_saved']}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Persistence (JSONL mission history)
    # ------------------------------------------------------------------

    def save(self) -> dict:
        """Append the mission summary as one JSON line; returns the dict.

        Safe to call more than once per mission (checkpointing): reload
        dedupes on ``mission_id``, keeping the latest line.
        """
        s = self.summary()
        s["t_saved"] = round(time.time(), 3)
        try:
            d = os.path.dirname(self.path)
            if d:
                os.makedirs(d, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(s, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")
        except OSError as exc:
            logger.warning("SavingsTracker: save to %s failed (%s)",
                           self.path, exc)
        self._last_autosave = time.time()
        return s

    def _maybe_autosave(self) -> None:
        if (self.autosave_interval_s > 0
                and time.time() - self._last_autosave >= self.autosave_interval_s):
            self.save()

    @classmethod
    def load_history(cls, path: str) -> list[dict]:
        """Past mission summaries, oldest first, deduped by mission_id
        (latest line wins).  Corrupt/blank lines are skipped."""
        if not os.path.exists(path):
            return []
        by_id: dict[str, dict] = {}
        order: list[str] = []
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for i, line in enumerate(fh):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        logger.debug("SavingsTracker: skipping corrupt line %d "
                                     "in %s", i + 1, path)
                        continue
                    if not isinstance(rec, dict):
                        continue
                    mid = rec.get("mission_id") or f"_line{i}"
                    if mid not in by_id:
                        order.append(mid)
                    by_id[mid] = rec
        except OSError as exc:
            logger.warning("SavingsTracker: cannot read %s (%s)", path, exc)
            return []
        return [by_id[m] for m in order]

    @classmethod
    def season_totals(cls, path: str) -> dict:
        """Season-to-date totals summed across the JSONL mission history."""
        return cls._sum(cls.load_history(path))

    @staticmethod
    def _sum(missions: list[dict]) -> dict:
        """Sum the provable numbers across mission summaries."""
        tot = {"missions": len(missions), "area_acres": 0.0, "sprays": 0,
               "litres_used": 0.0, "litres_saved": 0.0, "inr_saved": 0}
        for m in missions:
            tot["area_acres"] += float(m.get("area_acres", 0.0))
            tot["sprays"] += int(m.get("sprays", 0))
            tot["litres_used"] += float(m.get("litres_used", 0.0))
            tot["litres_saved"] += float(m.get("litres_saved", 0.0))
            tot["inr_saved"] += round(float(m.get("inr_saved", 0)))
        tot["area_acres"] = round(tot["area_acres"], 3)
        tot["litres_used"] = round(tot["litres_used"], 3)
        tot["litres_saved"] = round(tot["litres_saved"], 2)
        return tot
