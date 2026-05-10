import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from green_rock.service_layer.pipeline import DataPipeline

@pytest.fixture
def mock_data_fetcher():
    fetcher = MagicMock()
    df = pd.DataFrame({
        "spy_close": np.linspace(100, 200, 250),
        "tlt_close": np.linspace(100, 50, 250),
        "gld_close": np.linspace(50, 100, 250),
        "volume": np.random.randint(1000, 5000, 250)
    })
    fetcher.fetch_live_data.return_value = df
    return fetcher
    
@pytest.fixture
def mock_file_repository():
    return MagicMock()

def test_pipeline_run_pipeline_with_rf(mock_data_fetcher, mock_file_repository):
    """[P0] Integration: test DataPipeline running RF classification"""
    pipeline = DataPipeline(data_fetcher=mock_data_fetcher, file_repository=mock_file_repository)
    
    # Run full pipeline with rf_features
    df, status, importances, _ = pipeline.run_pipeline(
        start_date="2020-01-01",
        compute_baseline=True,
        compute_rf=True,
        rf_features=["spy_close"]
    )
    
    assert status == "LIVE"
    assert "baseline_regime" in df.columns
    assert "rf_prediction" in df.columns
    assert "is_test" in df.columns
    assert isinstance(importances, dict)
    assert "spy_close" in importances

def test_pipeline_run_pipeline_rf_missing_baseline(mock_data_fetcher, mock_file_repository):
    """[P1] Integration: pipeline running RF without computing baseline (should raise ValueError)"""
    pipeline = DataPipeline(data_fetcher=mock_data_fetcher, file_repository=mock_file_repository)
    
    with pytest.raises(ValueError, match="compute_baseline must be True if compute_rf is True"):
        pipeline.run_pipeline(
            start_date="2020-01-01",
            compute_baseline=False,
            compute_rf=True,
            rf_features=["spy_close"]
        )
