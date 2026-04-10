import pytest
import datetime
import pandas as pd
from green_rock.service_layer.pipeline import DataPipeline


@pytest.mark.integration
def test_pipeline_integration():
    """
    Integration test:
    Attempts to use the real pipeline. It will either succeed via network (LIVE)
    or fall back to the csv (CACHED). In both cases, the returned object must be a valid DataFrame.
    """
    pipeline = DataPipeline()
    start_date = "2023-01-01"
    end_date = "2024-01-01"
    
    df, status = pipeline.get_data(start_date=start_date, end_date=end_date)
    
    assert status in ["LIVE", "CACHED"]
    assert not df.empty
    assert isinstance(df, pd.DataFrame)
    
    # Check if necessary columns exist
    assert "spy_close" in df.columns
    assert "spy_volatility_20d" in df.columns
    assert "yield_spread_10y_2y" in df.columns
