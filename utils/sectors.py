import pandas as pd

def sector_deltas(lap_a, lap_b, sectors=3):
    total = min(lap_a["distance"].max(), lap_b["distance"].max())
    sector_len = total / sectors

    rows = []

    for i in range(sectors):
        start = i * sector_len
        end = (i + 1) * sector_len

        a = lap_a[(lap_a["distance"] >= start) & (lap_a["distance"] < end)]
        b = lap_b[(lap_b["distance"] >= start) & (lap_b["distance"] < end)]

        if len(a) == 0 or len(b) == 0:
            continue

        rows.append({
            "Sector": f"S{i+1}",
            "Delta (s)": round(a["time"].iloc[-1] - b["time"].iloc[-1], 3)
        })

    return pd.DataFrame(rows)
