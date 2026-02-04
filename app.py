import streamlit as st
import pandas as pd

from utils.distance_delta import distance_based_delta

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
st.sidebar.write("Upload multiple laps and compare distance-based deltas.")

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
# RESULTS
# --------------------------------------------------
st.markdown("---")
st.subheader("📉 Time Delta vs Distance")

st.line_chart(
    delta_df.set_index("distance")["delta_time"]
)

# --------------------------------------------------
# BASIC STATS
# --------------------------------------------------
avg_delta = delta_df["delta_time"].mean()
max_loss = delta_df["delta_time"].max()

st.markdown("### Summary")
st.write(f"**Average Delta:** {avg_delta:.3f} s")
st.write(f"**Maximum Time Loss:** {max_loss:.3f} s")

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
st.caption("AeroLap by FueledFast • Built for serious drivers")
