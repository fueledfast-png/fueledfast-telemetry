import pandas as pd
import numpy as np

def compute_sector_deltas(delta_df, num_sectors=3):
    """
    Split distance-based delta into equal-distance sectors
    and compute time loss per sector.
    """
    max_dist = delta_df["distance"].max()
    sector_edges = np.linspace(0, max_dist, num_sectors + 1)

    rows = []

    for i in range(num_sectors):
        start = sector_edges[i]
        end = sector_edges[i + 1]

        sector = delta_df[
            (delta_df["distance"] >= start) &
            (delta_df["distance"] < end)
        ]

        if sector.empty:
            continue

        sector_time = sector["delta_time"].iloc[-1] - sector["delta_time"].iloc[0]

        rows.append({
            "Sector": f"S{i+1}",
            "Distance Range (m)": f"{start:.0f} – {end:.0f}",
            "Time Delta (s)": round(sector_time, 3)
        })

    return pd.DataFrame(rows)
