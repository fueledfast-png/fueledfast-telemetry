import pandas as pd
import numpy as np

# -------------------------------------------------
# DISTANCE HANDLING
# -------------------------------------------------
def ensure_distance(lap):
    """
    Ensures lap has a distance column.
    If missing, calculate from speed & time.
    """
    if "distance" in lap.columns:
        return lap

    lap = lap.copy()

    if "speed" not in lap.columns or "time" not in lap.columns:
        lap["distance"] = np.arange(len(lap))
        return lap

    speed = lap["speed"].copy()

    # detect km/h → m/s
    if speed.mean() > 40:
        speed = speed / 3.6

    time = lap["time"]
    dt = time.diff().fillna(0.05)

    lap["distance"] = (speed * dt).cumsum()
    return lap


# -------------------------------------------------
# DISTANCE-BASED LAP COMPARISON
# -------------------------------------------------
def analyze_laps(reference_lap, compare_lap):
    ref = ensure_distance(reference_lap)
    cmp = ensure_distance(compare_lap)

    max_dist = min(ref["distance"].max(), cmp["distance"].max())

    ref = ref[ref["distance"] <= max_dist]
    cmp = cmp[cmp["distance"] <= max_dist]

    # interpolate time vs distance
    cmp_time_interp = np.interp(
        ref["distance"],
        cmp["distance"],
        cmp["time"]
    )

    ref = ref.copy()
    ref["delta_time"] = ref["time"] - cmp_time_interp

    insights = {
        "avg_delta": round(ref["delta_time"].mean(), 4),
        "max_loss": round(ref["delta_time"].max(), 4),
        "distance_of_max_loss": round(
            ref.loc[ref["delta_time"].idxmax(), "distance"], 2
        )
    }

    return ref, insights


# -------------------------------------------------
# DRIVING STATS
# -------------------------------------------------
def driving_stats(lap):
    stats = {}

    if "speed" in lap.columns:
        stats["Avg Speed"] = round(lap["speed"].mean(), 2)
        stats["Max Speed"] = round(lap["speed"].max(), 2)
        stats["Min Speed"] = round(lap["speed"].min(), 2)

    if "throttle" in lap.columns:
        stats["Avg Throttle"] = round(lap["throttle"].mean(), 3)

    if "brake" in lap.columns:
        stats["Avg Brake"] = round(lap["brake"].mean(), 3)

    return stats
