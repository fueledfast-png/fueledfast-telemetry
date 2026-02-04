import pandas as pd
import numpy as np

# --------------------------------------------------
# CORNER DETECTION (NO SCIPY)
# --------------------------------------------------
def detect_corners(lap_df, speed_col="speed"):
    """
    Detect corners using local minimum speed logic.
    Returns indices of corner apexes.
    """
    speed = lap_df[speed_col].values
    corner_indices = []

    for i in range(1, len(speed) - 1):
        if speed[i] < speed[i - 1] and speed[i] < speed[i + 1]:
            corner_indices.append(i)

    return corner_indices


# --------------------------------------------------
# CORNER METRICS
# --------------------------------------------------
def analyze_corners(lap_df):
    """
    Extract basic corner metrics for each detected corner.
    """
    corners = detect_corners(lap_df)
    results = []

    for idx in corners:
        entry = lap_df.iloc[max(0, idx - 10):idx]
        exit = lap_df.iloc[idx:min(len(lap_df), idx + 10)]

        results.append({
            "corner_idx": idx,
            "min_speed": lap_df.iloc[idx]["speed"],
            "entry_speed": entry["speed"].mean(),
            "exit_speed": exit["speed"].mean(),
        })

    return pd.DataFrame(results)


# --------------------------------------------------
# CORNER DELTA MATCHING
# --------------------------------------------------
def match_corner_deltas(corners_a, corners_b):
    """
    Compare corner metrics between two laps.
    """
    min_len = min(len(corners_a), len(corners_b))

    data = []
    for i in range(min_len):
        time_delta = (
            corners_b.iloc[i]["min_speed"]
            - corners_a.iloc[i]["min_speed"]
        )

        data.append({
            "Corner": i + 1,
            "Min Speed Δ": round(time_delta, 2),
            "Time Δ (s)": round(time_delta * -0.02, 3)  # proxy
        })

    return pd.DataFrame(data)


# --------------------------------------------------
# CORNER WINDOW EXTRACTION
# --------------------------------------------------
def extract_corner_window(lap_df, corner_idx,
                          window_before=20, window_after=40):
    """
    Returns telemetry slice around a corner.
    """
    start = max(0, corner_idx - window_before)
    end = min(len(lap_df), corner_idx + window_after)
    return lap_df.iloc[start:end].reset_index(drop=True)
