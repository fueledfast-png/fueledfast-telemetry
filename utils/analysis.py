import pandas as pd
import numpy as np


# -------------------------------------------------
# DISTANCE HANDLING
# -------------------------------------------------
def ensure_distance(lap: pd.DataFrame) -> pd.DataFrame:
    lap = lap.copy()

    if "distance" in lap.columns:
        return lap

    speed = lap["speed"]
    if speed.mean() > 40:
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
# DELTA CALCULATION
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


def interpolate_channel(ref: pd.DataFrame, cmp: pd.DataFrame, channel: str):
    if channel not in cmp.columns:
        return None

    return np.interp(
        ref["distance"],
        cmp["distance"],
        cmp[channel]
    )


# -------------------------------------------------
# SECTOR DELTAS
# -------------------------------------------------
def compute_sector_deltas(ref: pd.DataFrame, cmp: pd.DataFrame, sectors: int = 3):
    total_distance = ref["distance"].max()
    sector_length = total_distance / sectors

    rows = []

    for i in range(sectors):
        start = i * sector_length
        end = (i + 1) * sector_length

        ref_s = ref[(ref["distance"] >= start) & (ref["distance"] < end)]
        cmp_s = cmp[(cmp["distance"] >= start) & (cmp["distance"] < end)]

        if ref_s.empty or cmp_s.empty:
            continue

        ref_time = ref_s["time"].iloc[-1] - ref_s["time"].iloc[0]
        cmp_time = cmp_s["time"].iloc[-1] - cmp_s["time"].iloc[0]

        rows.append({
            "Sector": f"S{i+1}",
            "Reference (s)": round(ref_time, 3),
            "Comparison (s)": round(cmp_time, 3),
            "Delta (s)": round(ref_time - cmp_time, 3)
        })

    return pd.DataFrame(rows)


# -------------------------------------------------
# CORNER DETECTION
# -------------------------------------------------
def detect_corners(
    lap: pd.DataFrame,
    brake_threshold: float = 0.1,
    min_speed_drop: float = 8.0,
    window_m: float = 25.0
):
    """
    Detect corners using brake + local min speed.
    Returns list of corner dicts.
    """
    lap = lap.copy()
    corners = []

    speeds = lap["speed"].values
    distances = lap["distance"].values
    times = lap["time"].values
    brakes = lap["brake"].values if "brake" in lap.columns else np.zeros(len(lap))

    for i in range(2, len(lap) - 2):
        is_braking = brakes[i] > brake_threshold
        is_min_speed = speeds[i] < speeds[i - 1] and speeds[i] < speeds[i + 1]

        if not (is_braking and is_min_speed):
            continue

        start_dist = distances[i] - window_m
        end_dist = distances[i] + window_m

        segment = lap[
            (lap["distance"] >= start_dist) &
            (lap["distance"] <= end_dist)
        ]

        if segment.empty:
            continue

        entry_speed = segment["speed"].iloc[0]
        exit_speed = segment["speed"].iloc[-1]
        min_speed = segment["speed"].min()

        if entry_speed - min_speed < min_speed_drop:
            continue

        time_spent = segment["time"].iloc[-1] - segment["time"].iloc[0]

        corners.append({
            "Apex Distance": round(distances[i], 1),
            "Entry Speed": round(entry_speed, 2),
            "Min Speed": round(min_speed, 2),
            "Exit Speed": round(exit_speed, 2),
            "Corner Time (s)": round(time_spent, 3)
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
