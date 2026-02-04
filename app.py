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
.loss { background-color: #3F1D1D; }
.gain { background-color: #052E16; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<h1>🟦 <span class="accent-blue">AeroLap</span></h1>
<p style="color:#9CA3AF;">
Exit-speed focused lap analysis — where lap time is really won
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
<li>📐 Corner Detection</li>
<li>🚀 Exit Speed Deltas</li>
<li>🔥 Time Loss Ranking</li>
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
# EXIT SPEED CALCULATION
# =====================================================
EXIT_WINDOW = 20  # samples after apex

exit_results = []

for i in range(n):
    idx_a = corners_a[i]
    idx_b = corners_b[i]

    exit_a = lap_a["speed"].iloc[idx_a:idx_a+EXIT_WINDOW].mean()
    exit_b = lap_b["speed"].iloc[idx_b:idx_b+EXIT_WINDOW].mean()

    delta = round(exit_a - exit_b, 2)

    exit_results.append({
        "Corner": i + 1,
        "Lap A Exit Speed": round(exit_a, 2),
        "Lap B Exit Speed": round(exit_b, 2),
        "Exit Speed Δ": delta,
        "Result": "GAIN" if delta > 0 else "LOSS"
    })

exit_df = pd.DataFrame(exit_results).sort_values("Exit Speed Δ")

# =====================================================
# EXIT SPEED TABLE
# =====================================================
st.markdown("## 🚀 Exit Speed Delta Ranking")

def style_row(row):
    if row["Exit Speed Δ"] < 0:
        return ["background-color: #3F1D1D"] * len(row)
    return ["background-color: #052E16"] * len(row)

st.dataframe(
    exit_df.style.apply(style_row, axis=1),
    use_container_width=True
)

# =====================================================
# KEY INSIGHTS
# =====================================================
worst = exit_df.iloc[0]
best = exit_df.iloc[-1]

st.markdown("## 🧠 Exit Speed Insights")

st.markdown(f"""
- 🔴 **Worst Exit:** Corner {worst['Corner']} ({worst['Exit Speed Δ']} km/h)  
- 🟢 **Best Exit:** Corner {best['Corner']} (+{best['Exit Speed Δ']} km/h)  
- 🚀 Exit speed losses compound down the next straight
""")

# =====================================================
# CORNER REVIEW
# =====================================================
st.markdown("## 📊 Review Exit Behavior")

corner_choice = st.selectbox(
    "Select corner",
    exit_df["Corner"].tolist()
)

idx = corner_choice - 1

def segment(df, apex):
    s = max(0, apex - 30)
    e = min(len(df), apex + 60)
    return df.iloc[s:e].reset_index(drop=True)

seg_a = segment(lap_a, corners_a[idx])
seg_b = segment(lap_b, corners_b[idx])

st.line_chart(
    pd.DataFrame({
        f"{lap_a_name} Speed": seg_a["speed"],
        f"{lap_b_name} Speed": seg_b["speed"]
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
st.caption("AeroLap • FueledFast • Exit Speed Wins Races")
