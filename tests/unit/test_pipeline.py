import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from green_rock.service_layer.pipeline import DataPipeline

def test_fetch_data_live_success():
    mock_fetcher = MagicMock()
    mock_repo = MagicMock()
    
    mock_df = pd.DataFrame({"spy_close": [10.0]})
    mock_fetcher.fetch_live_data.return_value = mock_df
    
    pipeline = DataPipeline(data_fetcher=mock_fetcher, file_repository=mock_repo)
    df, status = pipeline.get_data(start_date="2020-01-01", end_date="2020-01-02")
    
    assert status == "LIVE"
    assert not df.empty
    mock_fetcher.fetch_live_data.assert_called_once()
    mock_repo.read_snapshot.assert_not_called()

def test_fetch_data_fallback():
    mock_fetcher = MagicMock()
    mock_repo = MagicMock()
    
    mock_fetcher.fetch_live_data.side_effect = RuntimeError("Timeout or other error")
    mock_df = pd.DataFrame({"spy_close": [10.0]})
    mock_repo.read_snapshot.return_value = mock_df
    
    pipeline = DataPipeline(data_fetcher=mock_fetcher, file_repository=mock_repo)
    df, status = pipeline.get_data(start_date="2020-01-01", end_date="2020-01-02")
    
    assert status == "CACHED"
    assert not df.empty
    mock_fetcher.fetch_live_data.assert_called_once()
    mock_repo.read_snapshot.assert_called_once()

def test_fetch_data_total_failure():
    mock_fetcher = MagicMock()
    mock_repo = MagicMock()
    
    mock_fetcher.fetch_live_data.side_effect = RuntimeError("Timeout or other error")
    mock_repo.read_snapshot.side_effect = FileNotFoundError("No file")
    
    pipeline = DataPipeline(data_fetcher=mock_fetcher, file_repository=mock_repo)
    with pytest.raises(RuntimeError):
        pipeline.get_data()

def test_pipeline_programming_error_bypass():
    mock_fetcher = MagicMock()
    mock_repo = MagicMock()
    
    # Simulate a programming error like AttributeError or TypeError
    mock_fetcher.fetch_live_data.side_effect = AttributeError("'DataFrame' object has no attribute 'invalid'")
    
    pipeline = DataPipeline(data_fetcher=mock_fetcher, file_repository=mock_repo)
    
    # It should not be caught by the fallback logic
    with pytest.raises(AttributeError):
        pipeline.get_data(start_date="2020-01-01", end_date="2020-01-02")
        
    mock_fetcher.fetch_live_data.assert_called_once()
    mock_repo.read_snapshot.assert_not_called()


# ---------------------------------------------------------------------------
# NEW: Each narrowed exception type triggers fallback (P0)
# The except clause catches (RuntimeError, OSError, ValueError, TimeoutError).
# Existing tests only exercise RuntimeError — we must cover each variant.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("exc_type,exc_msg", [
    (OSError, "Connection refused"),
    (ValueError, "Invalid data format"),
    (TimeoutError, "Request timed out"),
])
def test_pipeline_fallback_on_narrowed_exception_types(exc_type, exc_msg):
    """Each narrowed exception type in the except clause must trigger fallback."""
    mock_fetcher = MagicMock()
    mock_repo = MagicMock()
    
    mock_fetcher.fetch_live_data.side_effect = exc_type(exc_msg)
    cached_df = pd.DataFrame({"spy_close": [42.0]})
    mock_repo.read_snapshot.return_value = cached_df
    
    pipeline = DataPipeline(data_fetcher=mock_fetcher, file_repository=mock_repo)
    df, status = pipeline.get_data(start_date="2020-01-01", end_date="2020-01-02")
    
    assert status == "CACHED"
    assert not df.empty
    mock_fetcher.fetch_live_data.assert_called_once()
    mock_repo.read_snapshot.assert_called_once()


# ---------------------------------------------------------------------------
# NEW: end_date defaults to today when omitted (P1)
# ---------------------------------------------------------------------------

def test_pipeline_end_date_defaults_to_today():
    """When end_date is not provided, pipeline should use today's date."""
    mock_fetcher = MagicMock()
    mock_repo = MagicMock()
    
    mock_df = pd.DataFrame({"spy_close": [10.0]})
    mock_fetcher.fetch_live_data.return_value = mock_df
    
    pipeline = DataPipeline(data_fetcher=mock_fetcher, file_repository=mock_repo)
    
    with patch('green_rock.service_layer.pipeline.datetime') as mock_dt:
        mock_dt.datetime.now.return_value.strftime.return_value = "2026-04-09"
        df, status = pipeline.get_data(start_date="2020-01-01")
    
    assert status == "LIVE"
    # Verify fetch_live_data was called with today's date as end_date
    call_args = mock_fetcher.fetch_live_data.call_args
    assert call_args[0][1] == "2026-04-09" or call_args[1].get("end_date") == "2026-04-09"


# ---------------------------------------------------------------------------
# NEW: Total failure preserves exception chain (P1)
# ---------------------------------------------------------------------------

def test_pipeline_total_failure_preserves_cause_chain():
    """Fatal RuntimeError must chain the original FileNotFoundError via __cause__."""
    mock_fetcher = MagicMock()
    mock_repo = MagicMock()
    
    live_err = RuntimeError("Network down")
    cache_err = FileNotFoundError("snapshot missing")
    mock_fetcher.fetch_live_data.side_effect = live_err
    mock_repo.read_snapshot.side_effect = cache_err
    
    pipeline = DataPipeline(data_fetcher=mock_fetcher, file_repository=mock_repo)
    
    with pytest.raises(RuntimeError) as exc_info:
        pipeline.get_data(start_date="2020-01-01", end_date="2020-01-02")
    
    # The raised RuntimeError must chain to the FileNotFoundError
    assert exc_info.value.__cause__ is cache_err
    assert "snapshot missing" in str(exc_info.value)

