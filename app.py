import streamlit as st
import pandas as pd

from utils.distance_delta import distance_based_delta
from utils.sectors import compute_sector_deltas
from utils.corners import (
    analyze_corners,
    match_corner_deltas,
    detect_corners,
    extract_corner_window
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AeroLap – Lap Analysis",
    layout="wide"
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.title("🟦 AeroLap")
st.sidebar.write("Engineer-grade lap analysis")
st.sidebar.markdown("---")
st.sidebar.write("Distance • Sectors • Corners")

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🏎️ AeroLap – Professional Lap Comparison")
st.write("Upload **at least two lap CSV files** to compare performance.")

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload lap CSV files",
    type=["csv"],
    accept_multiple_files=True
)

if not uploaded_files or len(uploaded_files) < 2:
    st.info("Upload at least two laps to begin.")
    st.stop()

# --------------------------------------------------
# LOAD LAPS
# --------------------------------------------------
laps = {f.name: pd.read_csv(f) for f in uploaded_files}
lap_names = list(laps.keys())

# --------------------------------------------------
# LAP SELECTION
# --------------------------------------------------
st.markdown("## 🔁 Select Laps")

col1, col2 = st.columns(2)
with col1:
    lap_a_name = st.selectbox("Reference Lap", lap_names, index=0)
with col2:
    lap_b_name = st.selectbox("Comparison Lap", lap_names, index=1)

lap_a = laps[lap_a_name]
lap_b = laps[lap_b_name]

st.success(f"Comparing **{lap_a_name}** vs **{lap_b_name}**")

# --------------------------------------------------
# DISTANCE DELTA
# --------------------------------------------------
delta_df = distance_based_delta(lap_a, lap_b)

# --------------------------------------------------
# SECTORS
# --------------------------------------------------
st.markdown("---")
st.subheader("⏱ Sector Time Deltas")

num_sectors = st.selectbox("Number of sectors", [3, 4, 5])
sector_df = compute_sector_deltas(delta_df, num_sectors)
st.dataframe(sector_df, use_container_width=True)

# --------------------------------------------------
# DELTA PLOT
# --------------------------------------------------
st.markdown("---")
st.subheader("📉 Time Delta vs Distance")
st.line_chart(delta_df.set_index("distance")["delta_time"])

# --------------------------------------------------
# CORNER ANALYSIS
# --------------------------------------------------
st.markdown("---")
st.subheader("📐 Corner Time Loss Analysis")

corners_a = analyze_corners(lap_a)
corners_b = analyze_corners(lap_b)

corner_deltas = match_corner_deltas(corners_a, corners_b)

st.dataframe(
    corner_deltas.sort_values("Time Δ (s)", ascending=False),
    use_container_width=True
)

# --------------------------------------------------
# CORNER OVERLAY SECTION
# --------------------------------------------------
st.markdown("---")
st.subheader("🧩 Corner Telemetry Overlay")

corner_indices_a = detect_corners(lap_a)
corner_indices_b = detect_corners(lap_b)

max_corners = min(len(corner_indices_a), len(corner_indices_b))

if max_corners == 0:
    st.warning("No corners detected in one or both laps.")
else:
    selected_corner = st.selectbox(
        "Select Corner",
        list(range(1, max_corners + 1))
    )

    idx = selected_corner - 1

    window_a = extract_corner_window(lap_a, corner_indices_a[idx])
    window_b = extract_corner_window(lap_b, corner_indices_b[idx])

    def overlay_channel(channel, title):
        if channel in window_a.columns and channel in window_b.columns:
            st.markdown(f"**{title}**")
            st.line_chart(pd.DataFrame({
                lap_a_name: window_a[channel],
                lap_b_name: window_b[channel]
            }))

    col1, col2 = st.columns(2)

    with col1:
        overlay_channel("speed", "Speed")

    with col2:
        overlay_channel("throttle", "Throttle")

    overlay_channel("brake", "Brake")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("AeroLap by FueledFast • Built like a race engineering tool")

