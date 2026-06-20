"""Streamlit dashboard (BOM #103).

Reads the dated field-log CSV produced by pipeline/pathway_stream.py and renders
live metrics, an NPK time-series, a GPS map of readings, and an anomaly table.
Also displays per-plant health history from the PlantDB.

Run:  streamlit run pi/dashboard/app.py
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime, timezone

import streamlit as st


def _latest_csv(csv_dir: str = ".") -> str | None:
    files = sorted(glob.glob(os.path.join(csv_dir, "field_log_*.csv")))
    return files[-1] if files else None


def _load(path: str):
    try:
        import pandas as pd

        return pd.read_csv(path)
    except Exception:
        return None


def _load_plant_db(path: str) -> dict:
    """Load plant DB JSON file, return plants dict or empty."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get("plants", {})
    except (json.JSONDecodeError, OSError):
        return {}


def _render_plant_section(plants: dict) -> None:
    """Render the per-plant health history section."""
    st.subheader("Plant Health Database")
    st.metric("Tracked Plants", len(plants))

    if not plants:
        st.caption("No plants tracked yet. Run the rover to start building the database.")
        return

    # Recent observations across all plants
    all_obs: list[dict] = []
    for pid, rec in plants.items():
        for obs in rec.get("observations", []):
            all_obs.append({"plant_id": pid, "lat": rec["lat"],
                            "lng": rec["lng"], **obs})
    all_obs.sort(key=lambda o: o.get("ts", 0), reverse=True)

    st.write(f"**Total observations:** {len(all_obs)}")

    if all_obs:
        st.write("**Recent observations** (newest first):")
        display_obs = all_obs[:20]
        for obs in display_obs:
            ts_str = datetime.fromtimestamp(
                obs.get("ts", 0), tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M UTC")
            conf_pct = obs.get("confidence", 0) * 100
            notes = f" | {obs['notes']}" if obs.get("notes") else ""
            st.text(
                f"  {obs['plant_id']} | {ts_str} | "
                f"{obs.get('disease_class', '?')} ({conf_pct:.0f}%){notes}"
            )

    # Health trend for plants with multiple observations
    multi_obs = {pid: rec for pid, rec in plants.items()
                 if len(rec.get("observations", [])) > 1}
    if multi_obs:
        st.subheader("Health Trends (plants with multiple visits)")
        selected = st.selectbox(
            "Select plant",
            options=list(multi_obs.keys()),
            format_func=lambda pid: (
                f"{pid} ({len(multi_obs[pid]['observations'])} obs)"
            ),
        )
        if selected:
            trend = multi_obs[selected]["observations"]
            st.write(f"Location: ({multi_obs[selected]['lat']:.6f}, "
                     f"{multi_obs[selected]['lng']:.6f})")
            try:
                import pandas as pd

                rows = []
                for obs in trend:
                    rows.append({
                        "time": datetime.fromtimestamp(
                            obs["ts"], tz=timezone.utc
                        ).strftime("%m-%d %H:%M"),
                        "disease": obs.get("disease_class", "?"),
                        "confidence": obs.get("confidence", 0),
                    })
                df_trend = pd.DataFrame(rows)
                st.dataframe(df_trend)
                st.line_chart(df_trend.set_index("time")[["confidence"]])
            except ImportError:
                for obs in trend:
                    ts_str = datetime.fromtimestamp(
                        obs["ts"], tz=timezone.utc
                    ).strftime("%m-%d %H:%M")
                    st.text(f"  {ts_str}: {obs.get('disease_class', '?')} "
                            f"({obs.get('confidence', 0) * 100:.0f}%)")


def main() -> None:
    st.set_page_config(page_title="AgriRover", layout="wide")
    st.title("AgriRover - Field Dashboard")

    csv_dir = os.getenv("FIELD_LOG_DIR", ".")
    path = _latest_csv(csv_dir)

    if not path:
        st.info("No field_log_*.csv yet. Start pipeline/pathway_stream.py to collect data.")
        st.caption(f"Looking in: {os.path.abspath(csv_dir)}")
    else:
        df = _load(path)
        if df is None or len(df) == 0:
            st.warning(f"Found {os.path.basename(path)} but could not read rows (pandas required).")
        else:
            last = df.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Nitrogen (N)", f"{last.get('n', 0):.0f} mg/kg")
            c2.metric("Phosphorus (P)", f"{last.get('p', 0):.0f} mg/kg")
            c3.metric("Potassium (K)", f"{last.get('k', 0):.0f} mg/kg")
            c4.metric("pH", f"{last.get('ph', 0):.2f}")

            st.caption(
                f"Source: {os.path.basename(path)} | {len(df)} readings | "
                f"updated {datetime.now(tz=timezone.utc).strftime('%H:%M:%S UTC')}"
            )

            st.subheader("NPK over time")
            cols = [c for c in ("n", "p", "k") if c in df.columns]
            if cols:
                st.line_chart(df[cols])

            st.subheader("Reading locations")
            geo = df[(df.get("gps_fix", 0) == 1)] if "gps_fix" in df.columns else df
            if {"lat", "lng"}.issubset(geo.columns) and len(geo) > 0:
                st.map(geo.rename(columns={"lng": "lon"})[["lat", "lon"]])
            else:
                st.caption("No GPS-fixed readings to plot yet.")

            st.subheader("Anomalies")
            anom_cols = [c for c in df.columns if c.endswith("_anomaly")]
            if anom_cols:
                mask = df[anom_cols].any(axis=1)
                flagged = df[mask]
                st.write(f"{len(flagged)} flagged reading(s).")
                if len(flagged) > 0:
                    st.dataframe(flagged.tail(50))
            else:
                st.caption("No anomaly columns in log.")

    # --- Plant Health History Section ---
    st.divider()
    plant_db_path = os.getenv("PLANT_DB_PATH", "plant_db.json")
    plants = _load_plant_db(plant_db_path)
    _render_plant_section(plants)


if __name__ == "__main__":
    main()
