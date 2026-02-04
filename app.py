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
# STYLING
# =====================================================
st.markdown("""
<style>
.stApp { background-color: #0B0E14; color: #E5E7EB; }
[data-testid="stSidebar"] { background-color: #111827; }
h1, h2, h3 { color: #E5E7EB; }
.accent-blue { color: #3B82F6; }
.accent-orange { color: #F97316; }
.gain { color: #22C55E; font-weight: bold; }
.loss { color: #EF4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<h1>🟦 <span class="accent-blue">AeroLap</span></h1>
<p style="color:#9CA3AF;">
Automatically identifies where lap time is gained and lost
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
<li>⏱ Sector Deltas</li>
<li>📐 Corner Detection</li>
<li>🔥 Time Gain/Loss Ranking</li>
</ul>
""", unsafe_allow_html=True)

# =====================================================
# FILE UPLOAD
# =====================================================
uploaded_files = st.file_uploader(
    "Upload lap CSV files",
    type=["csv"],
    accept_multiple_files=True
)

if not uploaded_files or len(uploaded_files) < 2:
    st.info("Upload at least two lap files.")
    st.stop()

laps = {f.name: pd.read_csv(f) for f in uploaded_files}
lap_names = list(laps.keys())

# =====================================================
# LAP SELECTION
# =====================================================
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
required = {"distance", "speed", "brake", "throttle"}
for col in required:
    if col not in lap_a.columns or col not in lap_b.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# =====================================================
# ALIGN
# =====================================================
min_len = min(len(lap_a), len(lap_b))
lap_a = lap_a.iloc[:min_len]
lap_b = lap_b.iloc[:min_len]

# =====================================================
# CORNER DETECTION
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
n = min(len(corners_a), len(corners_b))

# =====================================================
# CORNER TIME CALCULATION
# =====================================================
WINDOW = 40

def corner_time(df, idx):
    s = max(0, idx - WINDOW)
    e = min(len(df), idx + WINDOW)
    dist = df["distance"].iloc[e-1] - df["distance"].iloc[s]
    avg_speed = df["speed"].iloc[s:e].mean()
    return dist / max(avg_speed, 0.1)

corner_results = []

for i in range(n):
    t_a = corner_time(lap_a, corners_a[i])
    t_b = corner_time(lap_b, corners_b[i])
    delta = round(t_a - t_b, 3)

    corner_results.append({
        "Corner": i + 1,
        "Lap A Time (est)": round(t_a, 3),
        "Lap B Time (est)": round(t_b, 3),
        "Delta (A-B)": delta,
        "Result": "GAIN" if delta < 0 else "LOSS"
    })

corner_df = pd.DataFrame(corner_results).sort_values("Delta (A-B)")

# =====================================================
# HIGHLIGHT TABLE
# =====================================================
st.markdown("## 🔥 Corner Time Gain / Loss Ranking")

def highlight(row):
    if row["Delta (A-B)"] < 0:
        return ["background-color: #052E16"] * len(row)
    return ["background-color: #3F1D1D"] * len(row)

st.dataframe(
    corner_df.style.apply(highlight, axis=1),
    use_container_width=True
)

# =====================================================
# AUTO INSIGHTS
# =====================================================
best = corner_df.iloc[0]
worst = corner_df.iloc[-1]

st.markdown("## 🧠 Automatic Insights")

st.markdown(f"""
- 🟢 **Biggest Gain:** Corner {best['Corner']} ({best['Delta (A-B)']}s)  
- 🔴 **Biggest Loss:** Corner {worst['Corner']} (+{worst['Delta (A-B)']}s)  
- 🎯 Focus coaching on **red corners first**
""")

# =====================================================
# SELECT CORNER TO REVIEW
# =====================================================
st.markdown("## 📊 Review Specific Corner")

corner_choice = st.selectbox(
    "Select corner",
    corner_df["Corner"].tolist()
)

idx = corner_choice - 1

def seg(df, i):
    s = max(0, corners_a[i] - WINDOW)
    e = min(len(df), corners_a[i] + WINDOW)
    return df.iloc[s:e].reset_index(drop=True)

seg_a = seg(lap_a, idx)
seg_b = seg(lap_b, idx)

st.line_chart(
    pd.DataFrame({
        f"{lap_a_name} Speed": seg_a["speed"],
        f"{lap_b_name} Speed": seg_b["speed"]
    })
)

st.line_chart(
    pd.DataFrame({
        f"{lap_a_name} Brake": seg_a["brake"],
        f"{lap_b_name} Brake": seg_b["brake"]
    })
)

st.line_chart(
    pd.DataFrame({
        f"{lap_a_name} Throttle": seg_a["throttle"],
        f"{lap_b_name} Throttle": seg_b["throttle"]
    })
)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("AeroLap • FueledFast • Identify Where Lap Time Is Won")
