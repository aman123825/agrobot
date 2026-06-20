"""Streamlit dashboard (BOM #103).

Reads the dated field-log CSV produced by pipeline/pathway_stream.py and renders
live metrics, an NPK time-series, a GPS map of readings, and an anomaly table.

Run:  streamlit run pi/dashboard/app.py
"""
from __future__ import annotations

import glob
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


def main() -> None:
    st.set_page_config(page_title="AgriRover", layout="wide")
    st.title("AgriRover - Field Dashboard")

    csv_dir = os.getenv("FIELD_LOG_DIR", ".")
    path = _latest_csv(csv_dir)

    if not path:
        st.info("No field_log_*.csv yet. Start pipeline/pathway_stream.py to collect data.")
        st.caption(f"Looking in: {os.path.abspath(csv_dir)}")
        return

    df = _load(path)
    if df is None or len(df) == 0:
        st.warning(f"Found {os.path.basename(path)} but could not read rows (pandas required).")
        return

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


if __name__ == "__main__":
    main()
