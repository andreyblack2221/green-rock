import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from scripts.generate_snapshot import fetch_yfinance_data, fetch_fred_data, generate_snapshot

class TestGenerateSnapshot:
    """[P0] Unit tests for offline data snapshot generator script"""

    @patch("scripts.generate_snapshot.yf.Ticker")
    def test_fetch_yfinance_data_success(self, mock_ticker):
        """[P0] Should fetch data and format columns to snake_case"""
        mock_df = pd.DataFrame({"Close": [100.0]}, index=pd.to_datetime(["2020-01-01"]))
        mock_instance = MagicMock()
        mock_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_instance
        
        result = fetch_yfinance_data(["SPY"], "2020-01-01", "2020-01-02")
        
        assert not result.empty
        assert list(result.columns) == ["spy_close"]
        assert result.iloc[0]["spy_close"] == 100.0

    @patch("scripts.generate_snapshot.yf.Ticker")
    def test_fetch_yfinance_data_invalid_ticker(self, mock_ticker):
        """[P1] Should return empty DataFrame when ticker returns empty data"""
        mock_instance = MagicMock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_instance
        
        result = fetch_yfinance_data(["INVALID"], "2020-01-01", "2020-01-02")
        
        assert result.empty

    @patch("scripts.generate_snapshot.yf.Ticker")
    def test_fetch_yfinance_data_network_error(self, mock_ticker):
        """[P1] Should raise RuntimeError on network exception"""
        mock_instance = MagicMock()
        mock_instance.history.side_effect = Exception("Network timeout")
        mock_ticker.return_value = mock_instance
        
        with pytest.raises(RuntimeError, match="Failed to fetch SPY from yfinance"):
            fetch_yfinance_data(["SPY"], "2020-01-01", "2020-01-02")

    @patch("scripts.generate_snapshot.pdr.get_data_fred")
    def test_fetch_fred_data_success(self, mock_get_fred):
        """[P0] Should fetch FRED data and rename the column"""
        mock_df = pd.DataFrame({"T10Y2Y": [1.5]}, index=pd.to_datetime(["2020-01-01"]))
        mock_get_fred.return_value = mock_df
        
        result = fetch_fred_data("T10Y2Y", "yield_spread", "2020-01-01", "2020-01-02")
        
        assert not result.empty
        assert list(result.columns) == ["yield_spread"]

    @patch("scripts.generate_snapshot.pdr.get_data_fred")
    def test_fetch_fred_data_network_error(self, mock_get_fred):
        """[P1] Should raise RuntimeError on network exception for FRED"""
        mock_get_fred.side_effect = Exception("API rate limit")
        
        with pytest.raises(RuntimeError, match="Failed to fetch FRED series"):
            fetch_fred_data("T10Y2Y", "yield_spread", "2020-01-01", "2020-01-02")

    @patch("scripts.generate_snapshot.fetch_fred_data")
    @patch("scripts.generate_snapshot.fetch_yfinance_data")
    def test_generate_snapshot_success(self, mock_fetch_yf, mock_fetch_fred, tmp_path):
        """[P0] Should successfully generate snapshot with mock data handling ffill"""
        with patch("scripts.generate_snapshot._PROJECT_ROOT", str(tmp_path)):
            idx_yf = pd.DatetimeIndex(["2020-01-01", "2020-01-03"]).tz_localize("UTC")
            df_yf = pd.DataFrame({
                "spy_close": [100.0, 102.0],
                "tlt_close": [90.0, 92.0],
                "gld_close": [150.0, 152.0]
            }, index=idx_yf)
            
            idx_fred = pd.DatetimeIndex(["2020-01-01", "2020-01-02"])
            df_fred = pd.DataFrame({"yield_spread_10y_2y": [1.5, 1.6]}, index=idx_fred)
            
            mock_fetch_yf.return_value = df_yf
            mock_fetch_fred.return_value = df_fred
            
            generate_snapshot()
            
            out_file = tmp_path / "data" / "static_snapshot.csv"
            assert out_file.exists()
            
            saved_df = pd.read_csv(out_file)
            assert len(saved_df) == 3
            
            row_2 = saved_df[saved_df["date"] == "2020-01-02"].iloc[0]
            assert float(row_2["spy_close"]) == 100.0
            assert float(row_2["yield_spread_10y_2y"]) == 1.6
            
            row_3 = saved_df[saved_df["date"] == "2020-01-03"].iloc[0]
            assert float(row_3["spy_close"]) == 102.0
            assert float(row_3["yield_spread_10y_2y"]) == 1.6
        
    @patch("scripts.generate_snapshot.fetch_yfinance_data")
    def test_generate_snapshot_empty_price_data(self, mock_fetch_yf):
        """[P1] Should raise an error if yf returns completely empty data"""
        mock_fetch_yf.return_value = pd.DataFrame()
        with pytest.raises(RuntimeError, match="No price data was fetched for any ticker"):
            generate_snapshot()
