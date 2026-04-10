import pandas as pd
import plotly.graph_objects as go
import numpy as np

def plot_baseline_timeline(df: pd.DataFrame) -> go.Figure:
    """
    Renders the baseline risk timeline as a horizontal Plotly Figure.
    It takes up full width visually via Streamlit later, with specific background
    bands corresponding to the risk regime.
    """
    fig = go.Figure()

    # Base line trace
    if "spy_close" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["spy_close"],
            mode="lines",
            name="SPY Close",
            line=dict(color="#1f77b4", width=2)
        ))

    colors = {
        "Low": "#388E3C",
        "Medium": "#FBC02D",
        "High": "#D32F2F"
    }

    if "baseline_regime" in df.columns:
        # To add contiguous shapes, we need to find blocks of regimes
        # because add_vrect is useful here.
        df_valid = df.dropna(subset=["baseline_regime"])
        
        if not df_valid.empty:
            # We'll group by consecutive identical regimes
            regime = df_valid["baseline_regime"].values
            dates = df_valid.index

            # Guard: single-row df_valid would produce starts=[0], ends=[-1]
            # (negative index) due to empty regime[:-1]. Render one vrect directly.
            if len(df_valid) == 1:
                r = regime[0]
                color = colors.get(r, "#CCCCCC")
                fig.add_vrect(
                    x0=dates[0],
                    x1=dates[0] + pd.Timedelta(days=1),
                    fillcolor=color,
                    opacity=0.3,
                    layer="below",
                    line_width=0,
                )
                # Skip the block-detection loop below for this edge case
                dates = pd.DatetimeIndex([])  # causes zip to produce nothing
                starts = np.array([], dtype=int)
                ends = np.array([], dtype=int)
            else:
                # Find boundaries where regime changes
                changes = np.where(regime[:-1] != regime[1:])[0]

                starts = np.insert(changes + 1, 0, 0)
                ends = np.append(changes, len(regime) - 1)
            
            for start, end in zip(starts, ends):
                r = regime[start]
                start_date = dates[start]
                # Use exclusive end: add 1 day so adjacent regime blocks do not
                # share a boundary date, preventing 1-day overlap in vrect rendering.
                end_date = dates[end] + pd.Timedelta(days=1)
                color = colors.get(r, "#CCCCCC")

                fig.add_vrect(
                    x0=start_date,
                    x1=end_date,
                    fillcolor=color,
                    opacity=0.3,  # slight opacity so price line stays visible
                    layer="below",
                    line_width=0,
                )

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        title="SPY Baseline Risk Regime Overview",
        xaxis_title="",
        yaxis_title="SPY Closing Price",
        template="plotly_white",
        height=400,
        showlegend=True
    )
    
    return fig
