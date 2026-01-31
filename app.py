import streamlit as st
import pandas as pd
from utils.analysis import analyze_laps, driving_stats

# ------------------------------
# PAGE CONFIG
# ------------------------------
st.set_page_config(
    page_title="FueledFast Telemetry",
    page_icon="🏎️",
    layout="wide"
)

# ------------------------------
# SIDEBAR
# ------------------------------
st.sidebar.title("🔥 FueledFast – AI Race Engineering")
st.sidebar.write("Multi-Lap Telemetry MVP")
st.sidebar.write("Mode: Analysis Core")
st.sidebar.markdown("---")
st.sidebar.success("✅ MVP Active")

# ------------------------------
# MAIN TITLE
# ------------------------------
st.title("🏎️ FueledFast Multi-Lap Telemetry")
st.subheader("Upload multiple laps and compare them like a race engineer")
st.markdown("---")

# ------------------------------
# MULTI-LAP UPLOAD
# ------------------------------
uploaded_files = st.file_uploader(
    "Upload lap CSV files",
    type=["csv"],
    accept_multiple_files=True
)

if not uploaded_files or len(uploaded_files) < 2:
    st.info("Upload **at least two laps** to begin analysis.")
    st.stop()

# ------------------------------
# LOAD LAPS
# ------------------------------
laps = {file.name: pd.read_csv(file) for file in uploaded_files}
lap_names = list(laps.keys())

# ------------------------------
# LAP SELECTION
# ------------------------------
st.markdown("## 🔁 Lap Comparison")

col1, col2 = st.columns(2)
with col1:
    ref_name = st.selectbox("Reference Lap", lap_names, index=0)
with col2:
    cmp_name = st.selectbox("Comparison Lap", lap_names, index=1)

ref_lap = laps[ref_name]
cmp_lap = laps[cmp_name]

st.success(f"Comparing **{ref_name}** vs **{cmp_name}**")

# ------------------------------
# ANALYSIS
# ------------------------------
processed, insights = analyze_laps(ref_lap, cmp_lap)
ref_stats = driving_stats(ref_lap)
cmp_stats = driving_stats(cmp_lap)

# ------------------------------
# RESULTS — STATS
# ------------------------------
st.markdown("---")
st.subheader("📊 Driving Behavior Analysis")

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"### {ref_name}")
    st.json(ref_stats)

with c2:
    st.markdown(f"### {cmp_name}")
    st.json(cmp_stats)

# ------------------------------
# DELTA GRAPH
# ------------------------------
st.markdown("---")
st.subheader("📉 Time Delta vs Distance")
st.line_chart(
    processed.set_index("distance")["delta_time"]
)


st.write(f"**Average Delta:** {insights['avg_delta']} s")
st.write(f"**Max Time Lost:** {insights['max_loss']} s")
st.write(f"**Distance of Max Loss:** {insights['distance_of_max_loss']} m")

# ------------------------------
# TELEMETRY CHANNELS
# ------------------------------
st.markdown("---")
st.subheader("📈 Telemetry Channels")

for channel in ["speed", "throttle", "brake"]:
    if channel in ref_lap.columns:
        st.write(f"### {channel.capitalize()}")
        st.line_chart(
            pd.DataFrame({
                "Reference": ref_lap[channel],
                "Comparison": cmp_lap[channel]
            })
        )

# ------------------------------
# FOOTER
# ------------------------------
st.markdown("---")
st.caption("FueledFast Telemetry • MVP Core • © Creao AI")
