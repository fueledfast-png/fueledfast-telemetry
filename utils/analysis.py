import pandas as pd
import numpy as np


# -------------------------------------------------
# DISTANCE HANDLING
# -------------------------------------------------
def ensure_distance(lap: pd.DataFrame) -> pd.DataFrame:
    lap = lap.copy()

    if "distance" in lap.columns:
        return lap

    if "speed" not in lap.columns or "time" not in lap.columns:
        lap["distance"] = np.arange(len(lap))
        return lap

    speed = lap["speed"]
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
    """
    Split lap into equal-distance sectors and compute time deltas.
    """
    total_distance = ref["distance"].max()
    sector_length = total_distance / sectors

    results = []

    for i in range(sectors):
        start = i * sector_length
        end = (i + 1) * sector_length

        ref_sector = ref[(ref["distance"] >= start) & (ref["distance"] < end)]
        cmp_sector = cmp[(cmp["distance"] >= start) & (cmp["distance"] < end)]

        if ref_sector.empty or cmp_sector.empty:
            continue

        ref_time = ref_sector["time"].iloc[-1] - ref_sector["time"].iloc[0]
        cmp_time = cmp_sector["time"].iloc[-1] - cmp_sector["time"].iloc[0]

        results.append({
            "Sector": f"S{i + 1}",
            "Reference Time (s)": round(ref_time, 3),
            "Comparison Time (s)": round(cmp_time, 3),
            "Delta (s)": round(ref_time - cmp_time, 3)
        })

    return pd.DataFrame(results)
