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

def test_pipeline_includes_feature_importance_in_results(mock_data_fetcher):
    """
    [P0] Verify that the DataPipeline includes feature importance data 
    in its execution results for RF models.
    """
    pipeline = DataPipeline(data_fetcher=mock_data_fetcher, file_repository=MagicMock())
    # We need to ensure compute_rf=True and features are provided
    _, _, importances, _ = pipeline.run_pipeline(
        start_date="2020-01-01",
        compute_baseline=True,
        compute_rf=True,
        rf_features=["spy_close", "tlt_close"]
    )
    
    assert isinstance(importances, dict)
    # The pipeline might return None if the internal train_and_predict_rf fails
    # But with our improved mock data, it should succeed.
    assert importances is not None, "Pipeline returned None for importances"
    assert set(importances.keys()) == {"spy_close", "tlt_close"}
    assert all(0 <= v <= 1 for v in importances.values())
    # Importances should sum to 1.0 (RandomForest property)
    assert sum(importances.values()) == pytest.approx(1.0)
