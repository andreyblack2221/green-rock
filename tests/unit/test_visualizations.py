import pandas as pd
import numpy as np
import plotly.graph_objects as go
from green_rock.entrypoints.visualizations import plot_baseline_timeline

def test_plot_baseline_timeline_returns_valid_figure():
    # Arrange
    dates = pd.date_range("2020-01-01", periods=5)
    df = pd.DataFrame({
        "spy_close": [100, 101, 102, 99, 98],
        "baseline_regime": ["Low", "Low", "Medium", "High", "High"]
    }, index=dates)

    # Act
    fig = plot_baseline_timeline(df)

    # Assert
    assert isinstance(fig, go.Figure)
    
    # Verify the layout has zero margins except top
    margins = fig.layout.margin
    assert margins.l == 0
    assert margins.r == 0
    assert margins.b == 0
    assert margins.t == 30

    # Verify that shapes for risk regimes were added
    shapes = fig.layout.shapes
    assert len(shapes) > 0

    # Test some shape styling
    colors_found = {shape.fillcolor for shape in shapes if hasattr(shape, 'fillcolor')}
    assert "#388E3C" in colors_found  # Low
    assert "#FBC02D" in colors_found  # Medium
    assert "#D32F2F" in colors_found  # High
