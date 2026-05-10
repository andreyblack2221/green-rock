import streamlit as st
import pandas as pd
from green_rock.service_layer.pipeline import DataPipeline
from green_rock.entrypoints.visualizations import plot_baseline_timeline, plot_feature_importance, plot_xai_waterfall


def render_badge(status: str) -> None:
    """Inject a fixed-position status badge in the top-right corner of the viewport.

    Uses `position: fixed` CSS so the badge persists even when the user scrolls
    down the Pitch Deck layout.  The badge color follows UX-DR3:
      - Forest Green (#388E3C) for LIVE API sync
      - Amber (#FBC02D) for CACHED / Static Demo Mode
    """
    color = "#388E3C" if status == "LIVE" else "#FBC02D"
    badge_html = f"""
    <div style="
        position: fixed;
        top: 12px;
        right: 16px;
        z-index: 9999;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: {color};
        color: white;
        font-weight: bold;
        font-family: sans-serif;
        font-size: 0.8em;
        line-height: 1.5;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    ">
        DATA: {status}
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Green-Rock Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize data pipeline and fetch data
    pipeline = DataPipeline()
    try:
        df_regime, status, _, _ = pipeline.run_pipeline(
            compute_baseline=True,
            compute_rf=False
        )
        st.session_state["data_source"] = status
    except Exception:
        st.error("Failed to fetch data and compute baseline.")
        return

    rf_importances = None
    comparative_metrics = {}
    xai_attribution = None
    strategy_returns = pd.DataFrame()
    try:
        df_regime, rf_importances, comparative_metrics, xai_attribution, strategy_returns = pipeline.compute_ml_analysis(
            df_regime
        )
    except Exception:
        # Instead of failing the entire dashboard, let Acts 2, 3, and 4 degrade gracefully
        st.warning("⚠️ Machine Learning analysis could not be completed.")

    # Inject fixed-position state badge only when data loaded successfully.
    # data_source must be present in session_state — do not fall back to
    # "UNKNOWN" here, since that would misrepresent an error as a known state.
    data_source = st.session_state.get("data_source")
    if data_source is not None:
        render_badge(data_source)

    # Title
    st.title("Green-Rock Adaptive ETF Portfolio")

    st.markdown("---")

    # Narrative text column limit for easy reading
    text_col, _ = st.columns([0.7, 0.3])
    with text_col:
        st.markdown(
            "### Risk Regime Overview\n"
            "This section presents the baseline market risk classification. "
            "It establishes our core thesis for current market behavior, acting as the foundation "
            "before evaluating advanced ML models. The timeline uses standard MA crossover logic to determine Baseline risk."
        )

    st.markdown("---")

    # Visualization
    fig = plot_baseline_timeline(df_regime)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Act 2: ML Evaluation & Comparison
    text_col2, _ = st.columns([0.7, 0.3])
    with text_col2:
        st.markdown(
            "### Act 2: Machine Learning Evaluation\n"
            "This section explicitly juxtaposes the Random Forest model against the baseline, "
            "allowing for a quick evaluation of the value added by ML complexity."
        )

    if comparative_metrics:
        col_m1, col_m2, _ = st.columns([0.25, 0.25, 0.5])
        
        baseline_latest = comparative_metrics.get("baseline_latest", "N/A")
        rf_latest = comparative_metrics.get("rf_latest", "N/A")
        agreement_rate = comparative_metrics.get("agreement_rate", 0.0)
        divergence_count = comparative_metrics.get("divergence_count", 0)
        total_test_days = comparative_metrics.get("total_test_days", 0)
        
        with col_m1:
            st.metric(
                label="Baseline MA Regime", 
                value=baseline_latest
            )
            
        with col_m2:
            if agreement_rate is not None:
                try:
                    divergence_pct = 100.0 - float(agreement_rate)
                    delta_val = f"-{divergence_pct:.1f}% Divergence" if divergence_pct > 0 else "Fully Aligned"
                except (TypeError, ValueError):
                    delta_val = "N/A"
            else:
                delta_val = "N/A"
                
            st.metric(
                label="Random Forest Regime", 
                value=rf_latest,
                delta=delta_val,
                delta_color="normal"
            )
            
        st.caption(f"Out of {total_test_days} test days, the Random Forest diverged from the baseline **{divergence_count} times**.")
        st.markdown("---")

    text_col3, _ = st.columns([0.7, 0.3])
    with text_col3:
        st.markdown(
            "#### Feature Importance\n"
            "This chart reveals which quantitative inputs most heavily influenced the Random Forest's baseline regime classification."
        )

    if rf_importances:
        fig_importance = plot_feature_importance(rf_importances)
        st.plotly_chart(fig_importance, use_container_width=True)
    else:
        st.warning("Machine Learning outcomes could not be calculated.")

    st.markdown("---")

    # Act 3: The XAI Reveal
    text_col4, _ = st.columns([0.7, 0.3])
    with text_col4:
        st.markdown(
            "### Act 3: The XAI Reveal\n"
            "This Waterfall chart breaks down exactly which quantitative features shifted the model into today's risk regime. "
            "It establishes trust by ensuring the Random Forest is not acting as an unexplainable black box."
        )

    if xai_attribution:
        # We also need a try/except for resilience per AC
        try:
            fig_xai = plot_xai_waterfall(xai_attribution)
            st.plotly_chart(fig_xai, use_container_width=True)
        except Exception:
            st.warning("⚠️ XAI visualization could not be completed.")
    else:
        st.info("XAI attribution data is not available for today.")

    # Act 4: Final Benchmark Outcomes
    st.markdown("---")

    text_col5, _ = st.columns([0.7, 0.3])
    with text_col5:
        st.markdown("### Act 4: Final Benchmark Outcomes")
        st.markdown(
            "This section presents a clear, data-driven matrix comparing all strategies side-by-side, "
            "allowing for a quick evaluation of the final bottom-line numbers."
        )

    if strategy_returns is not None and not strategy_returns.empty:
        st.dataframe(
            strategy_returns, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Cumulative Return": st.column_config.NumberColumn(format="%.2f%%"),
                "Max Drawdown": st.column_config.NumberColumn(format="%.2f%%")
            }
        )
    else:
        st.info("Final outcomes data is not available.")


if __name__ == "__main__":
    main()
