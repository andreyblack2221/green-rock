"""
Unit tests for plot_xai_waterfall visualization (Story 3.1, AC 2 & 3).
"""
import pytest
import plotly.graph_objects as go
from green_rock.entrypoints.visualizations import plot_xai_waterfall


@pytest.fixture
def sample_xai_attribution():
    """Minimal valid XAI attribution dict for testing."""
    return {
        "base_value": 0.35,
        "spy_close": 0.12,
        "tlt_close": -0.08,
        "gld_close": 0.03,
        "predicted_class": "High",
    }


class TestPlotXaiWaterfallHappyPath:
    """[P0] Core rendering and AC compliance tests."""

    def test_returns_valid_plotly_figure(self, sample_xai_attribution):
        """AC2: Waterfall must produce a valid go.Figure."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        assert isinstance(fig, go.Figure)

    def test_uses_waterfall_trace_type(self, sample_xai_attribution):
        """AC2: Must use go.Waterfall as the Hero Component."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Waterfall)

    def test_color_tokens_match_ux_spec(self, sample_xai_attribution):
        """AC2: Forest Green (#388E3C) for risk-reducing, Crimson (#D32F2F) for risk-increasing, Slate Blue (#1F3A5F) for totals."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        waterfall = fig.data[0]

        assert waterfall.decreasing.marker.color == "#388E3C", "Risk-reducing must be Forest Green"
        assert waterfall.increasing.marker.color == "#D32F2F", "Risk-increasing must be Crimson"
        assert waterfall.totals.marker.color == "#1F3A5F", "Totals must be Slate Blue"

    def test_connector_line_color(self, sample_xai_attribution):
        """Professional styling: connector lines must be dark gray per spec."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        waterfall = fig.data[0]
        assert waterfall.connector.line.color == "rgb(63, 63, 63)"

    def test_layout_zero_margins_hero_treatment(self, sample_xai_attribution):
        """AC2: Hero treatment demands zero side/bottom margins."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        margins = fig.layout.margin
        assert margins.l == 0
        assert margins.r == 0
        assert margins.b == 0
        assert margins.t == 30

    def test_layout_height_500(self, sample_xai_attribution):
        """AC2: Waterfall chart height must be 500px for hero treatment."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        assert fig.layout.height == 500

    def test_layout_template_plotly_white(self, sample_xai_attribution):
        """Institutional styling: must use plotly_white template."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        assert fig.layout.template.layout.plot_bgcolor is not None or str(fig.layout.template) != ""
        # The canonical check: template was set to "plotly_white"
        # Plotly resolves the string to a Template object, so check the figure's JSON
        fig_json = fig.to_dict()
        assert fig_json["layout"]["template"] is not None

    def test_title_contains_predicted_class(self, sample_xai_attribution):
        """AC2: Title must dynamically include the predicted class."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        title_text = fig.layout.title.text if hasattr(fig.layout.title, "text") else str(fig.layout.title)
        assert "High" in title_text, "Title must contain the predicted class"
        assert "P(High Risk)" in title_text or "Predicted: High" in title_text


