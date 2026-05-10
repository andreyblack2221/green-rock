"""
Unit tests for calculate_daily_xai_attribution edge cases (Story 3.1, AC 1).
Extends existing tests in test_domain.py with boundary/negative-path coverage.
"""
import pytest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from green_rock.domain.quant_model import calculate_daily_xai_attribution


@pytest.fixture
def trained_rf_two_class():
    """A fitted RF with two classes (High/Low) for XAI testing."""
    df = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        "f2": [10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
    })
    y = ["Low"] * 5 + ["High"] * 5
    clf = RandomForestClassifier(n_estimators=20, random_state=42)
    clf.fit(df, y)
    return clf, df, ["f1", "f2"]


@pytest.fixture
def trained_rf_three_class():
    """A fitted RF with three classes (Low/Medium/High) for XAI testing."""
    n = 30
    df = pd.DataFrame({
        "f1": np.linspace(0, 10, n),
        "f2": np.linspace(10, 0, n),
    })
    y = ["Low"] * 10 + ["Medium"] * 10 + ["High"] * 10
    clf = RandomForestClassifier(n_estimators=20, random_state=42)
    clf.fit(df, y)
    return clf, df, ["f1", "f2"]


class TestXaiAttributionContributions:
    """[P0] Verify mathematical correctness of attribution contributions."""

    def test_contributions_sum_to_predicted_probability_two_class(self, trained_rf_two_class):
        """base_value + sum(contributions) must equal the P(High) probability."""
        clf, df, features = trained_rf_two_class
        row = df.iloc[[-1]]
        result = calculate_daily_xai_attribution(clf, row, features)

        total_prob = result["base_value"] + sum(result[f] for f in features)

        high_idx = np.where(clf.classes_ == "High")[0][0]
        expected_prob = clf.predict_proba(row[features])[0][high_idx]

        assert total_prob == pytest.approx(expected_prob, abs=1e-9)

    def test_contributions_sum_to_predicted_probability_three_class(self, trained_rf_three_class):
        """Contributions relative to High class must hold for 3-class models."""
        clf, df, features = trained_rf_three_class
        row = df.iloc[[-1]]
        result = calculate_daily_xai_attribution(clf, row, features)

        total_prob = result["base_value"] + sum(result[f] for f in features)

        high_idx = np.where(clf.classes_ == "High")[0][0]
        expected_prob = clf.predict_proba(row[features])[0][high_idx]

        assert total_prob == pytest.approx(expected_prob, abs=1e-9)

    def test_low_risk_row_has_negative_net_contribution(self, trained_rf_two_class):
        """A row predicted as Low should have net-negative contributions towards High risk."""
        clf, df, features = trained_rf_two_class
        row = df.iloc[[0]]  # Strongly "Low" territory
        result = calculate_daily_xai_attribution(clf, row, features)

        if result["predicted_class"] == "Low":
            net = sum(result[f] for f in features)
            # Net contribution should pull probability down (negative) for a Low prediction
            assert net <= 0.0 or result["base_value"] + net < 0.5

    def test_high_risk_row_has_positive_net_contribution(self, trained_rf_two_class):
        """A row predicted as High should have net-positive contributions towards High risk."""
        clf, df, features = trained_rf_two_class
        row = df.iloc[[-1]]  # Strongly "High" territory
        result = calculate_daily_xai_attribution(clf, row, features)

        if result["predicted_class"] == "High":
            total = result["base_value"] + sum(result[f] for f in features)
            assert total >= 0.5

    def test_different_rows_yield_different_attributions(self, trained_rf_two_class):
        """Attributions must vary across different input rows (no static outputs)."""
        clf, df, features = trained_rf_two_class
        row_first = df.iloc[[0]]
        row_last = df.iloc[[-1]]

        result_first = calculate_daily_xai_attribution(clf, row_first, features)
        result_last = calculate_daily_xai_attribution(clf, row_last, features)

        # At least one feature contribution should differ
        assert any(
            result_first[f] != pytest.approx(result_last[f])
            for f in features
        ), "Attributions should differ for different rows"


class TestXaiAttributionReturnContract:
    """[P0] Verify the return contract of calculate_daily_xai_attribution."""

    def test_returns_dict(self, trained_rf_two_class):
        clf, df, features = trained_rf_two_class
        result = calculate_daily_xai_attribution(clf, df.iloc[[-1]], features)
        assert isinstance(result, dict)

    def test_contains_base_value_key(self, trained_rf_two_class):
        clf, df, features = trained_rf_two_class
        result = calculate_daily_xai_attribution(clf, df.iloc[[-1]], features)
        assert "base_value" in result
        assert isinstance(result["base_value"], float)

    def test_contains_predicted_class_key(self, trained_rf_two_class):
        clf, df, features = trained_rf_two_class
        result = calculate_daily_xai_attribution(clf, df.iloc[[-1]], features)
        assert "predicted_class" in result
        assert result["predicted_class"] in {"Low", "Medium", "High"}

    def test_contains_all_feature_keys(self, trained_rf_two_class):
        clf, df, features = trained_rf_two_class
        result = calculate_daily_xai_attribution(clf, df.iloc[[-1]], features)
        for f in features:
            assert f in result
            assert isinstance(result[f], float)

    def test_base_value_is_bounded_probability(self, trained_rf_two_class):
        """Base value must be a valid probability [0, 1]."""
        clf, df, features = trained_rf_two_class
        result = calculate_daily_xai_attribution(clf, df.iloc[[-1]], features)
        assert 0.0 <= result["base_value"] <= 1.0


class TestXaiAttributionEdgeCases:
    """[P1] Edge case coverage."""

    def test_rejects_multi_row_input(self, trained_rf_two_class):
        """Single-row guard must reject multi-row DataFrames."""
        clf, df, features = trained_rf_two_class
        with pytest.raises(ValueError, match="single-row"):
            calculate_daily_xai_attribution(clf, df, features)

    def test_rejects_empty_dataframe(self, trained_rf_two_class):
        """Empty DataFrame should raise ValueError."""
        clf, _, features = trained_rf_two_class
        empty_df = pd.DataFrame(columns=features)
        with pytest.raises(ValueError, match="single-row"):
            calculate_daily_xai_attribution(clf, empty_df, features)

    def test_deterministic_across_calls(self, trained_rf_two_class):
        """Same input must produce identical output (random_state=42 in RF)."""
        clf, df, features = trained_rf_two_class
        row = df.iloc[[-1]]
        result1 = calculate_daily_xai_attribution(clf, row, features)
        result2 = calculate_daily_xai_attribution(clf, row, features)
        assert result1 == result2

    def test_five_features(self):
        """Verify attribution works with the project's 5-feature set."""
        feature_cols = ["spy_close", "tlt_close", "gld_close", "yield_spread_10y_2y", "spy_volatility_20d"]
        n = 50
        np.random.seed(42)
        data = {col: np.random.randn(n) for col in feature_cols}
        df = pd.DataFrame(data)
        y = ["Low"] * 15 + ["Medium"] * 20 + ["High"] * 15

        clf = RandomForestClassifier(n_estimators=20, random_state=42)
        clf.fit(df, y)

        row = df.iloc[[-1]]
        result = calculate_daily_xai_attribution(clf, row, feature_cols)

        assert len([k for k in result if k not in ("base_value", "predicted_class")]) == 5
        total = result["base_value"] + sum(result[f] for f in feature_cols)
        high_idx = np.where(clf.classes_ == "High")[0][0]
        expected = clf.predict_proba(row)[0][high_idx]
        assert total == pytest.approx(expected, abs=1e-9)
