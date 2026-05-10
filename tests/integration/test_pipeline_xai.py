import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from green_rock.service_layer.pipeline import DataPipeline


@pytest.fixture
def mock_data_fetcher():
    fetcher = MagicMock()
    # Create data with enough variation to ensure multiple regimes
    n_rows = 500
    spy_close = np.concatenate([
        np.linspace(100, 150, 200),  # Bullish
        np.linspace(150, 140, 100),  # Bearish
        np.linspace(140, 145, 200)   # Neutral
    ])
    df = pd.DataFrame({
        "spy_close": spy_close,
        "tlt_close": np.linspace(100, 50, n_rows),
        "gld_close": np.linspace(50, 100, n_rows),
        "volume": np.random.randint(1000, 5000, n_rows)
    })
    fetcher.fetch_live_data.return_value = df
    return fetcher


def test_compute_ml_analysis_returns_xai_attribution(mock_data_fetcher):
    """
    [P0] Integration: verify compute_ml_analysis returns a valid xai_attribution dict
    with base_value, predicted_class, and feature contribution keys (AC1, Subtask 5.2).
    """
    pipeline = DataPipeline(data_fetcher=mock_data_fetcher, file_repository=MagicMock())
    
    # First get baseline data
    df, status, _, _ = pipeline.run_pipeline(
        start_date="2020-01-01",
        compute_baseline=True,
        compute_rf=False
    )
    
    rf_features = ["spy_close", "tlt_close"]
    df_result, importances, comparative_metrics, xai_attribution, strategy_returns = pipeline.compute_ml_analysis(
        df, rf_features
    )
    
    # XAI attribution must be present
    assert xai_attribution is not None, "xai_attribution should not be None"
    assert isinstance(xai_attribution, dict)
    
    # Must contain required keys
    assert "base_value" in xai_attribution
    assert "predicted_class" in xai_attribution
    
    # Must contain one key per feature
    for feature in rf_features:
        assert feature in xai_attribution, f"Missing feature contribution for {feature}"
    
    # base_value + contributions should sum to a valid probability [0, 1]
    feature_contributions = sum(xai_attribution[f] for f in rf_features)
    total_prob = xai_attribution["base_value"] + feature_contributions
    assert 0.0 <= total_prob <= 1.0 + 1e-9, f"Total probability {total_prob} is out of bounds"
    
    # Predicted class must be a valid regime
    assert xai_attribution["predicted_class"] in {"Low", "Medium", "High"}
