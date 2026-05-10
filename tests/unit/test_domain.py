import pytest
import pandas as pd
import numpy as np
from green_rock.domain.quant_model import calculate_baseline_regime, calculate_comparative_metrics


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


def test_train_and_predict_rf_deterministic():
    from green_rock.domain.quant_model import train_and_predict_rf
    # Create simple synthetic data
    df = pd.DataFrame({
        "feature1": np.linspace(0, 10, 100),
        "feature2": np.linspace(10, 0, 100),
        "target_regime": ["Low"] * 33 + ["Medium"] * 34 + ["High"] * 33
    })
    
    result_df1, _, _ = train_and_predict_rf(df.copy(), feature_cols=["feature1", "feature2"], target_col="target_regime", test_ratio=0.2, random_state=42)
    result_df2, _, _ = train_and_predict_rf(df.copy(), feature_cols=["feature1", "feature2"], target_col="target_regime", test_ratio=0.2, random_state=42)
    
    # Must be deterministic
    pd.testing.assert_series_equal(result_df1["rf_prediction"], result_df2["rf_prediction"])
    
def test_train_and_predict_rf_time_split():
    from green_rock.domain.quant_model import train_and_predict_rf
    df = pd.DataFrame({
        "feature1": range(100),
        "target_regime": ["Low"] * 50 + ["High"] * 50
    })
    
    result_df, _, _ = train_and_predict_rf(df, feature_cols=["feature1"], target_col="target_regime", test_ratio=0.2)
    
    # In a time-series split of 100 rows with 0.2 ratio, the last 20 rows are test data.
    # The first 80 rows should have 'rf_prediction' as NaN or "Train" or empty, or maybe the function predicts for all rows?
    # Usually we only predict on test data, or we predict on all data but specify 'is_test'.
    # Let's say it returns 'rf_prediction' for all rows, but 'is_test' boolean mask.
    assert "rf_prediction" in result_df.columns
    assert "is_test" in result_df.columns
    assert not result_df["is_test"].iloc[0]
    assert result_df["is_test"].iloc[-1]
    assert result_df["is_test"].sum() == 20

def test_train_and_predict_rf_feature_importances():
    from green_rock.domain.quant_model import train_and_predict_rf
    df = pd.DataFrame({
        "feature1": range(100),
        "feature2": range(100, 200),
        "target_regime": ["Low"] * 50 + ["High"] * 50
    })
    
    result_df, importances, _ = train_and_predict_rf(df, feature_cols=["feature1", "feature2"], target_col="target_regime", test_ratio=0.2)
    
    assert isinstance(importances, dict)
    assert set(importances.keys()) == {"feature1", "feature2"}
    assert sum(importances.values()) == pytest.approx(1.0)

def test_calculate_comparative_metrics_valid():
    df = pd.DataFrame({
        "is_test": [False, True, True, True, True],
        "baseline_regime": ["Low", "High", "High", "Low", "Medium"],
        "rf_prediction": [np.nan, "High", "Medium", "Low", "Low"]
    })
    
    metrics = calculate_comparative_metrics(df)
    
    assert metrics["baseline_latest"] == "Medium"
    assert metrics["rf_latest"] == "Low"
    assert metrics["total_test_days"] == 4
    # matches: High/High (True), High/Medium (False), Low/Low (True), Medium/Low (False)
    # 2 matches out of 4 -> 50.0%
    assert metrics["agreement_rate"] == 50.0
    assert metrics["divergence_count"] == 2

def test_calculate_comparative_metrics_no_test_data():
    df = pd.DataFrame({
        "is_test": [False, False],
        "baseline_regime": ["Low", "Low"],
        "rf_prediction": [np.nan, np.nan]
    })
    
    metrics = calculate_comparative_metrics(df)
    assert metrics == {}

def test_calculate_comparative_metrics_missing_columns():
    df = pd.DataFrame({
        "baseline_regime": ["Low", "Low"]
    })
    
    metrics = calculate_comparative_metrics(df)
    assert metrics == {}

def test_calculate_comparative_metrics_full_agreement():
    """Test that 100% agreement is correctly reported."""
    df = pd.DataFrame({
        "is_test": [False, True, True, True],
        "baseline_regime": ["Low", "High", "Medium", "Low"],
        "rf_prediction": [np.nan, "High", "Medium", "Low"]
    })
    
    metrics = calculate_comparative_metrics(df)
    
    assert metrics["agreement_rate"] == 100.0
    assert metrics["divergence_count"] == 0
    assert metrics["total_test_days"] == 3

def test_calculate_comparative_metrics_zero_agreement():
    """Test that 0% agreement (total divergence) is correctly reported."""
    df = pd.DataFrame({
        "is_test": [False, True, True, True],
        "baseline_regime": ["Low", "High", "Medium", "Low"],
        "rf_prediction": [np.nan, "Low", "High", "Medium"]
    })
    
    metrics = calculate_comparative_metrics(df)
    
    assert metrics["agreement_rate"] == 0.0
    assert metrics["divergence_count"] == 3
    assert metrics["total_test_days"] == 3

def test_calculate_daily_xai_attribution():
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from green_rock.domain.quant_model import calculate_daily_xai_attribution

    df = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "f2": [5.0, 4.0, 3.0, 2.0, 1.0],
    })
    y = ["Low", "Low", "High", "High", "High"]
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(df, y)
    
    # Take the last row
    row = df.iloc[[-1]]
    result = calculate_daily_xai_attribution(clf, row, ["f1", "f2"])
    
    assert "base_value" in result
    assert "predicted_class" in result
    assert "f1" in result
    assert "f2" in result
    
    # Calculate sum of base + contributions
    total_prob = result["base_value"] + result["f1"] + result["f2"]
    
    # Contributions are always relative to "High" risk class
    high_class_idx = np.where(clf.classes_ == "High")[0][0]
    expected_prob = clf.predict_proba(row)[0][high_class_idx]
    
    # Floating point precision match
    assert total_prob == pytest.approx(expected_prob)


def test_calculate_daily_xai_attribution_rejects_multi_row():
    """F-5: Verify single-row guard rejects multi-row input."""
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from green_rock.domain.quant_model import calculate_daily_xai_attribution

    df = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "f2": [5.0, 4.0, 3.0, 2.0, 1.0],
    })
    y = ["Low", "Low", "High", "High", "High"]
    clf = RandomForestClassifier(n_estimators=10, random_state=42)
    clf.fit(df, y)
    
    with pytest.raises(ValueError, match="single-row"):
        calculate_daily_xai_attribution(clf, df, ["f1", "f2"])



