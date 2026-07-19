"""Conceptual Plotly block layout for the warehouse MVP."""

import plotly.graph_objects as go


COLORS = {"Docks": "#334155", "Dock staging": "#38bdf8", "Processing": "#f59e0b",
          "Storage": "#22c55e", "Support": "#a78bfa", "Unallocated": "#e2e8f0"}


def create_layout(length: float, width: float, breakdown: dict[str, float], docks: int) -> go.Figure:
    """Draw proportional conceptual zones while keeping every block inside the shell."""
    gross = length * width
    support_width = min(width * 0.20, breakdown["Support areas"] / length) if length else 0
    main_width = width - support_width
    dock_depth = min(length * 0.06, 12)
    usable_length = max(length - dock_depth, 0)
    requested = breakdown["Dock staging"] + breakdown["Processing"] + breakdown["Storage"] + breakdown["Aisles"]
    scale = min(1.0, main_width * usable_length / requested) if requested else 1.0
    zones = [
        ("Dock staging", breakdown["Dock staging"]),
        ("Processing", breakdown["Processing"]),
        ("Storage", breakdown["Storage"] + breakdown["Aisles"]),
    ]
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=width, y1=length, line=dict(color="#0f172a", width=3), fillcolor="white")
    fig.add_shape(type="rect", x0=0, y0=0, x1=main_width, y1=dock_depth, fillcolor=COLORS["Docks"], line_width=1)
    fig.add_annotation(x=main_width / 2, y=dock_depth / 2, text=f"Docks ({docks})", showarrow=False, font=dict(color="white"))
    y = dock_depth
    for name, area in zones:
        depth = area * scale / main_width if main_width and area else 0
        if depth:
            fig.add_shape(type="rect", x0=0, y0=y, x1=main_width, y1=min(y + depth, length), fillcolor=COLORS[name], line=dict(color="white"))
            fig.add_annotation(x=main_width / 2, y=min(y + depth / 2, length), text=name, showarrow=False)
            y += depth
    if y < length:
        fig.add_shape(type="rect", x0=0, y0=y, x1=main_width, y1=length, fillcolor=COLORS["Unallocated"], line=dict(color="white"))
        fig.add_annotation(x=main_width / 2, y=(y + length) / 2, text="Unallocated / buffer", showarrow=False)
    if support_width:
        fig.add_shape(type="rect", x0=main_width, y0=0, x1=width, y1=length, fillcolor=COLORS["Support"], line=dict(color="white"))
        fig.add_annotation(x=(main_width + width) / 2, y=length / 2, text="Support", textangle=-90, showarrow=False)
    fig.update_xaxes(title="Width (ft)", range=[0, width], constrain="domain")
    fig.update_yaxes(title="Length (ft)", range=[0, length], scaleanchor="x", scaleratio=1)
    fig.update_layout(height=600, margin=dict(l=30, r=30, t=30, b=30), showlegend=False)
    return fig
