import os
import pytest
import pandas as pd
from unittest.mock import patch
from green_rock.adapters.file_repository import FileRepository

@patch('pandas.read_csv')
def test_read_snapshot_success(mock_read_csv):
    mock_df = pd.DataFrame({
        "date": ["2020-01-01"],
        "spy_close": [100.0],
        "tlt_close": [50.0],
        "gld_close": [10.0],
        "yield_spread_10y_2y": [1.1]
    })
    mock_df.set_index("date", inplace=True)
    mock_read_csv.return_value = mock_df
    
    repo = FileRepository(data_dir="/tmp/data")
    df = repo.read_snapshot("static_snapshot.csv")
    
    assert not df.empty
    assert "spy_close" in df.columns
    mock_read_csv.assert_called_once_with(os.path.join("/tmp/data", "static_snapshot.csv"), index_col="date", parse_dates=True)

def test_read_snapshot_not_found():
    repo = FileRepository(data_dir="/tmp/data")
    with pytest.raises(FileNotFoundError):
        repo.read_snapshot("non_existent.csv")

@patch('pandas.read_csv')
def test_read_snapshot_short_data(mock_read_csv):
    # Setup data with len < 20 (only 2 dates)
    mock_df = pd.DataFrame({
        "date": ["2020-01-01", "2020-01-02"],
        "spy_close": [100.0, 101.0],
        "tlt_close": [50.0, 51.0],
        "gld_close": [10.0, 11.0],
        "yield_spread_10y_2y": [1.1, 1.2]
    })
    mock_df.set_index("date", inplace=True)
    mock_read_csv.return_value = mock_df
    
    repo = FileRepository(data_dir="/tmp/data")
    df = repo.read_snapshot("static_snapshot.csv")
    
    # 20d volatility should be set to 0.0 on len < 20
    assert not df.empty
    assert "spy_volatility_20d" in df.columns
    assert df["spy_volatility_20d"].iloc[0] == 0.0
    assert df["spy_volatility_20d"].iloc[-1] == 0.0


# ---------------------------------------------------------------------------
# NEW: Default data_dir resolution (P1)
# ---------------------------------------------------------------------------

def test_file_repository_default_data_dir():
    """When no data_dir is specified, FileRepository resolves to project-root/data."""
    repo = FileRepository()
    
    # The default path should end with /data and should be an absolute path
    assert os.path.isabs(repo.data_dir)
    assert repo.data_dir.endswith("data")
    # Verify it navigates up 3 levels from the file_repository.py location
    expected_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../src/green_rock/adapters/file_repository.py')
        ))
    )))
    expected_data = os.path.join(expected_root, "data")
    assert repo.data_dir == expected_data

