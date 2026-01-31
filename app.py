import streamlit as st
import pandas as pd
from utils.analysis import (
    align_laps,
    compute_delta,
    compute_sector_deltas,
    detect_corners,
    match_corners
)
import matplotlib.pyplot as plt

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="FueledFast Telemetry",
    page_icon="🏎️",
    layout="wide"
)

# -------------------------------------------------
# COLOR SCHEME
# -------------------------------------------------
PRIMARY_COLOR = "#FF4C29"
SECONDARY_COLOR = "#1F2937"
BACKGROUND_COLOR = "#F9FAFB"
TEXT_COLOR = "#111827"
POSITIVE_COLOR = "#10B981"
NEGATIVE_COLOR = "#EF4444"

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown(
    f"""
    <div style='background-color:{PRIMARY_COLOR};padding:15px;border-radius:8px'>
        <h1 style='color:white;text-align:center;font-family:Roboto'>🏎️ FueledFast Telemetry</h1>
        <p style='color:white;text-align:center;font-size:16px;font-family:Roboto'>
        Multi-Lap Telemetry Analysis – Distance, Sector & Corner Deltas
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------
# INFO CARDS
# -------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Multi-Lap Upload", "✅", "Compare multiple laps at once")
col2.metric("Corner Detection", "✅", "Brake & Min Speed logic")
col3.metric("Sector Deltas", "✅", "Distance-based sector breakdown")

st.markdown("---")

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
st.subheader("Upload Telemetry Files")
files = st.file_uploader(
    "Upload CSV telemetry files (iRacing, ACC, AC, Karting...)",
    type=["csv"],
    accept_multiple_files=True
)

if not files or len(files) < 2:
    st.info("Upload at least two laps to start analyzing.")
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
sector_count = st.slider("Number of sectors", 2, 6, 3)
sector_df = compute_sector_deltas(ref, cmp, sector_count)
st.dataframe(sector_df, use_container_width=True)

# -------------------------------------------------
# CORNER ANALYSIS
# -------------------------------------------------
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
    corner_df = pd.DataFrame()

# -------------------------------------------------
# CORNER DELTA PLOTS
# -------------------------------------------------
if not corner_df.empty:
    st.subheader("📊 Corner Delta Plot")
    fig, ax = plt.subplots(figsize=(10, 4))
    x = corner_df["Corner"]

    # Lines for Ref vs Comp
    ax.plot(x, corner_df["Ref Time"], marker='o', color=PRIMARY_COLOR, label="Ref Time")
    ax.plot(x, corner_df["Cmp Time"], marker='o', color=SECONDARY_COLOR, label="Cmp Time")

    # Color bars for delta
    colors = [POSITIVE_COLOR if d < 0 else NEGATIVE_COLOR for d in corner_df["Delta (s)"]]
    ax.bar(x, corner_df["Delta (s)"], alpha=0.5, color=colors, label="Delta (s)")

    ax.set_xlabel("Corner Number")
    ax.set_ylabel("Time (s)")
    ax.set_title("Corner Times & Delta Comparison")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

# -------------------------------------------------
# SUMMARY
# -------------------------------------------------
st.markdown("---")
st.subheader("📊 Lap Summary")
c1, c2, c3 = st.columns(3)
c1.metric("Avg Delta (s)", round(ref["delta_time"].mean(), 4))
c2.metric("Max Loss (s)", round(ref["delta_time"].max(), 4))
c3.metric("Corners", len(ref_corners))
