"""
Integration tests for strategy returns flowing through compute_ml_analysis
(Story 4.1: Financial Allocation & Benchmarking Engine).

Tests cover:
  - AC1+AC2: compute_ml_analysis returns strategy_returns as a pd.DataFrame
  - Negative: strategy_returns degrades to empty DataFrame when price data missing
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from green_rock.service_layer.pipeline import DataPipeline


@pytest.fixture
def mock_pipeline_with_price_data():
    """Pipeline with synthetic data containing SPY, TLT, GLD prices — enough for RF training."""
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
        "volume": np.random.RandomState(42).randint(1000, 5000, n_rows),
    })
    fetcher.fetch_live_data.return_value = df
    pipeline = DataPipeline(data_fetcher=fetcher, file_repository=MagicMock())
    return pipeline


class TestPipelineStrategyReturnsIntegration:
    """[P0] Integration: verify strategy_returns flows through compute_ml_analysis."""

    def test_strategy_returns_is_dataframe(self, mock_pipeline_with_price_data):
        """I1: compute_ml_analysis returns strategy_returns as a pd.DataFrame."""
        pipeline = mock_pipeline_with_price_data
        df, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        rf_features = ["spy_close", "tlt_close"]
        _, _, _, _, strategy_returns = pipeline.compute_ml_analysis(df, rf_features)

        assert isinstance(strategy_returns, pd.DataFrame)
        assert not strategy_returns.empty

    def test_strategy_returns_has_expected_columns(self, mock_pipeline_with_price_data):
        """I1b: The DataFrame must contain Strategy, Cumulative Return, and Max Drawdown columns."""
        pipeline = mock_pipeline_with_price_data
        df, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        rf_features = ["spy_close", "tlt_close"]
        _, _, _, _, strategy_returns = pipeline.compute_ml_analysis(df, rf_features)

        expected_cols = {"Strategy", "Cumulative Return", "Max Drawdown"}
        assert expected_cols.issubset(set(strategy_returns.columns))

    def test_strategy_returns_has_four_strategy_rows(self, mock_pipeline_with_price_data):
        """I1c: The DataFrame must contain exactly 4 rows (Baseline, RF, 60/40, S&P 500)."""
        pipeline = mock_pipeline_with_price_data
        df, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        rf_features = ["spy_close", "tlt_close"]
        _, _, _, _, strategy_returns = pipeline.compute_ml_analysis(df, rf_features)

        assert len(strategy_returns) == 4
        expected_strategies = {"Baseline MA", "Random Forest", "60/40 Portfolio", "S&P 500"}
        assert set(strategy_returns["Strategy"]) == expected_strategies

    def test_strategy_returns_values_are_numeric(self, mock_pipeline_with_price_data):
        """I2: Cumulative Return and Max Drawdown values must be numeric."""
        pipeline = mock_pipeline_with_price_data
        df, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        rf_features = ["spy_close", "tlt_close"]
        _, _, _, _, strategy_returns = pipeline.compute_ml_analysis(df, rf_features)

        for col in ["Cumulative Return", "Max Drawdown"]:
            assert strategy_returns[col].dtype in [np.float64, np.float32, float], \
                f"Column '{col}' has dtype {strategy_returns[col].dtype}, expected float"

    def test_compute_ml_analysis_uses_default_features(self, mock_pipeline_with_price_data):
        """I4: compute_ml_analysis with None rf_features uses internal defaults.
        The default features include columns not in our synthetic data (e.g. yield_spread_10y_2y),
        so a KeyError is the expected, correct behaviour."""
        pipeline = mock_pipeline_with_price_data
        df, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        # Default features reference columns absent from synthetic data → must raise KeyError
        with pytest.raises(KeyError):
            pipeline.compute_ml_analysis(df)


class TestPipelineStrategyReturnsNegativePaths:
    """[P1] Negative paths: strategy_returns degrades gracefully."""

    def test_strategy_returns_empty_when_price_columns_missing(self):
        """I3: When price columns (tlt_close, gld_close) are absent, strategy_returns is empty DataFrame."""
        fetcher = MagicMock()
        n_rows = 500
        spy_close = np.concatenate([
            np.linspace(100, 150, 200),
            np.linspace(150, 140, 100),
            np.linspace(140, 145, 200),
        ])
        # Deliberately omit tlt_close and gld_close
        df = pd.DataFrame({
            "spy_close": spy_close,
        })
        fetcher.fetch_live_data.return_value = df
        pipeline = DataPipeline(data_fetcher=fetcher, file_repository=MagicMock())

        df_regime, _, _, _ = pipeline.run_pipeline(compute_baseline=True, compute_rf=False)

        # compute_ml_analysis should catch the KeyError and return empty DataFrame
        _, _, _, _, strategy_returns = pipeline.compute_ml_analysis(df_regime, ["spy_close"])

        assert isinstance(strategy_returns, pd.DataFrame)
        assert strategy_returns.empty
