"""
E2E tests for the Final Outcomes Documentation Board (Story 4.2).

Tests cover:
  - App rendering the final benchmark outcomes board without crashing
  - Presence of st.dataframe when strategy_returns is provided
  - Presence of fallback info message when strategy_returns is empty
"""
import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).parent.parent.parent
APP_PATH = ROOT / "src" / "green_rock" / "entrypoints" / "streamlit_app.py"


@pytest.fixture
def mock_dates():
    return pd.date_range("2023-01-01", periods=100)


def _build_ml_dataframe(dates):
    return pd.DataFrame({
        "spy_close": range(100),
        "baseline_regime": ["Low"] * 80 + ["High"] * 20,
        "is_test": [False] * 80 + [True] * 20,
        "rf_prediction": [None] * 80 + ["Low"] * 10 + ["High"] * 10,
    }, index=dates)


class TestOutcomesBoardE2E:
    """E2E: Verify the final outcomes board rendering."""

    def test_outcomes_board_renders_dataframe(self, mock_dates):
        """Verify the dataframe is rendered when strategy_returns is present."""
        
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

            assert not at.exception, f"App crashed: {at.exception}"
            
            # Check for dataframe rendering
            assert len(at.dataframe) > 0, "No dataframe rendered in the app"
            
            # Check the markdown headers
            markdowns = [md.value for md in at.markdown]
            assert any("Act 4: Final Benchmark Outcomes" in md for md in markdowns)

    def test_outcomes_board_renders_fallback(self, mock_dates):
        """Verify the fallback message is rendered when strategy_returns is missing."""
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

            assert not at.exception, f"App crashed: {at.exception}"
            
            infos = [info.value for info in at.info]
            assert "Final outcomes data is not available." in infos

    def test_outcomes_board_renders_error_gracefully(self, mock_dates):
        """Verify that a failure in compute_ml_analysis is handled gracefully."""
        def _mock_run_pipeline(self, *args, **kwargs):
            return (pd.DataFrame({"spy_close": range(100)}, index=mock_dates), "LIVE", None, None)
            
        def _mock_compute_ml_failure(self, df, rf_features=None, target_col="baseline_regime"):
            raise ValueError("Injected pipeline failure")

        with patch("green_rock.service_layer.pipeline.DataPipeline.run_pipeline", _mock_run_pipeline), \
             patch("green_rock.service_layer.pipeline.DataPipeline.compute_ml_analysis", _mock_compute_ml_failure):
            at = AppTest.from_file(str(APP_PATH))
            at.run(timeout=10)

            assert not at.exception, f"App crashed: {at.exception}"
            
            warnings = [w.value for w in at.warning]
            assert any("Machine Learning analysis could not be completed." in w for w in warnings)
            
            infos = [info.value for info in at.info]
            assert "Final outcomes data is not available." in infos

    def test_outcomes_board_invalid_agreement_rate(self, mock_dates):
        """Verify that an invalid agreement_rate degrades to N/A without crashing."""
        def _mock_run_pipeline(self, *args, **kwargs):
            return (pd.DataFrame({"spy_close": range(100)}, index=mock_dates), "LIVE", None, None)
            
        def _mock_compute_ml(self, df, rf_features=None, target_col="baseline_regime"):
            return (
                _build_ml_dataframe(mock_dates),
                {"spy_close": 0.6, "tlt_close": 0.4},
                {"baseline_latest": "High", "rf_latest": "High", "agreement_rate": "invalid_string",
                 "divergence_count": 10, "total_test_days": 20},
                {"base_value": 0.35, "spy_close": 0.12, "tlt_close": -0.08, "predicted_class": "High"},
                pd.DataFrame({
                    "Strategy": ["Baseline MA", "Random Forest"],
                    "Cumulative Return": [15.0, 22.0],
                    "Max Drawdown": [5.0, 4.0]
                }),
            )

        with patch("green_rock.service_layer.pipeline.DataPipeline.run_pipeline", _mock_run_pipeline), \
             patch("green_rock.service_layer.pipeline.DataPipeline.compute_ml_analysis", _mock_compute_ml):
            at = AppTest.from_file(str(APP_PATH))
            at.run(timeout=10)

            assert not at.exception, f"App crashed with invalid agreement_rate: {at.exception}"
            
            # Find the delta metric for Random Forest Regime and verify it shows N/A
            # Streamlit test API might not expose metric deltas directly in an easy way,
            # but we can verify it doesn't crash.
            metrics = at.metric
            rf_metric = next((m for m in metrics if m.label == "Random Forest Regime"), None)
            assert rf_metric is not None, "Random Forest Regime metric not found"
            assert rf_metric.delta == "N/A", f"Expected delta to be N/A, got {rf_metric.delta}"
