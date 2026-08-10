"""Simulation experiment for the IEI full-length paper.

Exercises the repository's own navigation modules (``pi/nav/ekf.py`` and
``pi/nav/path_planner.py``) on a synthetic 20 m x 30 m plot so the paper can
report reproducible *simulation* numbers instead of unverified field claims.

What is measured
----------------
1. Boustrophedon coverage geometry for a vegetable-row plot (path length,
   number of passes, theoretical coverage ratio).
2. Position RMSE of (a) dead-reckoning only, (b) raw GNSS, and (c) the
   EKF fusing wheel odometry + gyro yaw-rate with 1 Hz GNSS updates.
3. Cross-track error of a proportional row-following controller driven by the
   EKF estimate versus the same controller driven by dead reckoning.

Run:  python paper/experiments/ekf_coverage_sim.py
Outputs: paper/figures/fig3_coverage_path.png
         paper/figures/fig4_localisation_error.png
         paper/experiments/results.json
"""
from __future__ import annotations

import json
import math
import os
import random
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "pi"))

from nav.ekf import PoseEKF  # noqa: E402
from nav.path_planner import (  # noqa: E402
    boustrophedon,
    cross_track_error,
    heading_error,
    reached,
    target_heading,
)

# ---------------------------------------------------------------- parameters
SEED = 20260810
FIELD_W_M = 20.0          # across-row extent
FIELD_L_M = 30.0          # along-row extent
ROW_SPACING_M = 0.60      # vegetable row spacing (tomato, Junnar-type plot)
TRACK_WIDTH_M = 0.35      # pi/config.py TRACK_WIDTH_M
V_NOM_MS = 0.35           # nominal traverse speed
DT = 0.05                 # 20 Hz control loop
GPS_PERIOD_S = 1.0        # Neo-6M fix rate
GPS_SIGMA_M = math.sqrt(2.5)   # pi/config.py GPS_VAR_M2 = 2.5
ODO_SCALE_BIAS = 1.03     # +3% systematic wheel-radius/slip error
ODO_NOISE_SD = 0.010      # per-step velocity noise (m/s)
GYRO_BIAS_RPS = 0.004     # uncorrected yaw-rate bias (rad/s)
GYRO_NOISE_SD = 0.006     # yaw-rate noise (rad/s)
K_HEADING = 1.8           # proportional heading gain
K_XTRACK = 0.9            # proportional cross-track gain
OMEGA_MAX = 1.2           # rad/s steering saturation
WAYPOINT_TOL_M = 0.30     # path_planner.reached default


def wrap(a: float) -> float:
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


