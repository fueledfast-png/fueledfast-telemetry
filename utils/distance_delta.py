import numpy as np
import pandas as pd

def prepare_distance(df):
    """
    Ensure distance column exists.
    If missing, approximate from speed.
    """
    if "distance" in df.columns:
        return df

    if "speed" not in df.columns or "time" not in df.columns:
        raise ValueError("Lap must contain speed and time")

    speed = df["speed"].copy()

    # convert km/h → m/s if needed
    if speed.mean() > 40:
        speed = speed / 3.6

    time = df["time"].values
    dt = np.diff(time, prepend=time[0])
    distance = np.cumsum(speed * dt)

    df["distance"] = distance
    return df


def distance_based_delta(lap_a, lap_b, samples=2000):
    """
    Interpolate both laps onto a common distance axis
    and compute time delta.
    """
    lap_a = prepare_distance(lap_a.copy())
    lap_b = prepare_distance(lap_b.copy())

    max_dist = min(
        lap_a["distance"].max(),
        lap_b["distance"].max()
    )

    common_dist = np.linspace(0, max_dist, samples)

    time_a = np.interp(common_dist, lap_a["distance"], lap_a["time"])
    time_b = np.interp(common_dist, lap_b["distance"], lap_b["time"])

    delta = time_a - time_b

    return pd.DataFrame({
        "distance": common_dist,
        "delta_time": delta
    })
