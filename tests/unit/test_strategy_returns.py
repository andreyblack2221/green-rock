"""
Unit tests for calculate_strategy_returns (Story 4.1: Financial Allocation & Benchmarking Engine).

Tests cover:
  - AC1: Allocation weight mapping correctness per regime
  - AC1: Cumulative return formula (prod(1+r)-1)
  - AC1: Max drawdown calculation
  - AC2: 60/40 and S&P 500 benchmark correctness
  - Edge cases: NaN regimes, NaN returns, single-day, uniform regimes, unmapped strings
"""
import pytest
import numpy as np
import pandas as pd
from green_rock.domain.quant_model import calculate_strategy_returns


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(
    spy_prices,
    tlt_prices,
    gld_prices,
    baseline_regimes,
    rf_predictions,
    is_test_flags,
):
    """Build a minimal DataFrame for calculate_strategy_returns."""
    return pd.DataFrame({
        "spy_close": spy_prices,
        "tlt_close": tlt_prices,
        "gld_close": gld_prices,
        "baseline_regime": baseline_regimes,
        "rf_prediction": rf_predictions,
        "is_test": is_test_flags,
    })


ALL_EXPECTED_KEYS = {
    "baseline_cumulative", "rf_cumulative", "benchmark_60_40", "benchmark_spy",
    "baseline_max_drawdown", "rf_max_drawdown",
    "benchmark_60_40_max_drawdown", "benchmark_spy_max_drawdown",
}


# ---------------------------------------------------------------------------
# P0 — Weight Mapping Correctness (G1)
# ---------------------------------------------------------------------------

class TestWeightMappingCorrectness:
    """[P0] Verify regime-to-weight mapping produces numerically correct daily returns."""

    def test_low_risk_regime_weights(self):
        """U1: Low Risk → 70% SPY, 20% TLT, 10% GLD."""
        # Two days: day 0 train, day 1 test.
        # SPY: 100→102 (2%), TLT: 100→101 (1%), GLD: 100→103 (3%)
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["Low", "Low"],
            rf_predictions=[np.nan, "Low"],
            is_test_flags=[False, True],
        )

        result = calculate_strategy_returns(df)

        # Expected portfolio return for Low: 0.70*0.02 + 0.20*0.01 + 0.10*0.03 = 0.019
        expected_baseline = 0.70 * 0.02 + 0.20 * 0.01 + 0.10 * 0.03
        assert result["baseline_cumulative"] == pytest.approx(expected_baseline, abs=1e-9)

        # RF is also "Low" → same weights
        assert result["rf_cumulative"] == pytest.approx(expected_baseline, abs=1e-9)

    def test_high_risk_regime_weights(self):
        """U2: High Risk → 20% SPY, 50% TLT, 30% GLD."""
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["High", "High"],
            rf_predictions=[np.nan, "High"],
            is_test_flags=[False, True],
        )

        result = calculate_strategy_returns(df)

        expected = 0.20 * 0.02 + 0.50 * 0.01 + 0.30 * 0.03
        assert result["baseline_cumulative"] == pytest.approx(expected, abs=1e-9)
        assert result["rf_cumulative"] == pytest.approx(expected, abs=1e-9)

    def test_medium_risk_regime_weights(self):
        """Medium Risk → 40% SPY, 40% TLT, 20% GLD."""
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["Medium", "Medium"],
            rf_predictions=[np.nan, "Medium"],
            is_test_flags=[False, True],
        )

        result = calculate_strategy_returns(df)

        expected = 0.40 * 0.02 + 0.40 * 0.01 + 0.20 * 0.03
        assert result["baseline_cumulative"] == pytest.approx(expected, abs=1e-9)


# ---------------------------------------------------------------------------
# P0 — Benchmark Correctness (G6, G7)
# ---------------------------------------------------------------------------

class TestBenchmarkCorrectness:
    """[P0] Verify static benchmark strategies compute correct returns."""

    def test_60_40_benchmark(self):
        """U3: 60/40 benchmark = 60% SPY + 40% TLT, 0% GLD."""
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["Low", "Low"],
            rf_predictions=[np.nan, "Low"],
            is_test_flags=[False, True],
        )

        result = calculate_strategy_returns(df)

        expected_60_40 = 0.60 * 0.02 + 0.40 * 0.01
        assert result["benchmark_60_40"] == pytest.approx(expected_60_40, abs=1e-9)

    def test_spy_buy_and_hold_benchmark(self):
        """U4: S&P 500 benchmark = 100% SPY."""
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["Low", "Low"],
            rf_predictions=[np.nan, "Low"],
            is_test_flags=[False, True],
        )

        result = calculate_strategy_returns(df)

        assert result["benchmark_spy"] == pytest.approx(0.02, abs=1e-9)


