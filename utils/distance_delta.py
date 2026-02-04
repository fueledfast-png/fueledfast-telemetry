def distance_delta(lap_a, lap_b):
    """
    Returns distance array and time delta (A - B)
    """
    delta = lap_a["time"] - lap_b["time"]
    return lap_a["distance"], delta
