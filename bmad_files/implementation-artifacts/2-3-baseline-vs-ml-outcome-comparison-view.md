# Story 2.3: Baseline vs. ML Outcome Comparison View

Status: done

## Story

As a dashboard viewer,
I want to observe the ML model's regime classifications explicitly juxtaposed against the simpler baseline moving-average,
so that I can visually and quickly verify the value added by injecting Machine Learning complexity.

## Acceptance Criteria

1. **Given** both the Baseline MA model and Random Forest model have finalized computations
   **When** the dashboard renders Act 2 of the narrative
   **Then** it explicitly displays a side-by-side or stacked visual comparison (e.g., dual metric cards or a comparative plot) of both model outputs across identical time periods
   **And** any numerical "deltas" correctly display improved accuracy or divergence using universal financial up/down indicator logic native to `st.metric`

## Tasks / Subtasks

- [x] Task 1: Update UI layout in `streamlit_app.py` for Act 2 to include comparative views. (AC: 1)
  - [x] Subtask 1.1: Fetch `result_df` from `service_layer` which should contain both baseline and RF predictions.
  - [x] Subtask 1.2: Design and implement dual `st.metric` cards or comparative visualizations.
  - [x] Subtask 1.3: Calculate and display numerical "deltas" for accuracy or divergence using native `st.metric` delta indicators.
- [x] Task 2: Implement any necessary helper visualization in `visualizations.py` if a comparative plot is chosen over just metrics. (AC: 1)
- [x] Task 3: Ensure UI gracefully degrades if data is missing, avoiding "All-Or-Nothing Dashboard Degradation". (AC: 1)
- [x] Task 4: Add or update tests to verify Act 2 comparative components render. (AC: 1)

## Dev Notes

### Technical Requirements
- **Data Integration**: Consume the `result_df` from `DataPipeline.run_pipeline` which contains the historical regime predictions from both the Baseline MA and the Random Forest model.
- **Metrics Calculation**: Compute the agreement/divergence or accuracy comparison between the two models over the test period.
- **UI Elements**: Use `st.columns` for side-by-side comparison of metrics. Use `st.metric` to display the "deltas" (e.g., +2% accuracy over baseline, or divergence in regimes).
- **Layout Constraints**: The narrative should be wrapped in `st.columns` to prevent wide text wrapping. Visualizations should use full container width.

### Architecture Compliance
- **Strict Decoupling**: Keep data manipulation and logic in pure Python modules (`domain/` or `service_layer/`). Do not add data processing logic into `streamlit_app.py` directly; instead, write helper functions in `service_layer` or `visualizations`.
- **Naming**: Use `snake_case` strictly for Python variables.
- **Theming**: Use the established Light Classic theme and the specific semantic colors: Forest Green (`#388E3C`), Crimson (`#D32F2F`), and Amber (`#FBC02D`).
- **Resilience**: Ensure `try/except` blocks or default fallbacks handle any missing columns or data gracefully.

### Library & Framework Requirements
- **Streamlit**: Use `st.metric` for KPIs and deltas. Use `st.columns` and `st.markdown("---")` for layout.
- **Plotly**: (If visualizing comparison) Use `use_container_width=True` and minimal margins.

### File Structure Requirements
- **Modify**: `src/green_rock/entrypoints/streamlit_app.py` (Dashboard integration).
- **Modify**: `src/green_rock/entrypoints/visualizations.py` (Chart/Metric generation if needed).
- **Modify**: `src/green_rock/service_layer/pipeline.py` (Only if new summary stats need to be propagated).
- **Modify**: `tests/` (Testing the new view/logic).

### Testing Requirements
- Test to ensure `streamlit_app.py` or new calculation functions run without tracebacks.

### Previous Story Intelligence
- **All-Or-Nothing Dashboard Degradation**: In Story 2.2, a bug was found where a failure in one model chart crashed the entire UI. Ensure the new comparison view is wrapped in appropriate robust error handling.
- **Data Leakage & Test Split Alignment**: Ensure that any comparative metrics calculation correctly aligns the test set indices between the baseline and RF models.
- **Data State**: Utilize `random_state=42` from Story 2.1 to keep outputs deterministic.

### Project Context Reference
- **FR20**: "User can view a model comparison showing baseline vs. Random Forest regime outputs side-by-side"
- **UX-DR1**: "Pitch Deck Scroll" vertical layout with 3 explicit visual phases ("Acts").
- **UX-DR6**: "Wrap qualitative textual narrative sequentially in `st.columns` constraint blocks while letting Visualizations occupy full container width."

### References
- [Source: bmad_files/planning-artifacts/prd.md#FR20]
- [Source: bmad_files/planning-artifacts/ux-design-specification.md#UX-DR6]
- [Source: bmad_files/planning-artifacts/epics.md#Story 2.3]

## Dev Agent Record

### Agent Model Used
Gemini 3.1 Pro (High)

### Debug Log References
Pending

### Completion Notes List
- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented `calculate_comparative_metrics` in `src/green_rock/domain/quant_model.py` and wrote failing tests first.
- Updated `src/green_rock/entrypoints/streamlit_app.py` to use dual `st.metric` cards to show Baseline and Random Forest outcomes.
- Evaluated divergence and handled ML outcome missing gracefully without crashing.
- Updated e2e and unit tests to verify metrics are rendered and missing outcomes degrade gracefully.

### File List
- src/green_rock/domain/quant_model.py
- src/green_rock/entrypoints/streamlit_app.py
- tests/unit/test_domain.py
- tests/unit/test_app.py
- tests/e2e/test_streamlit_feature_importance.py

### Review Findings
- [x] [Review][Patch] Missing `baseline_regime` column guard in `calculate_comparative_metrics` — `dropna(subset=["baseline_regime", ...])` raises KeyError if column absent; guard on L185 only checks `is_test` and `rf_prediction` [quant_model.py:185-188]
- [x] [Review][Patch] `st.metric` delta always positive — misleading indicator — `agreement_rate` is 0-100%, always positive, so `delta_color="normal"` makes arrow permanently green even at 30% agreement. Violates AC "universal financial up/down indicator logic" [streamlit_app.py:130-131]
- [x] [Review][Patch] Architecture violation: domain calls from entrypoint bypass service layer — `train_and_predict_rf` and `calculate_comparative_metrics` called directly in streamlit_app.py, violating Dev Notes "Do not add data processing logic into streamlit_app.py directly" [streamlit_app.py:60-67]
- [x] [Review][Patch] Partial state on `calculate_comparative_metrics` exception — if `train_and_predict_rf` succeeds (L62-66) but `calculate_comparative_metrics` throws (L67), `rf_importances` is already set; feature importance renders but toast says "Act 2 (ML) deferred" — misleading [streamlit_app.py:57-70]
- [x] [Review][Patch] `st.toast` for ML failure auto-dismisses — ephemeral toast for significant failure path; user may never notice ML pipeline failed [streamlit_app.py:70]
- [x] [Review][Patch] E2E tests don't validate comparative metrics rendering — mock return values lack `is_test`/`rf_prediction`/`baseline_regime` columns, so `calculate_comparative_metrics` always returns `{}` in E2E [test_streamlit_feature_importance.py:26-28]
- [x] [Review][Patch] No test for 100%/0% agreement boundary — only 50% agreement tested; missing edge-case coverage for perfect agreement and total divergence [test_domain.py]
- [x] [Review][Patch] `== True` boolean comparison style — `df[df["is_test"] == True]` should be idiomatic `df[df["is_test"]]` [quant_model.py:188]
