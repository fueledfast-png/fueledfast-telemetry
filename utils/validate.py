REQUIRED_COLUMNS = ["time", "speed", "throttle", "brake"]

def validate_csv(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
