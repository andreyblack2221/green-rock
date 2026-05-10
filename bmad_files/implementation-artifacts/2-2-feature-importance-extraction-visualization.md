# Story 2.2: Feature Importance Extraction & Visualization

## Story Foundation
**Story ID:** 2.2
**Story Key:** 2-2-feature-importance-extraction-visualization
**Epic:** Epic 2: Transparent ML Classification Engine
**Status:** done

**User Story:**
As an evaluator assessing the model's transparency,
I want to clearly see which quantitative inputs most heavily dictated the Random Forest model's overall learned behavior,
So that I can verify the model is weighing logical economic factors (like yield spreads) rather than noise.

**Acceptance Criteria:**
- **Given** the Random Forest model has completed training
  **When** the model artifacts are accessed
  **Then** it programmatically extracts the ordered mathematical feature importances (e.g., Rolling Volatility, Bond Price Momentum, etc.)
- **Given** the feature importance data is passed to the presentation layer
  **When** the UI renders the visualization
  **Then** it displays a Plotly horizontally-oriented Bar Chart
  **And** the chart dynamically conforms to the container width (`use_container_width=True`) with UX-DR7 minimal margins for mobile edge-to-edge readability

---

## Developer Context & Guardrails

### Technical Requirements
- **Extraction Logic**: Modify `train_and_predict_rf` in `src/green_rock/domain/quant_model.py` to return the feature importances (mapping feature names to their respective `feature_importances_` values).
- **Service Layer**: Update `DataPipeline.run_pipeline` in `src/green_rock/service_layer/pipeline.py` to return the feature importance data alongside the DataFrame.
- **Visualization Component**: Implement `plot_feature_importance(importances: dict[str, float])` in `src/green_rock/entrypoints/visualizations.py`.
- **Chart Style**:
    - Horizontal Bar Chart (`go.Bar(orientation='h')`).
    - Sorted by importance (descending).
    - Color: Use Slate Blue (`#1F3A5F`) for the bars.
    - Layout: Minimal margins `margin=dict(l=0, r=0, t=30, b=0)`.
- **UI Integration**: Update `src/green_rock/entrypoints/streamlit_app.py` to call the RF pipeline and display the importance chart in a new section (Act 2).

### Architecture Compliance
- **Decoupling**: Ensure `domain/` and `service_layer/` remain free of `import streamlit`.
- **Naming**: Use `snake_case` for all new variables and functions.
- **Complexity**: Keep functions simple (cyclomatic complexity < 10).

### Library & Framework Requirements
- **Plotly**: Use `plotly.graph_objects` for the bar chart.
- **Streamlit**: Use `st.plotly_chart(fig, use_container_width=True)`.

### File Structure Requirements
- **Modify**: `src/green_rock/domain/quant_model.py` (Feature extraction).
- **Modify**: `src/green_rock/service_layer/pipeline.py` (Orchestration).
- **Modify**: `src/green_rock/entrypoints/visualizations.py` (Chart generation).
- **Modify**: `src/green_rock/entrypoints/streamlit_app.py` (Dashboard integration).

### Testing Requirements
- **Unit Test**: Add a test in `tests/unit/test_domain.py` to verify that `train_and_predict_rf` correctly returns a non-empty dictionary of feature importances with expected keys.
- **Integration Test**: Update `tests/integration/test_adapters.py` or similar if needed to ensure the pipeline orchestration works with the new return type.

### Git Intelligence & Previous Learnings
- **Story 2.1 Success**: The deterministic Random Forest model is already implemented. Use its existing `random_state=42` to ensure consistent importance values across runs.
- **UX DR3/DR7**: Follow the specific margin and color tokens defined in the UX specification for institutional look-and-feel.

### Project Context Reference
- Adheres to FR19: "User can view a feature importance bar chart showing which inputs drive Random Forest classifications overall."

## Status Update
- **Completion Note**: Ultimate context engine analysis completed - comprehensive developer guide created. Status changed to ready-for-dev.

## Tasks/Subtasks
- [x] Task 1: Update `domain/quant_model.py` to return feature importances from `train_and_predict_rf`.
- [x] Task 2: Update `service_layer/pipeline.py` to propagate feature importances through `run_pipeline`.
- [x] Task 3: Implement `plot_feature_importance` in `entrypoints/visualizations.py`.
- [x] Task 4: Integrate the Feature Importance section into `entrypoints/streamlit_app.py` as "Act 2".
- [x] Task 5: Add unit tests for importance extraction in `tests/unit/test_domain.py`.

## Dev Agent Record
- **Implementation Plan:** Implemented feature importance extraction in the Random Forest model training process. Propagated this output through the service layer to the Streamlit UI, rendering it using a Plotly horizontal bar chart. Addressed a bug with duplicate index values during test prediction assignment.
- **Completion Notes:** All acceptance criteria are met, tests are passing, and code is ready for review.

## File List
- `src/green_rock/domain/quant_model.py`
- `src/green_rock/service_layer/pipeline.py`
- `src/green_rock/entrypoints/visualizations.py`
- `src/green_rock/entrypoints/streamlit_app.py`
- `tests/unit/test_domain.py`
- `tests/integration/test_pipeline_rf.py`

## Change Log
- Modified `train_and_predict_rf` to return `(result_df, importances)` tuple and assigned predictions using `.iloc` to avoid duplicate index issues.
- Updated `DataPipeline.run_pipeline` to propagate `rf_importances`.
- Added `plot_feature_importance` horizontal bar chart in `visualizations.py`.
- Added Act 2 section in `streamlit_app.py` to fetch and render the RF feature importances.
- Updated and added tests to verify the new feature importance output structure.

### Review Findings
- [x] [Review][Patch] All-Or-Nothing Dashboard Degradation [src/green_rock/entrypoints/streamlit_app.py:312]
- [x] [Review][Patch] Silent Bypass of Validation [src/green_rock/service_layer/pipeline.py:432]
- [x] [Review][Patch] Test Split Float-Rounding Edge Case [src/green_rock/domain/quant_model.py:254]
- [x] [Review][Patch] pd.Series(dtype="object") Assignment Masking [src/green_rock/domain/quant_model.py:247]
- [x] [Review][Patch] Pipeline Flag Dependency Trap [src/green_rock/service_layer/pipeline.py]
- [x] [Review][Patch] Implicit Temporal Order Assumption [src/green_rock/domain/quant_model.py]
- [x] [Review][Patch] Target Leakage via feature_cols [src/green_rock/domain/quant_model.py]
- [x] [Review][Patch] Extraction Logic does not intrinsically order the feature importances [src/green_rock/domain/quant_model.py]
- [x] [Review][Patch] Modification of out-of-scope files [.agent/skills/* and tests/e2e/test_streamlit_boot.py]
- [x] [Review][Defer] Perfect Overlap / Zero Variance Edge Case [src/green_rock/entrypoints/visualizations.py] — deferred, pre-existing
- [x] [Review][Defer] Hardcoded Feature Brittleness [src/green_rock/entrypoints/streamlit_app.py:311] — deferred, pre-existing
