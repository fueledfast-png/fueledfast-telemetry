import streamlit as st
import pandas as pd

from utils.distance_delta import distance_based_delta
from utils.sectors import compute_sector_deltas

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
st.sidebar.write("Professional lap comparison")
st.sidebar.markdown("---")
st.sidebar.write("Distance-based deltas • Sector analysis")

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("🏎️ AeroLap – Distance-Based Lap Analysis")
st.write("Upload **at least two lap CSV files** to compare like a race engineer.")

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
laps = {}
for f in uploaded_files:
    laps[f.name] = pd.read_csv(f)

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
# DISTANCE-BASED DELTA
# --------------------------------------------------
delta_df = distance_based_delta(lap_a, lap_b)

# --------------------------------------------------
# SECTOR DELTAS
# --------------------------------------------------
st.markdown("---")
st.subheader("⏱ Sector Time Deltas")

num_sectors = st.selectbox(
    "Number of sectors",
    options=[3, 4, 5],
    index=0
)

sector_df = compute_sector_deltas(delta_df, num_sectors)

st.dataframe(
    sector_df,
    use_container_width=True
)

# --------------------------------------------------
# DELTA PLOT
# --------------------------------------------------
st.markdown("---")
st.subheader("📉 Time Delta vs Distance")

st.line_chart(
    delta_df.set_index("distance")["delta_time"]
)

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------
st.markdown("### Summary")

st.write(f"**Total Delta:** {delta_df['delta_time'].iloc[-1]:.3f} s")
st.write(f"**Average Delta:** {delta_df['delta_time'].mean():.3f} s")

# --------------------------------------------------
# TELEMETRY OVERLAYS
# --------------------------------------------------
st.markdown("---")
st.subheader("📊 Telemetry Overlays")

def overlay(channel):
    if channel in lap_a.columns and channel in lap_b.columns:
        st.line_chart(pd.DataFrame({
            lap_a_name: lap_a[channel],
            lap_b_name: lap_b[channel]
        }))

overlay("speed")
overlay("throttle")
overlay("brake")
overlay("steering")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption("AeroLap by FueledFast • Engineer-grade lap analysis")
