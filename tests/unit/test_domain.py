import pytest
import pandas as pd
import numpy as np
from green_rock.domain.quant_model import calculate_baseline_regime


def test_calculate_baseline_regime_columns_present():
    """Test that the output DataFrame contains the expected derived columns."""
    df = pd.DataFrame({
        "spy_close": np.concatenate([
            np.linspace(100, 150, 100),  # Uptrend
            np.linspace(150, 100, 100),  # Downtrend
            np.linspace(100, 100, 50),   # Flat
        ])
    })
    result_df = calculate_baseline_regime(df, short_window=10, long_window=50)

    assert "baseline_regime" in result_df.columns
    assert "short_ma" in result_df.columns
    assert "long_ma" in result_df.columns

    # All valid (non-warm-up) rows must carry one of the three regime labels
    valid_results = result_df.dropna(subset=["baseline_regime"])
    assert len(valid_results) > 0
    assert set(valid_results["baseline_regime"].unique()).issubset({"Low", "Medium", "High"})


def test_calculate_baseline_regime_low_risk():
    """Test that a sustained uptrend deterministically produces a 'Low' risk regime."""
    # Monotonic uptrend: short MA (window=2) will be above long MA (window=3) by >1%
    df = pd.DataFrame({"spy_close": np.linspace(100, 200, 10)})
    result_df = calculate_baseline_regime(df, short_window=2, long_window=3)

    last_valid = result_df.dropna(subset=["baseline_regime"])
    assert last_valid.iloc[-1]["baseline_regime"] == "Low"


def test_calculate_baseline_regime_high_risk():
    """Test that a sustained downtrend deterministically produces a 'High' risk regime."""
    # Monotonic downtrend: short MA (window=2) will be below long MA (window=3) by >1%
    df = pd.DataFrame({"spy_close": np.linspace(200, 100, 10)})
    result_df = calculate_baseline_regime(df, short_window=2, long_window=3)

    last_valid = result_df.dropna(subset=["baseline_regime"])
    assert last_valid.iloc[-1]["baseline_regime"] == "High"


def test_calculate_baseline_regime_warm_up_rows_are_nan():
    """Test that warm-up rows (before long_window is satisfied) carry np.nan, not a label."""
    df = pd.DataFrame({"spy_close": np.linspace(100, 110, 10)})
    result_df = calculate_baseline_regime(df, short_window=2, long_window=5)

    # First long_window - 1 rows should be nan
    warm_up = result_df.iloc[: 5 - 1]
    assert warm_up["baseline_regime"].isna().all()


def test_calculate_baseline_regime_missing_spy_close():
    """Test that a missing spy_close column raises KeyError."""
    with pytest.raises(KeyError):
        # Use small windows so the row-count guard does not fire before the column check
        df = pd.DataFrame({"wrong_column": range(10)})
        calculate_baseline_regime(df, short_window=2, long_window=5)


def test_calculate_baseline_regime_invalid_windows():
    """Test that non-positive or inverted window parameters raise ValueError."""
    df = pd.DataFrame({"spy_close": range(50)})
    with pytest.raises(ValueError):
        calculate_baseline_regime(df, short_window=0, long_window=10)
    with pytest.raises(ValueError):
        calculate_baseline_regime(df, short_window=10, long_window=5)
    with pytest.raises(ValueError):
        calculate_baseline_regime(df, short_window=10, long_window=10)


def test_calculate_baseline_regime_too_few_rows():
    """Test that a DataFrame with fewer rows than long_window raises ValueError."""
    df = pd.DataFrame({"spy_close": range(5)})
    with pytest.raises(ValueError, match="fewer than long_window"):
        calculate_baseline_regime(df, short_window=2, long_window=10)


def test_calculate_baseline_regime_handles_nans():
    """Test that individual NaNs in prices propagate correctly to regime NaNs."""
    df = pd.DataFrame({"spy_close": [100.0, 101.0, np.nan, 103.0, 104.0]})
    # With window=2, the NaN at index 2 will make short_ma NaN at indices 2 and 3.
    result_df = calculate_baseline_regime(df, short_window=2, long_window=3)
    
    # Indices 0,1 are warm-up. Index 2 has np.nan in price. Index 3 has np.nan in long_ma (window 2-3 contains NaN).
    # So index 2 and 3 should be NaN in baseline_regime.
    assert pd.isna(result_df["baseline_regime"].iloc[2])
    assert pd.isna(result_df["baseline_regime"].iloc[3])


def test_calculate_baseline_regime_medium_spread():
    """Test that a small spread (within 1%) produces 'Medium' risk."""
    # short_ma = 100.5, long_ma = 100.0 => ratio 1.005 (within 1.01 boundary)
    df = pd.DataFrame({"spy_close": [100.0, 100.0, 100.0, 101.0, 100.0]})
    # long_window=3, short_window=2
    # At index 4: prices [100.0, 101.0, 100.0]. Mean = 100.33...
    # Short window (2): [101.0, 100.0]. Mean = 100.5.
    # 100.5 / 100.33... = 1.0016... < 1.01.
    result_df = calculate_baseline_regime(df, short_window=2, long_window=3)
    assert result_df["baseline_regime"].iloc[-1] == "Medium"

def test_calculate_baseline_regime_duplicate_index():
    """Test that duplicate indices do not crash the computation (row-order based)."""
    dates = ["2020-01-01", "2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04"]
    df = pd.DataFrame({"spy_close": np.linspace(100, 110, 5)}, index=dates)
    
    # Should calculate based on row position, not index value
    result_df = calculate_baseline_regime(df, short_window=2, long_window=3)
    assert len(result_df) == 5
    assert "baseline_regime" in result_df.columns
