import plotly.graph_objects as go

def plot_distance_delta(distance, delta):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=distance,
        y=delta,
        mode="lines",
        name="Δ Time"
    ))

    fig.update_layout(
        template="plotly_dark",
        title="Distance-Based Delta",
        xaxis_title="Distance",
        yaxis_title="Time Δ (s)"
    )
    return fig

def plot_throttle_brake(seg_a, seg_b):
    fig = go.Figure()

    fig.add_trace(go.Scatter(y=seg_a["throttle"], name="Throttle A"))
    fig.add_trace(go.Scatter(y=seg_b["throttle"], name="Throttle B"))
    fig.add_trace(go.Scatter(y=seg_a["brake"], name="Brake A"))
    fig.add_trace(go.Scatter(y=seg_b["brake"], name="Brake B"))

    fig.update_layout(
        template="plotly_dark",
        title="Throttle / Brake Overlay"
    )
    return fig
