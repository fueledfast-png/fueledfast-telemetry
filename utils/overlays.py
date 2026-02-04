def extract_corner_segment(df, corner):
    return df.iloc[int(corner["start"]):int(corner["end"])]
