"""Streamlit dashboard (BOM #103).

Shows: live GPS field map (Folium/Pydeck), NPK heatmap, moisture gradient,
dosing event log, camera stream, and battery status - updating in real time
from the Pathway output.

Run:  streamlit run pi/dashboard/app.py
"""
from __future__ import annotations

import streamlit as st


def main() -> None:
    st.set_page_config(page_title="AgriRover", layout="wide")
    st.title("AgriRover - Field Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Battery", "-- %")
    col2.metric("Mode", "--")
    col3.metric("GPS Fix", "--")

    st.subheader("NPK Heatmap")
    st.info("TODO: render Folium map with GPS-colored NPK overlay from Pathway.")

    st.subheader("Camera Stream")
    st.info("TODO: embed MJPEG stream from Pi Camera / ESP32-CAM.")

    st.subheader("Dosing Event Log")
    st.info("TODO: tail field_log_*.csv.")


if __name__ == "__main__":
    main()
