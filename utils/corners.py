import numpy as np
import pandas as pd
from scipy.signal import find_peaks

def detect_corners(lap_df, speed_col="speed", time_col="time",
                   min_prominence=1.5, min_distance_s=0.5):
    """
    Detect corners by finding local minima in speed.
    Returns list of corner indices.
    """
    speeds = lap_df[speed_col].values
    times = lap_df[time_col].values

    if len(times) < 2:
        return []

    # invert speed to find minima
    inverted = -speeds

    dt = np.median(np.diff(times))
    min_samples = max(1, int(min_distance_s / (dt if dt > 0 else 0.05)))

    peaks, _ = find_peaks(
        inverted,
        prominence=min_prominence,
        distance=min_samples
    )

    return peaks.tolist()


def corner_stats(lap_df, corner_idx,
                 window_before=20, window_after=40,
                 speed_col="speed", time_col="time"):
    """
    Compute entry / min / exit speed and time spent for a corner.
    """
    start = max(0, corner_idx - window_before)
    end = min(len(lap_df) - 1, corner_idx + window_after)

    segment = lap_df.iloc[start:end]

    entry_speed = segment[speed_col].iloc[:5].mean()
    exit_speed = segment[speed_col].iloc[-5:].mean()
    min_speed = segment[speed_col].min()
    time_spent = segment[time_col].iloc[-1] - segment[time_col].iloc[0]

    return {
        "entry_speed": round(entry_speed, 2),
        "min_speed": round(min_speed, 2),
        "exit_speed": round(exit_speed, 2),
        "time_spent": round(time_spent, 3)
    }


def analyze_corners(lap_df):
    """
    Full corner analysis for one lap.
    Returns DataFrame of corner stats.
    """
    corner_indices = detect_corners(lap_df)

    rows = []
    for i, idx in enumerate(corner_indices):
        stats = corner_stats(lap_df, idx)
        stats["Corner"] = i + 1
        rows.append(stats)

    return pd.DataFrame(rows)


def match_corner_deltas(corners_a, corners_b):
    """
    Match corners by order and compute deltas.
    """
    n = min(len(corners_a), len(corners_b))
    rows = []

    for i in range(n):
        a = corners_a.iloc[i]
        b = corners_b.iloc[i]

        rows.append({
            "Corner": int(a["Corner"]),
            "Entry Δ": round(a["entry_speed"] - b["entry_speed"], 2),
            "Min Speed Δ": round(a["min_speed"] - b["min_speed"], 2),
            "Exit Δ": round(a["exit_speed"] - b["exit_speed"], 2),
            "Time Δ (s)": round(a["time_spent"] - b["time_spent"], 3)
        })

    return pd.DataFrame(rows)
