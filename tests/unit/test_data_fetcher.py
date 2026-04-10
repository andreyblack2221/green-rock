import pytest
import pandas as pd
import numpy as np
import concurrent.futures
from unittest.mock import patch, MagicMock
from green_rock.adapters.data_fetcher import DataFetcher, fetch_yfinance_data, fetch_fred_data


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------

def test_fetch_live_data_success():
    fetcher = DataFetcher()
    
    # Mock successful response
    mock_prices = pd.DataFrame(
        {"spy_close": [100.0, 101.0], "tlt_close": [50.0, 51.0], "gld_close": [10.0, 11.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02"])
    )
    mock_yield = pd.DataFrame(
        {"yield_spread_10y_2y": [1.1, 1.2]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02"])
    )
    
    with patch('green_rock.adapters.data_fetcher.fetch_yfinance_data', return_value=mock_prices), \
         patch('green_rock.adapters.data_fetcher.fetch_fred_data', return_value=mock_yield):
        
        df = fetcher.fetch_live_data("2020-01-01", "2020-01-02")
        
        assert not df.empty
        assert "spy_close" in df.columns
        assert "yield_spread_10y_2y" in df.columns
        assert "spy_volatility_20d" in df.columns

def test_fetch_live_data_timeout():
    fetcher = DataFetcher()
    
    # Simulate a timeout — both futures must be mocked to avoid accidental network calls
    with patch('green_rock.adapters.data_fetcher.fetch_yfinance_data', side_effect=RuntimeError("Timeout")), \
         patch('green_rock.adapters.data_fetcher.fetch_fred_data', return_value=pd.DataFrame()):
        with pytest.raises(RuntimeError):
            fetcher.fetch_live_data("2020-01-01", "2020-01-02")

def test_fetch_yfinance_data_empty_warning():
    with patch('green_rock.adapters.data_fetcher.yf.Ticker') as mock_ticker:
        # Mock returning an empty DataFrame
        mock_hist = MagicMock(return_value=pd.DataFrame())
        mock_ticker.return_value.history = mock_hist
        
        with pytest.warns(RuntimeWarning, match="Ticker 'SPY' returned an empty DataFrame"):
            df = fetch_yfinance_data(["SPY"], "2020-01-01", "2020-01-02")
        
        assert df.empty

def test_fetch_live_data_naive_timezone():
    fetcher = DataFetcher()
    
    # Mock successful response with completely NAIVE timezones
    mock_prices = pd.DataFrame(
        {"spy_close": [100.0, 101.0], "tlt_close": [50.0, 51.0], "gld_close": [10.0, 11.0]},
        index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"]) # tz=None implicitly
    )
    mock_yield = pd.DataFrame(
        {"yield_spread_10y_2y": [1.1, 1.2]},
        index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"])
    )
    
    with patch('green_rock.adapters.data_fetcher.fetch_yfinance_data', return_value=mock_prices), \
         patch('green_rock.adapters.data_fetcher.fetch_fred_data', return_value=mock_yield):
        
        # It should not crash on `tz_convert` if `tz is None`
        df = fetcher.fetch_live_data("2020-01-01", "2020-01-02")
        
        assert not df.empty
        assert df.index.tz is None


# ---------------------------------------------------------------------------
# NEW: fetch_yfinance_data — API exception wrapping (P0)
# ---------------------------------------------------------------------------

def test_fetch_yfinance_data_api_exception_wraps_runtime_error():
    """When yf.Ticker().history() raises, it must be wrapped in RuntimeError."""
    with patch('green_rock.adapters.data_fetcher.yf.Ticker') as mock_ticker:
        mock_ticker.return_value.history.side_effect = ConnectionError("Network down")
        
        with pytest.raises(RuntimeError, match="Failed to fetch SPY from yfinance"):
            fetch_yfinance_data(["SPY"], "2020-01-01", "2020-01-02")


# ---------------------------------------------------------------------------
# NEW: fetch_fred_data — API exception wrapping (P0)
# ---------------------------------------------------------------------------

def test_fetch_fred_data_api_exception_wraps_runtime_error():
    """When pdr.get_data_fred() raises, it must be wrapped in RuntimeError."""
    with patch('green_rock.adapters.data_fetcher.pdr.get_data_fred', side_effect=Exception("FRED unreachable")):
        with pytest.raises(RuntimeError, match="Failed to fetch FRED series 'T10Y2Y'"):
            fetch_fred_data("T10Y2Y", "yield_spread_10y_2y", "2020-01-01", "2020-01-02")


# ---------------------------------------------------------------------------
# NEW: fetch_fred_data — column rename correctness (P2)
# ---------------------------------------------------------------------------

def test_fetch_fred_data_renames_column_correctly():
    """Verify the returned DataFrame column is renamed to the provided col_name."""
    mock_df = pd.DataFrame(
        {"T10Y2Y": [1.5, 1.6]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02"])
    )
    with patch('green_rock.adapters.data_fetcher.pdr.get_data_fred', return_value=mock_df):
        result = fetch_fred_data("T10Y2Y", "my_custom_name", "2020-01-01", "2020-01-02")
        
        assert "my_custom_name" in result.columns
        assert "T10Y2Y" not in result.columns


# ---------------------------------------------------------------------------
# NEW: fetch_live_data — concurrent.futures.TimeoutError path (P1)
# ---------------------------------------------------------------------------

def test_fetch_live_data_concurrent_timeout_error():
    """Verify that concurrent.futures.TimeoutError is caught and wrapped in RuntimeError."""
    fetcher = DataFetcher()
    
    with patch('green_rock.adapters.data_fetcher.fetch_yfinance_data') as mock_yf, \
         patch('green_rock.adapters.data_fetcher.fetch_fred_data') as mock_fred:
        
        # Make the first future hang beyond the deadline by raising TimeoutError
        # when .result() is called
        import time
        def slow_yfinance(*args, **kwargs):
            time.sleep(5)  # longer than the 1.9s deadline
            return pd.DataFrame()
        
        mock_yf.side_effect = slow_yfinance
        mock_fred.return_value = pd.DataFrame()
        
        with pytest.raises(RuntimeError, match="timed out"):
            fetcher.fetch_live_data("2020-01-01", "2020-01-02")


# ---------------------------------------------------------------------------
# NEW: fetch_live_data — prices_df.empty guard (P1)
# ---------------------------------------------------------------------------

def test_fetch_live_data_empty_prices_raises():
    """When yfinance returns an empty price DataFrame, RuntimeError is raised."""
    fetcher = DataFetcher()
    
    with patch('green_rock.adapters.data_fetcher.fetch_yfinance_data', return_value=pd.DataFrame()), \
         patch('green_rock.adapters.data_fetcher.fetch_fred_data', return_value=pd.DataFrame()):
        
        with pytest.raises(RuntimeError, match="No price data fetched"):
            fetcher.fetch_live_data("2020-01-01", "2020-01-02")


# ---------------------------------------------------------------------------
# NEW: fetch_live_data — tz-aware index stripping (P1)
# ---------------------------------------------------------------------------

def test_fetch_live_data_tz_aware_index_gets_stripped():
    """When yfinance and FRED return tz-aware indices, they must be converted to naive."""
    fetcher = DataFetcher()
    
    tz_aware_index = pd.DatetimeIndex(["2020-01-01", "2020-01-02"], tz="US/Eastern")
    mock_prices = pd.DataFrame(
        {"spy_close": [100.0, 101.0], "tlt_close": [50.0, 51.0], "gld_close": [10.0, 11.0]},
        index=tz_aware_index
    )
    mock_yield = pd.DataFrame(
        {"yield_spread_10y_2y": [1.1, 1.2]},
        index=pd.DatetimeIndex(["2020-01-01", "2020-01-02"], tz="UTC")
    )
    
    with patch('green_rock.adapters.data_fetcher.fetch_yfinance_data', return_value=mock_prices), \
         patch('green_rock.adapters.data_fetcher.fetch_fred_data', return_value=mock_yield):
        
        df = fetcher.fetch_live_data("2020-01-01", "2020-01-02")
        
        assert df.index.tz is None
        assert not df.empty


# ---------------------------------------------------------------------------
# NEW: fetch_live_data — volatility short-circuit for short datasets (P2)
# ---------------------------------------------------------------------------

def test_fetch_live_data_short_dataset_volatility_defaults_to_zero():
    """When merged data has < 20 rows, spy_volatility_20d must default to 0.0."""
    fetcher = DataFetcher()
    
    # Only 5 rows — well below the 20-row threshold
    dates = pd.date_range("2020-01-01", periods=5, freq="B")
    mock_prices = pd.DataFrame(
        {"spy_close": np.random.uniform(100, 110, 5),
         "tlt_close": np.random.uniform(50, 55, 5),
         "gld_close": np.random.uniform(10, 12, 5)},
        index=dates
    )
    mock_yield = pd.DataFrame(
        {"yield_spread_10y_2y": np.random.uniform(1.0, 2.0, 5)},
        index=dates
    )
    
    with patch('green_rock.adapters.data_fetcher.fetch_yfinance_data', return_value=mock_prices), \
         patch('green_rock.adapters.data_fetcher.fetch_fred_data', return_value=mock_yield):
        
        df = fetcher.fetch_live_data("2020-01-01", "2020-01-10")
        
        assert "spy_volatility_20d" in df.columns
        assert (df["spy_volatility_20d"] == 0.0).all()
