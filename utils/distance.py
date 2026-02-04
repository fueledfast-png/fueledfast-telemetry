def ensure_distance(df):
    if "distance" not in df.columns:
        dt = df["time"].diff().fillna(0)
        df["distance"] = (df["speed"] * dt).cumsum()
    return df
