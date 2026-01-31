import pandas as pd
import numpy as np


def ensure_distance(lap: pd.DataFrame) -> pd.DataFrame:
    lap = lap.copy()

    # If distance already exists, trust it
    if "distance" in lap.columns:
        return lap

    # Safety fallback
    if "speed" not in lap.columns or "time" not in lap.columns:
        lap["distance"] = np.arange(len(lap))
        return lap

    # Convert km/h to m/s if needed
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