# ---------------------------------------------------------------------------
# P0 — Cumulative Return Formula (G1)
# ---------------------------------------------------------------------------

class TestCumulativeReturnFormula:
    """[P0] Verify cumulative return = prod(1+daily_return) - 1."""

    def test_multi_day_cumulative_return(self):
        """U10: 3 test days with known returns verify compounding."""
        # SPY: 100→102→101→103  → daily returns: +2%, -0.98%, +1.98%
        # TLT: 100→100→101→100  → daily returns: 0%, +1%, -0.99%
        # GLD: 100→102→100→101  → daily returns: +2%, -1.96%, +1%
        df = _make_df(
            spy_prices=[100.0, 102.0, 101.0, 103.0],
            tlt_prices=[100.0, 100.0, 101.0, 100.0],
            gld_prices=[100.0, 102.0, 100.0, 101.0],
            baseline_regimes=["Low", "Low", "Low", "Low"],
            rf_predictions=[np.nan, "Low", "Low", "Low"],
            is_test_flags=[False, True, True, True],
        )

        result = calculate_strategy_returns(df)

        # Compute expected manually for Low: 70% SPY, 20% TLT, 10% GLD
        spy_rets = np.array([0.02, -1 / 102, 2 / 101])
        tlt_rets = np.array([0.0, 0.01, -1 / 101])
        gld_rets = np.array([0.02, -2 / 102, 0.01])

        daily_port = 0.70 * spy_rets + 0.20 * tlt_rets + 0.10 * gld_rets
        expected = np.prod(1 + daily_port) - 1

        assert result["baseline_cumulative"] == pytest.approx(expected, rel=1e-6)

        # SPY benchmark: cumulative of raw SPY daily returns
        expected_spy = np.prod(1 + spy_rets) - 1
        assert result["benchmark_spy"] == pytest.approx(expected_spy, rel=1e-6)


# ---------------------------------------------------------------------------
# P0 — Return Dict Contains All Expected Keys
# ---------------------------------------------------------------------------

class TestReturnDictStructure:
    """[P0] Verify the returned dict has all 8 expected keys."""

    def test_return_dict_has_all_keys(self):
        """All 8 keys (4 cumulative + 4 max_drawdown) must be present."""
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["Low", "Low"],
            rf_predictions=[np.nan, "Low"],
            is_test_flags=[False, True],
        )

        result = calculate_strategy_returns(df)

        assert set(result.keys()) == ALL_EXPECTED_KEYS

    def test_all_values_are_floats(self):
        """Every value in the returned dict must be a Python float."""
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["Low", "Low"],
            rf_predictions=[np.nan, "Low"],
            is_test_flags=[False, True],
        )

        result = calculate_strategy_returns(df)

        for key, val in result.items():
            assert isinstance(val, float), f"result['{key}'] is {type(val)}, expected float"


# ---------------------------------------------------------------------------
# P0 — Max Drawdown Correctness
# ---------------------------------------------------------------------------

class TestMaxDrawdown:
    """[P0] Verify max drawdown calculation."""

    def test_max_drawdown_is_non_negative(self):
        """Drawdown should always be >= 0."""
        df = _make_df(
            spy_prices=[100.0, 102.0, 101.0, 103.0],
            tlt_prices=[100.0, 100.0, 101.0, 100.0],
            gld_prices=[100.0, 102.0, 100.0, 101.0],
            baseline_regimes=["Low", "Low", "Low", "Low"],
            rf_predictions=[np.nan, "Low", "Low", "Low"],
            is_test_flags=[False, True, True, True],
        )

        result = calculate_strategy_returns(df)

        assert result["baseline_max_drawdown"] >= 0.0
        assert result["rf_max_drawdown"] >= 0.0
        assert result["benchmark_60_40_max_drawdown"] >= 0.0
        assert result["benchmark_spy_max_drawdown"] >= 0.0

    def test_max_drawdown_zero_for_monotonic_increase(self):
        """If portfolio only goes up, max drawdown should be 0."""
        # All assets increase monotonically → no drawdown
        df = _make_df(
            spy_prices=[100.0, 101.0, 102.0, 103.0],
            tlt_prices=[100.0, 101.0, 102.0, 103.0],
            gld_prices=[100.0, 101.0, 102.0, 103.0],
            baseline_regimes=["Low", "Low", "Low", "Low"],
            rf_predictions=[np.nan, "Low", "Low", "Low"],
            is_test_flags=[False, True, True, True],
        )

        result = calculate_strategy_returns(df)

        assert result["benchmark_spy_max_drawdown"] == pytest.approx(0.0, abs=1e-9)

    def test_max_drawdown_positive_for_drop(self):
        """If portfolio drops from peak, max drawdown should be > 0."""
        # SPY: 100→110→105→108 → drops from 110 to 105 → drawdown present
        df = _make_df(
            spy_prices=[100.0, 110.0, 105.0, 108.0],
            tlt_prices=[100.0, 100.0, 100.0, 100.0],
            gld_prices=[100.0, 100.0, 100.0, 100.0],
            baseline_regimes=["Low", "Low", "Low", "Low"],
            rf_predictions=[np.nan, "Low", "Low", "Low"],
            is_test_flags=[False, True, True, True],
        )

        result = calculate_strategy_returns(df)

        assert result["benchmark_spy_max_drawdown"] > 0.0


