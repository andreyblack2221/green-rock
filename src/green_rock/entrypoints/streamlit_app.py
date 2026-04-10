import streamlit as st
from green_rock.service_layer.pipeline import DataPipeline
from green_rock.domain.quant_model import calculate_baseline_regime
from green_rock.entrypoints.visualizations import plot_baseline_timeline


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
        df, status = pipeline.get_data()
        st.session_state["data_source"] = status
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return

    # Inject fixed-position state badge only when data loaded successfully.
    # data_source must be present in session_state — do not fall back to
    # "UNKNOWN" here, since that would misrepresent an error as a known state.
    data_source = st.session_state.get("data_source")
    if data_source is not None:
        render_badge(data_source)

    # Process data
    try:
        df_regime = calculate_baseline_regime(df)
    except Exception as e:
        st.error(f"Failed to calculate baseline regime: {e}")
        return

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


if __name__ == "__main__":
    main()