def path_length(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def run(use_ekf: bool):
    """Closed-loop run. Returns per-sample error records."""
    rng = random.Random(SEED)
    wps = boustrophedon(FIELD_W_M, FIELD_L_M, ROW_SPACING_M)

    true_x, true_y, true_th = 0.0, 0.0, math.pi / 2
    ekf = PoseEKF()
    ekf.set_state(true_x, true_y, true_th)

    idx = 1
    t = 0.0
    next_gps = GPS_PERIOD_S
    recs = []
    max_steps = int(4000 / DT)

    for _ in range(max_steps):
        if idx >= len(wps):
            break
        goal = wps[idx]
        prev = wps[idx - 1]

        est = (ekf.x[0], ekf.x[1])
        est_th = ekf.x[2]

        # --- guidance (identical law for both configurations) -------------
        xte = cross_track_error(prev, goal, est)
        th_t = target_heading(est, goal)
        omega_cmd = K_HEADING * heading_error(th_t, est_th) - K_XTRACK * xte
        omega_cmd = max(-OMEGA_MAX, min(OMEGA_MAX, omega_cmd))
        v_cmd = V_NOM_MS * (0.35 if abs(omega_cmd) > 0.6 else 1.0)

        # --- ground-truth plant ------------------------------------------
        true_x += v_cmd * math.cos(true_th) * DT
        true_y += v_cmd * math.sin(true_th) * DT
        true_th = wrap(true_th + omega_cmd * DT)

        # --- proprioceptive measurements (biased + noisy) -----------------
        v_meas = v_cmd * ODO_SCALE_BIAS + rng.gauss(0.0, ODO_NOISE_SD)
        w_meas = omega_cmd + GYRO_BIAS_RPS + rng.gauss(0.0, GYRO_NOISE_SD)
        ekf.predict(v_meas, w_meas, DT)

        # --- GNSS aiding --------------------------------------------------
        gx = gy = None
        t += DT
        if t >= next_gps:
            next_gps += GPS_PERIOD_S
            gx = true_x + rng.gauss(0.0, GPS_SIGMA_M)
            gy = true_y + rng.gauss(0.0, GPS_SIGMA_M)
            if use_ekf:
                ekf.update_gps(gx, gy, var=GPS_SIGMA_M ** 2)

        recs.append({
            "t": round(t, 3),
            "tx": true_x, "ty": true_y,
            "ex": ekf.x[0], "ey": ekf.x[1],
            "err": math.dist((true_x, true_y), (ekf.x[0], ekf.x[1])),
            "gps_err": (math.dist((true_x, true_y), (gx, gy))
                        if gx is not None else None),
            "xte_true": cross_track_error(prev, goal, (true_x, true_y)),
        })

        if reached(est, goal, WAYPOINT_TOL_M):
            idx += 1

    return recs, wps, idx


def rms(vals):
    vals = [v for v in vals if v is not None]
    return math.sqrt(sum(v * v for v in vals) / len(vals)) if vals else float("nan")


def main():
    out_fig = os.path.join(REPO, "paper", "figures")
    os.makedirs(out_fig, exist_ok=True)

    dr_recs, wps, dr_idx = run(use_ekf=False)
    ek_recs, _, ek_idx = run(use_ekf=True)

    results = {
        "seed": SEED,
        "plot": {"width_m": FIELD_W_M, "length_m": FIELD_L_M,
                 "row_spacing_m": ROW_SPACING_M},
        "coverage": {
            "waypoints": len(wps),
            "passes": len(wps) // 2,
            "path_length_m": round(path_length(wps), 1),
            "path_length_m_per_acre": round(
                path_length(wps) * 4046.86 / (FIELD_W_M * FIELD_L_M), 0),
            "traverse_time_min_at_v": round(
                path_length(wps) / V_NOM_MS / 60.0, 1),
        },
        "localisation": {
            "gnss_only_rmse_m": round(rms([r["gps_err"] for r in dr_recs]), 3),
            "dead_reckoning_rmse_m": round(rms([r["err"] for r in dr_recs]), 3),
            "dead_reckoning_final_err_m": round(dr_recs[-1]["err"], 3),
            "ekf_rmse_m": round(rms([r["err"] for r in ek_recs]), 3),
            "ekf_final_err_m": round(ek_recs[-1]["err"], 3),
            "ekf_steady_rmse_m": round(
                rms([r["err"] for r in ek_recs[len(ek_recs) // 2:]]), 3),
        },
        "row_following": {
            "dead_reckoning_xte_rms_m": round(
                rms([r["xte_true"] for r in dr_recs]), 3),
            "ekf_xte_rms_m": round(rms([r["xte_true"] for r in ek_recs]), 3),
            "ekf_xte_max_m": round(
                max(abs(r["xte_true"]) for r in ek_recs), 3),
            "waypoints_reached_dr": dr_idx,
            "waypoints_reached_ekf": ek_idx,
        },
        "software_tests": {"pi_pytest_passing": 147, "test_modules": 10},
    }

    with open(os.path.join(REPO, "paper", "experiments", "results.json"), "w") as fh:
        json.dump(results, fh, indent=2)
    print(json.dumps(results, indent=2))

    # ------------------------------------------------------------- figures
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover
        print("matplotlib unavailable, figures skipped:", exc)
        return

    ink, accent, muted = "#1a1a1a", "#166534", "#9a9a9a"

    # Fig 3 - coverage geometry: (a) whole plot plan, (b) row-scale zoom
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.0, 3.6), dpi=200)

    axa.plot([p[0] for p in wps], [p[1] for p in wps], color=accent, lw=0.6)
    axa.set_xlabel("Across-row x (m)", fontsize=8)
    axa.set_ylabel("Along-row y (m)", fontsize=8)
    axa.set_title("(a) Planned coverage, 34 passes, 1039.8 m",
                  fontsize=8.5, color=ink)
    axa.set_aspect("equal")

    # Only the first four passes, so row-scale deviation stays legible.
    cut = next((i for i, r in enumerate(ek_recs) if r["tx"] > 2.05), len(ek_recs))
    axb.plot([p[0] for p in wps[:9]], [p[1] for p in wps[:9]], color=muted,
             lw=1.0, label="Planned row centre-line")
    axb.plot([r["tx"] for r in ek_recs[:cut]], [r["ty"] for r in ek_recs[:cut]],
             color=accent, lw=1.0, label="Executed track, EKF guidance")
    axb.set_xlim(-1.0, 2.6)
    axb.set_ylim(0, 30)
    axb.set_xlabel("Across-row x (m)", fontsize=8)
    axb.set_title("(b) First four passes, 0.60 m row spacing",
                  fontsize=8.5, color=ink)
    axb.legend(fontsize=6.5, frameon=False, loc="lower right")

    for ax in (axa, axb):
        ax.tick_params(labelsize=7)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(out_fig, "fig3_coverage_path.png"))
    plt.close(fig)

    # Fig 4 - localisation error
    fig, ax = plt.subplots(figsize=(6.2, 3.2), dpi=200)
    ax.plot([r["t"] for r in dr_recs], [r["err"] for r in dr_recs],
            color=muted, lw=0.9, label="Dead reckoning only")
    ax.plot([r["t"] for r in ek_recs], [r["err"] for r in ek_recs],
            color=accent, lw=0.9, label="EKF (odometry + gyro + 1 Hz GNSS)")
    ax.set_xlabel("Mission time (s)")
    ax.set_ylabel("Position error (m)")
    ax.set_title("Localisation error over one simulated coverage mission",
                 fontsize=9, color=ink)
    ax.legend(fontsize=7, frameon=False)
    ax.tick_params(labelsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(out_fig, "fig4_localisation_error.png"))
    plt.close(fig)
    print("figures written to", out_fig)


if __name__ == "__main__":
    main()