# ---------------------------------------------------------------------------
# P1 — Edge Cases (G2, G3, G5, G8)
# ---------------------------------------------------------------------------

class TestStrategyReturnsEdgeCases:
    """[P1] Edge case coverage for calculate_strategy_returns."""

    def test_nan_regime_defaults_to_medium(self):
        """U5: NaN in baseline_regime or rf_prediction falls back to Medium weights."""
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["Low", np.nan],
            rf_predictions=[np.nan, np.nan],
            is_test_flags=[False, True],
        )

        result = calculate_strategy_returns(df)

        # NaN should be filled with "Medium" → 40/40/20
        expected_medium = 0.40 * 0.02 + 0.40 * 0.01 + 0.20 * 0.03
        assert result["baseline_cumulative"] == pytest.approx(expected_medium, abs=1e-9)
        assert result["rf_cumulative"] == pytest.approx(expected_medium, abs=1e-9)

    def test_nan_asset_returns_treated_as_zero(self):
        """U6: If asset returns are NaN (e.g. first pct_change row), they are treated as 0."""
        df = pd.DataFrame({
            "spy_close": [100.0],
            "tlt_close": [100.0],
            "gld_close": [100.0],
            "baseline_regime": ["Low"],
            "rf_prediction": ["Low"],
            "is_test": [True],
        })

        result = calculate_strategy_returns(df)

        # pct_change on a single row = NaN → nan_to_num → 0
        # Cumulative = prod(1+0) - 1 = 0.0
        assert result["baseline_cumulative"] == pytest.approx(0.0, abs=1e-9)
        assert result["benchmark_spy"] == pytest.approx(0.0, abs=1e-9)

    def test_uniform_regime_all_low(self):
        """U8: All test days with same regime apply consistent weights."""
        df = _make_df(
            spy_prices=[100.0, 101.0, 102.0, 103.0],
            tlt_prices=[100.0, 100.5, 101.0, 101.5],
            gld_prices=[100.0, 100.2, 100.4, 100.6],
            baseline_regimes=["Low", "Low", "Low", "Low"],
            rf_predictions=[np.nan, "Low", "Low", "Low"],
            is_test_flags=[False, True, True, True],
        )

        result = calculate_strategy_returns(df)

        # All values should be floats and all 8 keys present
        assert set(result.keys()) == ALL_EXPECTED_KEYS
        for val in result.values():
            assert isinstance(val, float)

    def test_unmapped_regime_string_raises(self):
        """U9: A regime string not in the weights_map (e.g. 'Unknown') raises KeyError."""
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["Low", "Unknown"],
            rf_predictions=[np.nan, "Low"],
            is_test_flags=[False, True],
        )

        with pytest.raises(KeyError):
            calculate_strategy_returns(df)


# ---------------------------------------------------------------------------
# P2 — Single-Day Test Period (G4)
# ---------------------------------------------------------------------------

class TestSingleDayTestPeriod:
    """[P2] Verify function handles a single-day test period."""

    def test_single_day_returns_valid_dict(self):
        """U7: Single test day produces a dict with all 8 keys."""
        df = _make_df(
            spy_prices=[100.0, 102.0],
            tlt_prices=[100.0, 101.0],
            gld_prices=[100.0, 103.0],
            baseline_regimes=["Low", "Medium"],
            rf_predictions=[np.nan, "High"],
            is_test_flags=[False, True],
        )

        result = calculate_strategy_returns(df)

        assert set(result.keys()) == ALL_EXPECTED_KEYS
        for val in result.values():
            assert isinstance(val, float)
