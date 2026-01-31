import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.analysis import (
    align_laps,
    compute_delta,
    compute_sector_deltas,
    detect_corners,
    match_corners
)

# -------------------------------------------------
# PAGE SETUP
# -------------------------------------------------
st.set_page_config(page_title="FueledFast Telemetry", layout="wide")

st.sidebar.title("🔥 FueledFast Telemetry")
st.sidebar.caption("Telemetry Analysis MVP")

st.title("🏎️ Telemetry Comparison Tool")
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
    st.info("Upload at least two lap files.")
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
    cmp_name = st.selectbox(
        "Comparison Lap",
        [n for n in names if n != ref_name]
    )

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
    corner_df = pd.DataFrame()  # empty fallback

# -------------------------------------------------
# CORNER DELTA PLOTS
# -------------------------------------------------
if not corner_df.empty:
    st.subheader("📊 Corner Delta Plot")

    fig, ax = plt.subplots(figsize=(10, 4))
    x = corner_df["Corner"]

    # Plot reference vs comparison
    ax.plot(x, corner_df["Ref Time"], marker='o', label="Ref Corner Time")
    ax.plot(x, corner_df["Cmp Time"], marker='o', label="Cmp Corner Time")

    # Plot delta
    ax.bar(x, corner_df["Delta (s)"], alpha=0.3, color='red', label="Delta (s)")

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
