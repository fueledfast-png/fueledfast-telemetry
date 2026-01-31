import pandas as pd
import numpy as np


# -------------------------------------------------
# DISTANCE HANDLING
# -------------------------------------------------
def ensure_distance(lap: pd.DataFrame) -> pd.DataFrame:
    lap = lap.copy()

    if "distance" in lap.columns:
        return lap

    speed = lap["speed"].copy()
    if speed.mean() > 40:  # km/h → m/s
        speed = speed / 3.6

    dt = lap["time"].diff().fillna(0.05)
    lap["distance"] = (speed * dt).cumsum()

    return lap


def align_laps(ref: pd.DataFrame, cmp: pd.DataFrame):
    ref = ensure_distance(ref)
    cmp = ensure_distance(cmp)

    max_dist = min(ref["distance"].max(), cmp["distance"].max())

    ref = ref[ref["distance"] <= max_dist].reset_index(drop=True)
    cmp = cmp[cmp["distance"] <= max_dist].reset_index(drop=True)

    return ref, cmp


# -------------------------------------------------
# DISTANCE-BASED DELTA
# -------------------------------------------------
def compute_delta(ref: pd.DataFrame, cmp: pd.DataFrame) -> pd.DataFrame:
    cmp_time_interp = np.interp(
        ref["distance"],
        cmp["distance"],
        cmp["time"]
    )

    ref = ref.copy()
    ref["delta_time"] = ref["time"] - cmp_time_interp
    return ref


# -------------------------------------------------
# SECTOR DELTAS
# -------------------------------------------------
def compute_sector_deltas(ref: pd.DataFrame, cmp: pd.DataFrame, sectors: int = 3):
    total_distance = ref["distance"].max()
    sector_len = total_distance / sectors

    rows = []

    for i in range(sectors):
        start = i * sector_len
        end = (i + 1) * sector_len

        r = ref[(ref["distance"] >= start) & (ref["distance"] < end)]
        c = cmp[(cmp["distance"] >= start) & (cmp["distance"] < end)]

        if r.empty or c.empty:
            continue

        rows.append({
            "Sector": f"S{i+1}",
            "Ref Time (s)": round(r["time"].iloc[-1] - r["time"].iloc[0], 3),
            "Cmp Time (s)": round(c["time"].iloc[-1] - c["time"].iloc[0], 3),
            "Delta (s)": round(
                (r["time"].iloc[-1] - r["time"].iloc[0]) -
                (c["time"].iloc[-1] - c["time"].iloc[0]), 3
            )
        })

    return pd.DataFrame(rows)


# -------------------------------------------------
# CORNER DETECTION (BRAKE + MIN SPEED)
# -------------------------------------------------
def detect_corners(
    lap: pd.DataFrame,
    brake_threshold: float = 0.1,
    min_speed_drop: float = 8.0,
    window_m: float = 25.0
):
    lap = lap.copy()
    corners = []

    speeds = lap["speed"].values
    distances = lap["distance"].values
    times = lap["time"].values
    brakes = lap["brake"].values if "brake" in lap.columns else np.zeros(len(lap))

    for i in range(2, len(lap) - 2):
        braking = brakes[i] > brake_threshold
        local_min = speeds[i] < speeds[i - 1] and speeds[i] < speeds[i + 1]

        if not (braking and local_min):
            continue

        start = distances[i] - window_m
        end = distances[i] + window_m

        seg = lap[(lap["distance"] >= start) & (lap["distance"] <= end)]
        if seg.empty:
            continue

        entry = seg["speed"].iloc[0]
        minimum = seg["speed"].min()

        if entry - minimum < min_speed_drop:
            continue

        corners.append({
            "Apex Dist (m)": round(distances[i], 1),
            "Entry Speed": round(entry, 2),
            "Min Speed": round(minimum, 2),
            "Exit Speed": round(seg["speed"].iloc[-1], 2),
            "Corner Time (s)": round(seg["time"].iloc[-1] - seg["time"].iloc[0], 3)
        })

    return pd.DataFrame(corners)


def match_corners(ref_corners: pd.DataFrame, cmp_corners: pd.DataFrame):
    n = min(len(ref_corners), len(cmp_corners))
    rows = []

    for i in range(n):
        r = ref_corners.iloc[i]
        c = cmp_corners.iloc[i]

        rows.append({
            "Corner": i + 1,
            "Ref Entry": r["Entry Speed"],
            "Cmp Entry": c["Entry Speed"],
            "Ref Min": r["Min Speed"],
            "Cmp Min": c["Min Speed"],
            "Ref Exit": r["Exit Speed"],
            "Cmp Exit": c["Exit Speed"],
            "Ref Time": r["Corner Time (s)"],
            "Cmp Time": c["Corner Time (s)"],
            "Delta (s)": round(r["Corner Time (s)"] - c["Corner Time (s)"], 3)
        })

    return pd.DataFrame(rows)
