import streamlit as st
import pandas as pd

from utils.analysis import (
    align_laps,
    compute_delta,
    interpolate_channel
)

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(
    page_title="FueledFast Telemetry",
    layout="wide"
)

st.sidebar.title("🔥 FueledFast Telemetry")
st.sidebar.caption("Distance-Based Lap Analysis")

st.title("🏎️ Telemetry Comparison Dashboard")
st.markdown("---")

# -----------------------------
# FILE UPLOAD
# -----------------------------
files = st.file_uploader(
    "Upload telemetry CSV files",
    type=["csv"],
    accept_multiple_files=True
)

if not files or len(files) < 2:
    st.info("Upload at least 2 laps to begin.")
    st.stop()

laps = {}
for f in files:
    df = pd.read_csv(f)
    laps[f.name] = df

lap_names = list(laps.keys())

# -----------------------------
# LAP SELECTION
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    ref_name = st.selectbox("Reference Lap (Gold)", lap_names)

with col2:
    cmp_name = st.selectbox(
        "Comparison Lap",
        [n for n in lap_names if n != ref_name]
    )

ref_lap = laps[ref_name]
cmp_lap = laps[cmp_name]

# -----------------------------
# ALIGN + DELTA
# -----------------------------
ref_aligned, cmp_aligned = align_laps(ref_lap, cmp_lap)
ref_processed = compute_delta(ref_aligned, cmp_aligned)

# -----------------------------
# DELTA CHART
# -----------------------------
st.subheader("📉 Delta Time vs Distance")

delta_df = ref_processed.set_index("distance")["delta_time"]
st.line_chart(delta_df)

# -----------------------------
# SPEED OVERLAY
# -----------------------------
st.subheader("📈 Speed Overlay")

cmp_speed = interpolate_channel(ref_processed, cmp_aligned, "speed")

speed_df = pd.DataFrame({
    ref_name: ref_processed["speed"],
    cmp_name: cmp_speed
}, index=ref_processed["distance"])

st.line_chart(speed_df)

# -----------------------------
# THROTTLE / BRAKE OVERLAYS
# -----------------------------
st.subheader("🦶 Throttle & Brake Overlays")

tabs = st.tabs(["Throttle", "Brake"])

for tab, channel in zip(tabs, ["throttle", "brake"]):
    with tab:
        cmp_channel = interpolate_channel(ref_processed, cmp_aligned, channel)

        if channel not in ref_processed.columns or cmp_channel is None:
            st.warning(f"{channel.capitalize()} data not available.")
            continue

        overlay_df = pd.DataFrame({
            ref_name: ref_processed[channel],
            cmp_name: cmp_channel
        }, index=ref_processed["distance"])

        st.line_chart(overlay_df)

# -----------------------------
# SUMMARY METRICS
# -----------------------------
st.markdown("---")
st.subheader("📊 Lap Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Average Delta (s)",
        round(ref_processed["delta_time"].mean(), 4)
    )

with col2:
    st.metric(
        "Max Time Loss (s)",
        round(ref_processed["delta_time"].max(), 4)
    )

with col3:
    st.metric(
        "Lap Distance (m)",
        round(ref_processed["distance"].max(), 1)
    )
