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
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<h1>🟦 <span class="accent-blue">AeroLap</span></h1>
<p style="color:#9CA3AF;">
Professional lap analysis — works with ANY sim telemetry
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
<li>📏 Auto Distance Reconstruction</li>
<li>📐 Corner Detection</li>
<li>🚀 Exit Speed Analysis</li>
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
# DISTANCE RECONSTRUCTION
# =====================================================
def ensure_distance(df):
    if "distance" in df.columns:
        return df

    # detect time column
    time_col = None
    for c in ["time", "timestamp", "sessiontime"]:
        if c in df.columns:
            time_col = c
            break

    if time_col is None:
        st.error("No time column found to reconstruct distance.")
        st.stop()

    speed = df["speed"].copy()

    # detect km/h vs m/s
    if speed.mean() > 40:
        speed = speed / 3.6  # km/h → m/s

    time = df[time_col]
    dt = time.diff().fillna(0)

    df["distance"] = (speed * dt).cumsum()
    return df

lap_a = ensure_distance(lap_a)
lap_b = ensure_distance(lap_b)

# =====================================================
# COLUMN CHECK
# =====================================================
required = {"distance", "speed", "brake", "throttle"}
for col in required:
    if col not in lap_a.columns or col not in lap_b.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# =====================================================
# ALIGN LAPS
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
# EXIT SPEED ANALYSIS
# =====================================================
EXIT_WINDOW = 20
rows = []

for i in range(n):
    idx_a = corners_a[i]
    idx_b = corners_b[i]

    exit_a = lap_a["speed"].iloc[idx_a:idx_a+EXIT_WINDOW].mean()
    exit_b = lap_b["speed"].iloc[idx_b:idx_b+EXIT_WINDOW].mean()

    rows.append({
        "Corner": i + 1,
        "Lap A Exit Speed": round(exit_a, 2),
        "Lap B Exit Speed": round(exit_b, 2),
        "Exit Speed Δ": round(exit_a - exit_b, 2)
    })

exit_df = pd.DataFrame(rows).sort_values("Exit Speed Δ")

# =====================================================
# DISPLAY
# =====================================================
st.markdown("## 🚀 Exit Speed Delta Ranking")
st.dataframe(exit_df, use_container_width=True)

worst = exit_df.iloc[0]
best = exit_df.iloc[-1]

st.markdown("## 🧠 Key Insights")
st.markdown(f"""
- 🔴 **Worst Exit:** Corner {worst['Corner']} ({worst['Exit Speed Δ']} km/h)  
- 🟢 **Best Exit:** Corner {best['Corner']} (+{best['Exit Speed Δ']} km/h)  
""")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("AeroLap • FueledFast • Robust Telemetry Analysis")
