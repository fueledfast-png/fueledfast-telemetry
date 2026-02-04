import streamlit as st
import pandas as pd
import numpy as np

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="AeroLap • Lap Analysis",
    page_icon="🏎️",
    layout="wide"
)

# =====================================================
# GLOBAL STYLING (JET BLACK THEME)
# =====================================================
st.markdown("""
<style>
.stApp { background-color: #0B0E14; color: #E5E7EB; }
[data-testid="stSidebar"] { background-color: #111827; }
h1, h2, h3 { color: #E5E7EB; }
.accent-blue { color: #3B82F6; }
.accent-orange { color: #F97316; }
section[data-testid="stFileUploader"] {
    border: 1px dashed #3B82F6;
    padding: 1rem;
    border-radius: 10px;
}
.stButton button {
    background-color: #3B82F6;
    color: white;
    border-radius: 8px;
}
.stButton button:hover { background-color: #2563EB; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<h1>🟦 <span class="accent-blue">AeroLap</span></h1>
<p style="color:#9CA3AF; font-size:18px;">
Professional lap analysis for sim racers & drivers
</p>
<p class="accent-orange">
Compare laps using distance, sectors, braking & corner performance
</p>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.markdown("""
<h2 class="accent-blue">AeroLap</h2>
<p style="color:#9CA3AF;">FueledFast Performance Tools</p>
<hr style="border-color:#1F2937;">
<ul style="color:#E5E7EB;">
<li>📏 Distance Delta</li>
<li>⏱ Sector Analysis</li>
<li>📐 Corner Deltas</li>
<li>🧩 Brake / Speed Logic</li>
</ul>
""", unsafe_allow_html=True)

# =====================================================
# FILE UPLOAD
# =====================================================
st.markdown("## 📤 Upload Lap Files")

uploaded_files = st.file_uploader(
    "Upload CSV lap files (same track)",
    type=["csv"],
    accept_multiple_files=True
)

if not uploaded_files or len(uploaded_files) < 2:
    st.info("Upload **at least two lap CSV files** to begin analysis.")
    st.stop()

laps = {f.name: pd.read_csv(f) for f in uploaded_files}
lap_names = list(laps.keys())

# =====================================================
# LAP SELECTION
# =====================================================
st.markdown("## 🔁 Select Laps to Compare")

c1, c2 = st.columns(2)
with c1:
    lap_a_name = st.selectbox("Lap A", lap_names, index=0)
with c2:
    lap_b_name = st.selectbox("Lap B", lap_names, index=1)

lap_a = laps[lap_a_name].copy()
lap_b = laps[lap_b_name].copy()

# =====================================================
# REQUIRED COLUMNS CHECK
# =====================================================
required_cols = {"distance", "speed", "brake"}
for col in required_cols:
    if col not in lap_a.columns or col not in lap_b.columns:
        st.error(f"Missing required column: `{col}`")
        st.stop()

# =====================================================
# DISTANCE ALIGNMENT
# =====================================================
min_len = min(len(lap_a), len(lap_b))
lap_a = lap_a.iloc[:min_len]
lap_b = lap_b.iloc[:min_len]

lap_a["delta_time"] = lap_a["distance"] - lap_b["distance"]

# =====================================================
# DISTANCE-BASED DELTA
# =====================================================
st.markdown("## 📉 Distance Delta")

st.line_chart(
    pd.DataFrame({
        lap_a_name: lap_a["distance"],
        lap_b_name: lap_b["distance"]
    })
)

# =====================================================
# SECTOR DELTAS
# =====================================================
st.markdown("## ⏱ Sector Deltas")

SECTORS = 3
sector_len = len(lap_a) // SECTORS
sector_data = []

for i in range(SECTORS):
    start = i * sector_len
    end = (i + 1) * sector_len if i < SECTORS - 1 else len(lap_a)

    a_dist = lap_a["distance"].iloc[end - 1] - lap_a["distance"].iloc[start]
    b_dist = lap_b["distance"].iloc[end - 1] - lap_b["distance"].iloc[start]

    sector_data.append({
        "Sector": f"S{i+1}",
        "Lap A Distance": round(a_dist, 2),
        "Lap B Distance": round(b_dist, 2),
        "Delta": round(a_dist - b_dist, 2)
    })

sector_df = pd.DataFrame(sector_data)
st.dataframe(sector_df, use_container_width=True)

# =====================================================
# CORNER DETECTION (BRAKE + MIN SPEED LOGIC)
# =====================================================
def detect_corners(df, brake_thresh=0.2):
    corners = []
    in_brake = False
    min_speed = None
    min_idx = None

    for i in range(len(df)):
        brake = df["brake"].iloc[i]
        speed = df["speed"].iloc[i]

        if brake > brake_thresh and not in_brake:
            in_brake = True
            min_speed = speed
            min_idx = i

        if in_brake:
            if speed < min_speed:
                min_speed = speed
                min_idx = i

            if brake <= brake_thresh:
                corners.append(min_idx)
                in_brake = False

    return corners

corners_a = detect_corners(lap_a)
corners_b = detect_corners(lap_b)

num_corners = min(len(corners_a), len(corners_b))

# =====================================================
# CORNER DELTAS TABLE
# =====================================================
st.markdown("## 📐 Corner Performance")

corner_rows = []
for i in range(num_corners):
    idx_a = corners_a[i]
    idx_b = corners_b[i]

    corner_rows.append({
        "Corner": i + 1,
        "Lap A Min Speed": round(lap_a["speed"].iloc[idx_a], 2),
        "Lap B Min Speed": round(lap_b["speed"].iloc[idx_b], 2),
        "Speed Δ": round(
            lap_a["speed"].iloc[idx_a] - lap_b["speed"].iloc[idx_b], 2
        )
    })

corner_df = pd.DataFrame(corner_rows)

st.dataframe(
    corner_df.style.background_gradient(
        subset=["Speed Δ"],
        cmap="Oranges"
    ),
    use_container_width=True
)

# =====================================================
# CORNER DELTA PLOT
# =====================================================
st.markdown("## 📊 Corner Delta Plot")

st.line_chart(
    corner_df.set_index("Corner")[["Speed Δ"]]
)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("AeroLap • FueledFast • Professional Lap Analysis")
