import pytest
import pandas as pd
import numpy as np
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
from pathlib import Path

def test_feature_importance_viz_rendering():
    """
    [P0] Verify that the Streamlit app renders Plotly charts and
    comparative metric cards when ML analysis succeeds.
    """
    # GIVEN a mocked environment
    with patch("green_rock.entrypoints.streamlit_app.DataPipeline") as MockPipeline:
        
        # Use a proper DatetimeIndex to avoid TypeError in plot_baseline_timeline
        mock_dates = pd.date_range("2023-01-01", periods=100)
        
        mock_df_base = pd.DataFrame({"spy_close": range(100)}, index=mock_dates)
        
        mock_df_ml = pd.DataFrame({
            "spy_close": range(100),
            "baseline_regime": ["Low"]*80 + ["High"]*20,
            "is_test": [False]*80 + [True]*20,
            "rf_prediction": [None]*80 + ["Low"]*10 + ["High"]*10,
        }, index=mock_dates)
        
        mock_instance = MockPipeline.return_value
        mock_instance.run_pipeline.return_value = (mock_df_base, "LIVE", None, None)
        mock_instance.compute_ml_analysis.return_value = (
            mock_df_ml,
            {"spy_close": 0.6, "tlt_close": 0.4},
            {"baseline_latest": "High", "rf_latest": "High", "agreement_rate": 50.0, "divergence_count": 10, "total_test_days": 20},
            {"base_value": 0.5, "spy_close": 0.1, "tlt_close": -0.05, "predicted_class": "High"},
            {"baseline_cumulative": 0.1, "rf_cumulative": 0.2, "benchmark_60_40": 0.05, "benchmark_spy": 0.08}
        )
        
        # WHEN running the app
        root = Path(__file__).parent.parent.parent
        app_path = root / "src" / "green_rock" / "entrypoints" / "streamlit_app.py"
        at = AppTest.from_file(str(app_path))
        # Increase timeout to handle slower CI/local runs
        at.run(timeout=10)
        
        # THEN Plotly charts should be rendered (baseline + feature importance)
        charts = at.get("plotly_chart")
        assert len(charts) >= 2, f"Expected at least 2 charts, found {len(charts)}"
        
        # AND comparative metric cards should be rendered
        metrics = [(m.label, m.value) for m in at.metric]
        labels = [m[0] for m in metrics]
        assert "Baseline MA Regime" in labels, "Baseline metric must be rendered"
        assert "Random Forest Regime" in labels, "RF metric must be rendered"

def test_feature_importance_missing_graceful_handling():
    """
    [P1] Verify that the app handles cases where ML analysis fails entirely.
    """
    # GIVEN a mocked environment where ML analysis raises an exception
    # Patch at the class level (not instance) so the patch persists into
    # AppTest's isolated script execution context.
    with patch("green_rock.service_layer.pipeline.DataPipeline.compute_ml_analysis",
               side_effect=Exception("ML model training failed")):
        
        # WHEN running the app
        root = Path(__file__).parent.parent.parent
        app_path = root / "src" / "green_rock" / "entrypoints" / "streamlit_app.py"
        at = AppTest.from_file(str(app_path))
        at.run(timeout=10)
        
        # THEN the app should not crash
        assert not at.exception, f"Dashboard crashed when ML analysis failed: {at.exception}"
        # AND a warning message should be displayed
        warning_texts = [w.value for w in at.warning]
        assert any("Machine Learning" in w for w in warning_texts), (
            f"Expected ML warning, got warnings: {warning_texts}"
        )
