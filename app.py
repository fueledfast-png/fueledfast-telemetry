import streamlit as st
import pandas as pd

from utils.validate import validate_csv
from utils.distance import ensure_distance
from utils.distance_delta import distance_delta
from utils.sectors import sector_deltas
from utils.corners import detect_corners, match_corner_deltas
from utils.overlays import extract_corner_segment
from utils.plots import plot_distance_delta, plot_throttle_brake

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp { background-color:#0B0E14; color:#E5E7EB; }
[data-testid="stSidebar"] { background:#111827; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="color:#3B82F6;">AeroLap</h1>
<p style="color:#9CA3AF;">Professional lap comparison</p>
""", unsafe_allow_html=True)

# ---------------- Upload ----------------
lap_a_file = st.file_uploader("Upload Lap A CSV", type="csv")
lap_b_file = st.file_uploader("Upload Lap B CSV", type="csv")

if lap_a_file and lap_b_file:
    lap_a = pd.read_csv(lap_a_file)
    lap_b = pd.read_csv(lap_b_file)

    try:
        validate_csv(lap_a)
        validate_csv(lap_b)
    except Exception as e:
        st.error(str(e))
        st.stop()

    lap_a = ensure_distance(lap_a)
    lap_b = ensure_distance(lap_b)

    min_len = min(len(lap_a), len(lap_b))
    lap_a = lap_a.iloc[:min_len]
    lap_b = lap_b.iloc[:min_len]

    # -------- Distance Delta --------
    st.subheader("📏 Distance Delta")
    dist, delta = distance_delta(lap_a, lap_b)
    st.plotly_chart(plot_distance_delta(dist, delta), use_container_width=True)

    # -------- Sectors --------
    st.subheader("⏱ Sector Deltas")
    st.dataframe(sector_deltas(lap_a, lap_b), use_container_width=True)

    # -------- Corners --------
    st.subheader("📐 Corner Deltas")
    c1 = detect_corners(lap_a)
    c2 = detect_corners(lap_b)
    deltas = match_corner_deltas(c1, c2)
    st.dataframe(deltas, use_container_width=True)

    # -------- Overlays --------
    st.subheader("🧩 Corner Overlays")
    corner_id = st.selectbox("Select Corner", deltas["Corner"])

    seg_a = extract_corner_segment(lap_a, c1.iloc[corner_id - 1])
    seg_b = extract_corner_segment(lap_b, c2.iloc[corner_id - 1])

    st.plotly_chart(
        plot_throttle_brake(seg_a, seg_b),
        use_container_width=True
    )
