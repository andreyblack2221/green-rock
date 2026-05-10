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

def plot_feature_importance(importances: dict[str, float]) -> go.Figure:
    """
    Renders a horizontal bar chart of feature importances.
    """
    if not importances:
        return go.Figure()

    # Sort descending
    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    features = [k for k, v in sorted_items]
    values = [v for k, v in sorted_items]

    # Plotly puts the first item at the bottom for horizontal bar charts by default,
    # so we should reverse the sorted items to have the largest at the top.
    features.reverse()
    values.reverse()

    fig = go.Figure(go.Bar(
        x=values,
        y=features,
        orientation='h',
        marker=dict(color='#1F3A5F')
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        title="Feature Importances",
        xaxis_title="Importance",
        yaxis_title="",
        template="plotly_white",
        height=max(300, len(features) * 40)
    )

    return fig

def plot_xai_waterfall(xai_attribution: dict) -> go.Figure:
    """
    Renders a Waterfall chart for the daily risk attribution.
    """
    if not xai_attribution:
        return go.Figure()

    base_value = xai_attribution.get("base_value", 0.0)
    
    # Filter out base_value and predicted_class to get just feature contributions
    features = []
    contributions = []
    for k, v in xai_attribution.items():
        if k not in ["base_value", "predicted_class"]:
            features.append(k)
            contributions.append(v)
            
    # Sort by absolute contribution to show most impactful first
    sorted_items = sorted(zip(features, contributions), key=lambda x: abs(x[1]), reverse=True)
    sorted_features = [x[0] for x in sorted_items]
    sorted_contributions = [x[1] for x in sorted_items]
    
    measure = ["absolute"] + ["relative"] * len(sorted_features) + ["total"]
    x = ["Base Probability"] + sorted_features + ["Final Probability"]
    y = [base_value] + sorted_contributions + [base_value + sum(sorted_contributions)]
    
    # Text annotations for values
    text = [f"{val:.3f}" for val in y]
    
    fig = go.Figure(go.Waterfall(
        name="Risk Attribution",
        orientation="v",
        measure=measure,
        x=x,
        textposition="outside",
        text=text,
        y=y,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#388E3C"}}, # Forest Green for risk-reducing
        increasing={"marker": {"color": "#D32F2F"}}, # Crimson for risk-increasing
        totals={"marker": {"color": "#1F3A5F"}}      # Slate Blue for totals
    ))

    predicted_class = xai_attribution.get("predicted_class", "Unknown")
    
    fig.update_layout(
        title=f"Daily Risk Attribution Waterfall — P(High Risk) | Predicted: {predicted_class}",
        showlegend=False,
        template="plotly_white",
        margin=dict(l=0, r=0, t=30, b=0),
        height=500,
        waterfallgap=0.3
    )

    return fig