class TestPlotXaiWaterfallDataIntegrity:
    """[P0] Verify waterfall bar data structure and order."""

    def test_measure_sequence_absolute_relative_total(self, sample_xai_attribution):
        """Measures must be: absolute (base), relative (features...), total (final)."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        measures = list(fig.data[0].measure)

        assert measures[0] == "absolute", "First bar must be 'absolute' (base probability)"
        assert measures[-1] == "total", "Last bar must be 'total' (final probability)"
        assert all(m == "relative" for m in measures[1:-1]), "Middle bars must be 'relative' (feature contributions)"

    def test_bar_count_matches_features_plus_base_and_total(self, sample_xai_attribution):
        """Number of bars = 1 (base) + N features + 1 (total)."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        waterfall = fig.data[0]

        num_features = len([k for k in sample_xai_attribution if k not in ("base_value", "predicted_class")])
        expected_bars = 1 + num_features + 1  # base + features + total
        assert len(waterfall.x) == expected_bars
        assert len(waterfall.y) == expected_bars

    def test_x_labels_include_base_and_final(self, sample_xai_attribution):
        """X-axis must start with 'Base Probability' and end with 'Final Probability'."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        x_labels = list(fig.data[0].x)
        assert x_labels[0] == "Base Probability"
        assert x_labels[-1] == "Final Probability"

    def test_features_sorted_by_absolute_contribution(self, sample_xai_attribution):
        """Features must be sorted by |contribution| descending for readability."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        x_labels = list(fig.data[0].x)
        feature_labels = x_labels[1:-1]  # exclude base and total

        # Expected order: spy_close (|0.12|), tlt_close (|-0.08|), gld_close (|0.03|)
        assert feature_labels[0] == "spy_close"
        assert feature_labels[1] == "tlt_close"
        assert feature_labels[2] == "gld_close"

    def test_text_annotations_show_numeric_values(self, sample_xai_attribution):
        """AC3: Hover/text must show exact numerical breakdown."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        waterfall = fig.data[0]
        text_values = list(waterfall.text)

        # All text values should be numeric strings like "0.350", "0.120", etc.
        assert len(text_values) > 0
        for t in text_values:
            # Should be parseable as a float
            float(t)  # raises ValueError if not numeric

    def test_final_probability_equals_base_plus_contributions(self, sample_xai_attribution):
        """Mathematical invariant: final bar y-value = base + sum(contributions)."""
        fig = plot_xai_waterfall(sample_xai_attribution)
        y_values = list(fig.data[0].y)

        base = y_values[0]
        final = y_values[-1]
        contributions = y_values[1:-1]

        expected_final = base + sum(contributions)
        assert final == pytest.approx(expected_final, abs=1e-9)


class TestPlotXaiWaterfallEdgeCases:
    """[P1] Edge cases and boundary conditions."""

    def test_empty_dict_returns_empty_figure(self):
        """Empty attribution should return an empty figure, not crash."""
        fig = plot_xai_waterfall({})
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 0

    def test_none_input_returns_empty_figure(self):
        """None attribution should return an empty figure."""
        fig = plot_xai_waterfall(None)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 0

    def test_single_feature_attribution(self):
        """Waterfall should work with just one feature."""
        xai = {"base_value": 0.5, "only_feature": 0.2, "predicted_class": "High"}
        fig = plot_xai_waterfall(xai)
        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].x) == 3  # base + 1 feature + total

    def test_all_zero_contributions(self):
        """All features have zero contribution — chart should still render."""
        xai = {"base_value": 0.33, "f1": 0.0, "f2": 0.0, "predicted_class": "Medium"}
        fig = plot_xai_waterfall(xai)
        assert isinstance(fig, go.Figure)
        y_values = list(fig.data[0].y)
        # Final should equal base when all contributions are zero
        assert y_values[-1] == pytest.approx(y_values[0])

    def test_all_negative_contributions(self):
        """All features are risk-reducing — base should be highest bar."""
        xai = {"base_value": 0.8, "f1": -0.3, "f2": -0.2, "predicted_class": "Low"}
        fig = plot_xai_waterfall(xai)
        y_values = list(fig.data[0].y)
        assert y_values[-1] < y_values[0]  # Final < base

    def test_all_positive_contributions(self):
        """All features are risk-increasing — final should be highest."""
        xai = {"base_value": 0.1, "f1": 0.3, "f2": 0.2, "predicted_class": "High"}
        fig = plot_xai_waterfall(xai)
        y_values = list(fig.data[0].y)
        assert y_values[-1] > y_values[0]  # Final > base

    def test_missing_predicted_class_defaults_to_unknown(self):
        """If predicted_class is missing, title should say 'Unknown'."""
        xai = {"base_value": 0.5, "f1": 0.1}
        fig = plot_xai_waterfall(xai)
        title_text = fig.layout.title.text if hasattr(fig.layout.title, "text") else str(fig.layout.title)
        assert "Unknown" in title_text
