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
# STYLING — JET BLACK + BLUE / ORANGE
# =====================================================
st.markdown("""
<style>
.stApp { background-color: #0B0E14; color: #E5E7EB; }
[data-testid="stSidebar"] { background-color: #111827; }
h1, h2, h3 { color: #E5E7EB; }
.accent-blue { color: #3B82F6; }
.accent-orange { color: #F97316; }
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
<p style="color:#9CA3AF;">
Professional lap analysis — braking, throttle & corner performance
</p>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.markdown("""
<h2 class="accent-blue">AeroLap</h2>
<p style="color:#9CA3AF;">FueledFast Performance Tools</p>
<hr style="border-color:#1F2937;">
<ul>
<li>📏 Distance Delta</li>
<li>⏱ Sector Analysis</li>
<li>📐 Corner Detection</li>
<li>🎛 Throttle & Brake Overlays</li>
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
    st.info("Upload **at least two lap CSV files**.")
    st.stop()

laps = {f.name: pd.read_csv(f) for f in uploaded_files}
lap_names = list(laps.keys())

# =====================================================
# LAP SELECTION
# =====================================================
st.markdown("## 🔁 Select Laps")

c1, c2 = st.columns(2)
with c1:
    lap_a_name = st.selectbox("Lap A", lap_names, 0)
with c2:
    lap_b_name = st.selectbox("Lap B", lap_names, 1)

lap_a = laps[lap_a_name].copy()
lap_b = laps[lap_b_name].copy()

# =====================================================
# COLUMN CHECK
# =====================================================
required_cols = {"distance", "speed", "brake", "throttle"}
for col in required_cols:
    if col not in lap_a.columns or col not in lap_b.columns:
        st.error(f"Missing required column: `{col}`")
        st.stop()

# =====================================================
# ALIGN LAPS
# =====================================================
min_len = min(len(lap_a), len(lap_b))
lap_a = lap_a.iloc[:min_len]
lap_b = lap_b.iloc[:min_len]

# =====================================================
# DISTANCE DELTA
# =====================================================
st.markdown("## 📉 Distance Comparison")

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
sector_rows = []

for i in range(SECTORS):
    s = i * sector_len
    e = (i + 1) * sector_len if i < SECTORS - 1 else len(lap_a)

    a_dist = lap_a["distance"].iloc[e-1] - lap_a["distance"].iloc[s]
    b_dist = lap_b["distance"].iloc[e-1] - lap_b["distance"].iloc[s]

    sector_rows.append({
        "Sector": f"S{i+1}",
        "Lap A Distance": round(a_dist, 2),
        "Lap B Distance": round(b_dist, 2),
        "Delta": round(a_dist - b_dist, 2)
    })

st.dataframe(pd.DataFrame(sector_rows), use_container_width=True)

# =====================================================
# CORNER DETECTION (BRAKE + MIN SPEED)
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
# CORNER SELECTION
# =====================================================
st.markdown("## 📐 Corner Analysis")

corner_ids = list(range(1, num_corners + 1))
corner_choice = st.selectbox("Select Corner", corner_ids)

idx_a = corners_a[corner_choice - 1]
idx_b = corners_b[corner_choice - 1]

# =====================================================
# WINDOW AROUND CORNER
# =====================================================
WINDOW = 30  # samples before/after

def window(df, idx):
    start = max(0, idx - WINDOW)
    end = min(len(df), idx + WINDOW)
    return df.iloc[start:end].reset_index(drop=True)

seg_a = window(lap_a, idx_a)
seg_b = window(lap_b, idx_b)

# =====================================================
# THROTTLE OVERLAY
# =====================================================
st.markdown("### 🎛 Throttle Overlay")

st.line_chart(
    pd.DataFrame({
        f"{lap_a_name} Throttle": seg_a["throttle"],
        f"{lap_b_name} Throttle": seg_b["throttle"]
    })
)

# =====================================================
# BRAKE OVERLAY
# =====================================================
st.markdown("### 🛑 Brake Overlay")

st.line_chart(
    pd.DataFrame({
        f"{lap_a_name} Brake": seg_a["brake"],
        f"{lap_b_name} Brake": seg_b["brake"]
    })
)

# =====================================================
# SPEED OVERLAY
# =====================================================
st.markdown("### 🏎 Speed Overlay")

st.line_chart(
    pd.DataFrame({
        f"{lap_a_name} Speed": seg_a["speed"],
        f"{lap_b_name} Speed": seg_b["speed"]
    })
)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("AeroLap • FueledFast • Corner-Level Telemetry Analysis")
