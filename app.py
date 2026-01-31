import streamlit as st
import pandas as pd

from utils.analysis import (
    align_laps,
    compute_delta,
    compute_sector_deltas,
    detect_corners,
    match_corners
)

from utils.ai_engineer import generate_ai_report

# -------------------------------------------------
# PAGE SETUP
# -------------------------------------------------
st.set_page_config(page_title="FueledFast Telemetry", layout="wide")

st.sidebar.title("🔥 FueledFast Telemetry")
st.sidebar.caption("Race Engineering Analysis")

st.title("🏎️ Telemetry Comparison")
st.markdown("---")

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
files = st.file_uploader(
    "Upload telemetry CSV files",
    type=["csv"],
    accept_multiple_files=True
)

if not files or len(files) < 2:
    st.info("Upload at least two laps.")
    st.stop()

laps = {f.name: pd.read_csv(f) for f in files}
names = list(laps.keys())

# -------------------------------------------------
# LAP SELECTION
# -------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    ref_name = st.selectbox("Reference Lap", names)
with col2:
    cmp_name = st.selectbox("Comparison Lap", [n for n in names if n != ref_name])

ref, cmp = align_laps(laps[ref_name], laps[cmp_name])
ref = compute_delta(ref, cmp)

# -------------------------------------------------
# DELTA PLOT
# -------------------------------------------------
st.subheader("📉 Delta Time vs Distance")
st.line_chart(ref.set_index("distance")["delta_time"])

# -------------------------------------------------
# SECTOR DELTAS
# -------------------------------------------------
st.subheader("🧩 Sector Deltas")
sectors = st.slider("Number of sectors", 2, 6, 3)

sector_df = compute_sector_deltas(ref, cmp, sectors)
st.dataframe(sector_df, use_container_width=True)

# -------------------------------------------------
# CORNER ANALYSIS
# -------------------------------------------------
st.markdown("---")
st.subheader("📐 Corner Analysis")

with st.expander("Corner Detection Settings"):
    brake_th = st.slider("Brake Threshold", 0.0, 1.0, 0.1)
    speed_drop = st.slider("Minimum Speed Drop", 2.0, 30.0, 8.0)
    window = st.slider("Corner Window (meters)", 10.0, 60.0, 25.0)

ref_corners = detect_corners(ref, brake_th, speed_drop, window)
cmp_corners = detect_corners(cmp, brake_th, speed_drop, window)

if not ref_corners.empty and not cmp_corners.empty:
    corner_df = match_corners(ref_corners, cmp_corners)
    st.dataframe(corner_df, use_container_width=True)
else:
    st.warning("No corners detected with current settings.")

# -------------------------------------------------
# LAP SUMMARY
# -------------------------------------------------
st.markdown("---")
st.subheader("📊 Lap Summary")

lap_summary = {
    "Average Delta (s)": round(ref["delta_time"].mean(), 4),
    "Maximum Time Loss (s)": round(ref["delta_time"].max(), 4),
    "Total Distance (m)": round(ref["distance"].max(), 1),
    "Corners Detected": len(ref_corners),
}

c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg Delta (s)", lap_summary["Average Delta (s)"])
c2.metric("Max Loss (s)", lap_summary["Maximum Time Loss (s)"])
c3.metric("Distance (m)", lap_summary["Total Distance (m)"])
c4.metric("Corners", lap_summary["Corners Detected"])

# -------------------------------------------------
# AI ENGINEER COACHING
# -------------------------------------------------
st.markdown("---")
st.subheader("🧠 AI Race Engineer Coaching")

enable_ai = st.toggle("Enable AI Engineer", value=True)

if enable_ai:
    with st.spinner("AI engineer reviewing telemetry..."):
        ai_report = generate_ai_report(
            lap_summary=lap_summary,
            sector_table=sector_df.to_string(index=False),
            corner_table=corner_df.to_string(index=False) if not ref_corners.empty else "No corners detected"
        )

    st.markdown(ai_report)

else:
    st.info("AI coaching disabled.")
