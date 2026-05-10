"""
E2E tests for Act 3: XAI Waterfall rendering in Streamlit (Story 3.1, AC 2, 3).
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


class TestAct3XaiRendering:
    """[P0] Verify Act 3 XAI Waterfall renders in the Streamlit dashboard."""

    def test_three_plotly_charts_rendered(self, mock_dates):
        """AC2: Dashboard should render 3 charts — baseline, feature importance, XAI waterfall."""
        with patch("green_rock.entrypoints.streamlit_app.DataPipeline") as MockPipeline:
            mock_instance = MockPipeline.return_value
            mock_instance.run_pipeline.return_value = (
                pd.DataFrame({"spy_close": range(100)}, index=mock_dates),
                "LIVE",
                None,
                None,
            )
            mock_instance.compute_ml_analysis.return_value = (
                _build_ml_dataframe(mock_dates),
                {"spy_close": 0.6, "tlt_close": 0.4},
                {"baseline_latest": "High", "rf_latest": "High", "agreement_rate": 50.0,
                 "divergence_count": 10, "total_test_days": 20},
                {"base_value": 0.35, "spy_close": 0.12, "tlt_close": -0.08, "predicted_class": "High"},
                {"baseline_cumulative": 0.1, "rf_cumulative": 0.2, "benchmark_60_40": 0.05, "benchmark_spy": 0.08},
            )

            at = AppTest.from_file(str(APP_PATH))
            at.run(timeout=10)

            assert not at.exception, f"App crashed: {at.exception}"
            charts = at.get("plotly_chart")
            assert len(charts) >= 3, (
                f"Expected at least 3 Plotly charts (baseline + importance + XAI waterfall), found {len(charts)}"
            )

    def test_act3_section_heading_present(self, mock_dates):
        """AC2: 'Act 3' narrative section must be present in dashboard markdown."""
        with patch("green_rock.entrypoints.streamlit_app.DataPipeline") as MockPipeline:
            mock_instance = MockPipeline.return_value
            mock_instance.run_pipeline.return_value = (
                pd.DataFrame({"spy_close": range(100)}, index=mock_dates),
                "LIVE",
                None,
                None,
            )
            mock_instance.compute_ml_analysis.return_value = (
                _build_ml_dataframe(mock_dates),
                {"spy_close": 0.6, "tlt_close": 0.4},
                {"baseline_latest": "High", "rf_latest": "High", "agreement_rate": 50.0,
                 "divergence_count": 10, "total_test_days": 20},
                {"base_value": 0.35, "spy_close": 0.12, "tlt_close": -0.08, "predicted_class": "High"},
                {"baseline_cumulative": 0.1, "rf_cumulative": 0.2, "benchmark_60_40": 0.05, "benchmark_spy": 0.08},
            )

            at = AppTest.from_file(str(APP_PATH))
            at.run(timeout=10)

            assert not at.exception, f"App crashed: {at.exception}"
            markdown_texts = [m.value for m in at.markdown]
            act3_found = any("Act 3" in text for text in markdown_texts)
            assert act3_found, f"'Act 3' heading not found in markdown: {markdown_texts}"


class TestAct3GracefulDegradation:
    """[P1] Resilience: XAI failures should not crash the dashboard."""

    def test_xai_none_shows_info_message(self, mock_dates):
        """When xai_attribution is None, dashboard should show info message, not crash."""
        # Patch at class-method level so the mock persists into AppTest's isolated context
        def _mock_compute_ml(self, df, rf_features, target_col="baseline_regime"):
            return (
                _build_ml_dataframe(mock_dates),
                {"spy_close": 0.6, "tlt_close": 0.4},
                {"baseline_latest": "High", "rf_latest": "High", "agreement_rate": 50.0,
                 "divergence_count": 10, "total_test_days": 20},
                None,  # No XAI data
                {"baseline_cumulative": 0.1, "rf_cumulative": 0.2, "benchmark_60_40": 0.05, "benchmark_spy": 0.08},
            )

        with patch("green_rock.service_layer.pipeline.DataPipeline.compute_ml_analysis",
                   _mock_compute_ml):

            at = AppTest.from_file(str(APP_PATH))
            at.run(timeout=10)

            assert not at.exception, f"Dashboard crashed when XAI is None: {at.exception}"
            info_texts = [i.value for i in at.info]
            assert any("XAI" in t or "attribution" in t for t in info_texts), (
                f"Expected info message about XAI unavailability, got: {info_texts}"
            )

    def test_xai_visualization_error_shows_warning(self, mock_dates):
        """When plot_xai_waterfall raises, dashboard should show warning, not crash."""
        # Patch at the source module level so the mock survives AppTest re-import
        with patch("green_rock.entrypoints.visualizations.plot_xai_waterfall",
                   side_effect=ValueError("Simulated rendering failure")):

            at = AppTest.from_file(str(APP_PATH))
            at.run(timeout=10)

            assert not at.exception, f"Dashboard crashed on XAI rendering error: {at.exception}"
            warning_texts = [w.value for w in at.warning]
            assert any("XAI" in w for w in warning_texts), (
                f"Expected warning about XAI failure, got: {warning_texts}"
            )

    def test_full_ml_failure_still_renders_baseline(self, mock_dates):
        """When entire ML analysis fails, baseline chart must still render."""
        with patch("green_rock.service_layer.pipeline.DataPipeline.compute_ml_analysis",
                   side_effect=Exception("Complete ML pipeline failure")):

            at = AppTest.from_file(str(APP_PATH))
            at.run(timeout=10)

            assert not at.exception, f"Dashboard crashed entirely: {at.exception}"
            charts = at.get("plotly_chart")
            assert len(charts) >= 1, "At least baseline chart should render on ML failure"
