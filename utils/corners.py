import pandas as pd

def detect_corners(df, brake_threshold=0.2):
    corners = []
    braking = df["brake"] > brake_threshold
    start = None

    for i in range(len(df)):
        if braking.iloc[i] and start is None:
            start = i

        elif not braking.iloc[i] and start is not None:
            segment = df.iloc[start:i]
            min_idx = segment["speed"].idxmin()

            corners.append({
                "corner_id": len(corners) + 1,
                "start": start,
                "end": i,
                "min_speed": segment.loc[min_idx, "speed"]
            })
            start = None

    return pd.DataFrame(corners)

def match_corner_deltas(c1, c2):
    rows = []

    for i in range(min(len(c1), len(c2))):
        rows.append({
            "Corner": i + 1,
            "Min Speed Δ": round(c1.iloc[i]["min_speed"] - c2.iloc[i]["min_speed"], 2)
        })

    return pd.DataFrame(rows)
