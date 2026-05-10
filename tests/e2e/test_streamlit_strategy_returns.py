"""
E2E tests for strategy returns rendering in Streamlit
(Story 4.1: Financial Allocation & Benchmarking Engine).

Tests cover:
  - AC2: App renders without crash when strategy_returns present
  - Graceful degradation: App handles empty strategy_returns without crash
"""
import pytest
import pandas as pd
import numpy as np
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).parent.parent.parent
APP_PATH = ROOT / "src" / "green_rock" / "entrypoints" / "streamlit_app.py"


@pytest.fixture
def mock_dates():
    return pd.date_range("2023-01-01", periods=100)


def _build_ml_dataframe(dates):
    """Build a DataFrame with all columns the app expects after ML analysis."""
    return pd.DataFrame({
        "spy_close": range(100),
        "baseline_regime": ["Low"] * 80 + ["High"] * 20,
        "is_test": [False] * 80 + [True] * 20,
        "rf_prediction": [None] * 80 + ["Low"] * 10 + ["High"] * 10,
    }, index=dates)


class TestStrategyReturnsE2E:
    """[P1] E2E: Verify strategy returns data flows through to Streamlit."""

    def test_app_renders_with_strategy_returns(self, mock_dates):
        """E1: App renders without crash when strategy_returns dict is populated."""
        def _mock_run_pipeline(self, *args, **kwargs):
            return (pd.DataFrame({"spy_close": range(100)}, index=mock_dates), "LIVE", None, None)
            
        def _mock_compute_ml(self, df, rf_features=None, target_col="baseline_regime"):
            return (
                _build_ml_dataframe(mock_dates),
                {"spy_close": 0.6, "tlt_close": 0.4},
                {"baseline_latest": "High", "rf_latest": "High", "agreement_rate": 50.0,
                 "divergence_count": 10, "total_test_days": 20},
                {"base_value": 0.35, "spy_close": 0.12, "tlt_close": -0.08, "predicted_class": "High"},
                pd.DataFrame({
                    "Strategy": ["Baseline MA", "Random Forest", "60/40 Portfolio", "S&P 500"],
                    "Cumulative Return": [15.0, 22.0, 10.0, 18.0],
                    "Max Drawdown": [5.0, 4.0, 8.0, 10.0]
                }),
            )

        with patch("green_rock.service_layer.pipeline.DataPipeline.run_pipeline", _mock_run_pipeline), \
             patch("green_rock.service_layer.pipeline.DataPipeline.compute_ml_analysis", _mock_compute_ml):

            at = AppTest.from_file(str(APP_PATH))
            at.run(timeout=10)

            assert not at.exception, f"App crashed with strategy_returns present: {at.exception}"

    def test_app_renders_with_empty_strategy_returns(self, mock_dates):
        """E2: App renders without crash when strategy_returns is empty dict."""
        def _mock_run_pipeline(self, *args, **kwargs):
            return (pd.DataFrame({"spy_close": range(100)}, index=mock_dates), "LIVE", None, None)
            
        def _mock_compute_ml(self, df, rf_features=None, target_col="baseline_regime"):
            return (
                _build_ml_dataframe(mock_dates),
                {"spy_close": 0.6, "tlt_close": 0.4},
                {"baseline_latest": "High", "rf_latest": "High", "agreement_rate": 50.0,
                 "divergence_count": 10, "total_test_days": 20},
                {"base_value": 0.35, "spy_close": 0.12, "tlt_close": -0.08, "predicted_class": "High"},
                pd.DataFrame(),  # Empty strategy_returns
            )

        with patch("green_rock.service_layer.pipeline.DataPipeline.run_pipeline", _mock_run_pipeline), \
             patch("green_rock.service_layer.pipeline.DataPipeline.compute_ml_analysis", _mock_compute_ml):

            at = AppTest.from_file(str(APP_PATH))
            at.run(timeout=10)

            assert not at.exception, f"App crashed with empty strategy_returns: {at.exception}"
