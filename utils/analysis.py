import pandas as pd

def analyze_laps(reference_lap, compare_lap):
    min_len = min(len(reference_lap), len(compare_lap))
    ref = reference_lap.iloc[:min_len].copy()
    cmp = compare_lap.iloc[:min_len].copy()

    ref["delta_time"] = ref["time"] - cmp["time"]

    insights = {
        "avg_delta": round(ref["delta_time"].mean(), 4),
        "max_loss": round(ref["delta_time"].max(), 4),
        "worst_index": int(ref["delta_time"].idxmax())
    }

    return ref, insights


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
