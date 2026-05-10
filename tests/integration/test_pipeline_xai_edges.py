"""
Integration tests for XAI attribution pipeline flow edge cases (Story 3.1, AC 1).
Extends test_pipeline_xai.py with negative-path and boundary coverage.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from green_rock.service_layer.pipeline import DataPipeline


@pytest.fixture
def mock_pipeline_with_data():
    """Pipeline with enough synthetic data for RF training."""
    fetcher = MagicMock()
    n_rows = 500
    spy_close = np.concatenate([
        np.linspace(100, 150, 200),  # Bullish
        np.linspace(150, 140, 100),  # Bearish
        np.linspace(140, 145, 200),  # Neutral
    ])
    df = pd.DataFrame({
        "spy_close": spy_close,
        "tlt_close": np.linspace(100, 50, n_rows),
        "gld_close": np.linspace(50, 100, n_rows),
        "volume": np.random.randint(1000, 5000, n_rows),
    })
    fetcher.fetch_live_data.return_value = df
    pipeline = DataPipeline(data_fetcher=fetcher, file_repository=MagicMock())
    return pipeline


class TestXaiPipelineIntegration:
    """[P0] Integration: verify XAI flows through compute_ml_analysis correctly."""

    def test_xai_attribution_keys_match_feature_cols(self, mock_pipeline_with_data):
        """XAI attribution dict must contain exactly the features passed to compute_ml_analysis."""
        pipeline = mock_pipeline_with_data
        df, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        rf_features = ["spy_close", "tlt_close", "gld_close"]
        _, _, _, xai_attribution, _ = pipeline.compute_ml_analysis(df, rf_features)

        assert xai_attribution is not None
        for f in rf_features:
            assert f in xai_attribution

    def test_xai_attribution_predicted_class_valid_regime(self, mock_pipeline_with_data):
        """predicted_class must be one of Low/Medium/High."""
        pipeline = mock_pipeline_with_data
        df, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        rf_features = ["spy_close", "tlt_close"]
        _, _, _, xai_attribution, _ = pipeline.compute_ml_analysis(df, rf_features)

        assert xai_attribution["predicted_class"] in {"Low", "Medium", "High"}

    def test_run_pipeline_returns_none_for_xai_position(self, mock_pipeline_with_data):
        """run_pipeline always returns None for XAI (position 4) — XAI comes from compute_ml_analysis only."""
        pipeline = mock_pipeline_with_data
        _, _, _, xai_from_run_pipeline = pipeline.run_pipeline(
            compute_baseline=True, compute_rf=True, rf_features=["spy_close", "tlt_close"]
        )
        assert xai_from_run_pipeline is None, "run_pipeline must return None for XAI (deferred to compute_ml_analysis)"

    def test_xai_attribution_uses_latest_test_row(self, mock_pipeline_with_data):
        """XAI attribution should use the latest row from the test set."""
        pipeline = mock_pipeline_with_data
        df, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        rf_features = ["spy_close", "tlt_close"]
        df_result, _, _, xai_attribution, _ = pipeline.compute_ml_analysis(df, rf_features)

        # The latest test row should have a prediction matching xai_attribution's predicted_class
        test_df = df_result[df_result["is_test"]].dropna(subset=["rf_prediction"])
        if not test_df.empty:
            latest_prediction = test_df["rf_prediction"].iloc[-1]
            assert xai_attribution["predicted_class"] == latest_prediction


class TestXaiPipelineNegativePaths:
    """[P1] Negative paths and resilience."""

    def test_compute_ml_analysis_xai_none_when_test_set_all_nan(self):
        """If all test set feature values are NaN, XAI should be None (no valid row to explain)."""
        fetcher = MagicMock()
        n_rows = 500
        spy_close = np.concatenate([
            np.linspace(100, 150, 200),
            np.linspace(150, 140, 100),
            np.linspace(140, 145, 200),
        ])
        df = pd.DataFrame({
            "spy_close": spy_close,
            "tlt_close": np.linspace(100, 50, n_rows),
        })
        fetcher.fetch_live_data.return_value = df
        pipeline = DataPipeline(data_fetcher=fetcher, file_repository=MagicMock())
        df_regime, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        # Contaminate the last 20% (test set) with NaN to force no valid XAI row
        split_idx = int(len(df_regime) * 0.8)
        df_regime.iloc[split_idx:, df_regime.columns.get_loc("spy_close")] = np.nan
        df_regime.iloc[split_idx:, df_regime.columns.get_loc("tlt_close")] = np.nan

        _, _, _, xai_attribution, _ = pipeline.compute_ml_analysis(df_regime, ["spy_close", "tlt_close"])
        assert xai_attribution is None, "XAI should be None when no valid test rows exist"
