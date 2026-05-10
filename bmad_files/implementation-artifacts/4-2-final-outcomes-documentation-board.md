# Story 4.2: Final Outcomes Documentation Board

Status: done

## Story

As an evaluator finishing my review of the application,
I want to see a clear, un-styled, purely data-driven matrix comparing all strategies side-by-side,
So that I can quickly extract the final bottom-line numbers without hunting through complex tooltips.

## Acceptance Criteria

1. **Given** the `service_layer` has orchestrated all models and returned the final benchmarking statistics (e.g. Cumulative Return, Max Drawdown, etc.) for all four strategy variants (ML, Baseline, 60/40, SP500)
   **When** the UI renders the final chapter of the vertical scroll
   **Then** it displays a highly accessible, stark data matrix summarizing the outcomes

2. **Given** the final matrix is rendering
   **When** the user attempts to evaluate the data
   **Then** the matrix utilizes Streamlit's native `st.dataframe` component exactly per UX-DR8, ensuring high legibility and standard tabular contrasts without requiring custom CSS or dense chart interaction mapping

## Developer Context & Guardrails

### Technical Requirements
- **Data Rendering**: Extract the `strategy_returns` (5th element of `compute_ml_analysis` return tuple) and format it into a summary `pd.DataFrame`.
- **Layout**: This represents the final "Act" of the "Pitch Deck Scroll" vertical layout. Separate it from previous content using `st.markdown("---")`.
- **Component Use**: Render the final summary using `st.dataframe` with `use_container_width=True` (if applicable) for maximum legibility on both desktop and mobile. Do not use custom HTML or CSS here.

### Architecture Compliance
- **Hexagonal Integrity**: UI logic MUST remain within `src/green_rock/entrypoints/streamlit_app.py`. Do NOT add computation logic into the entrypoints file. Ensure `streamlit_app.py` simply maps the `strategy_returns` dictionary into a display-ready Pandas dataframe and renders it.
- **No Direct API Dependencies**: Ensure the `entrypoints` layer continues to only communicate with the `service_layer`.

### Library & Framework Requirements
- **Streamlit**: Use Streamlit 1.55+ natively.
- **Pandas**: Use pandas for reshaping the returns dictionary into the final presentation matrix.

### File Structure Requirements
- **Modify**: `src/green_rock/entrypoints/streamlit_app.py`
- **New Tests**: Add `tests/e2e/test_streamlit_outcomes_board.py` (or similar) to ensure the `st.dataframe` is rendered correctly in the UI. Ensure `at.dataframe` is found in the AppTest.

### Previous Story Intelligence
- **Return Tuple Size Issue**: In Story 4.1, the return tuple of `compute_ml_analysis` was updated to include the `strategy_returns` object as the 5th element. If you mock `compute_ml_analysis` in new E2E tests, ensure you return exactly 5 elements. 
- **Variable Unpacking**: `strategy_returns` should already be unpacked in `streamlit_app.py`. You just need to format and display it.

### Git Intelligence
- Recent commits introduced `calculate_strategy_returns` in `quant_model.py` and updated pipeline mocks. Be aware of `tests/e2e/test_streamlit_strategy_returns.py` which already tests if `strategy_returns` are passed to UI properly, you may want to append to it or create a new test.

### Project Context Reference
- **FR21**: User can view benchmark performance comparison across all strategies
- **UX-DR1**: Establish a "Pitch Deck Scroll" vertical layout with 3 explicit visual phases ("Acts") separated by `st.markdown("---")` dividers.
- **UX-DR8**: Standardize Benchmark performance layout exclusively using `st.dataframe` formatting to fulfill accessibility contrast expectations intuitively.

## Tasks / Subtasks

- [x] Locate `strategy_returns` in `streamlit_app.py` from the `compute_ml_analysis` call.
- [x] Implement the UI structure for the final chapter using `st.markdown("---")` and a subheader (e.g., `st.subheader("Final Benchmark Outcomes")`).
- [x] Format `strategy_returns` into a `pd.DataFrame` with clear labels (e.g., 'Baseline MA', 'Random Forest', '60/40 Portfolio', 'S&P 500').
- [x] Display the formatted DataFrame using `st.dataframe`.
- [x] Create or update E2E tests to verify the dataframe renders successfully without crashing.

## Dev Agent Record

### Agent Model Used
Gemini 3.1 Pro

### Debug Log References
- Addressed AppTest isolation issue where patching instance variables (`mock_instance.compute_ml_analysis`) failed to mock correctly in an E2E test. Fixed this by patching the method on the class directly before `AppTest` instantiation.

### Completion Notes List
- Validated that `strategy_returns` are formatted into a `pd.DataFrame` displaying Cumulative Return percentages side-by-side.
- Added graceful degradation fallback using `st.info` when `strategy_returns` is missing or the dictionary is empty.
- Implemented `tests/e2e/test_streamlit_outcomes_board.py` that fully verifies UI outcomes, AppTest execution, and graceful fallbacks.
- Corrected test mock issues in `test_streamlit_strategy_returns.py` to correctly test within Streamlit's `AppTest` context.
- Passed all 134 regression and integration tests successfully.
- [TEA Automation] Fixed assertion logic in `test_outcomes_board_renders_error_gracefully` to handle Streamlit 1.33+ emoji stripping behaviors.
- [TEA Automation] Added new E2E edge-case test (`test_outcomes_board_invalid_agreement_rate`) to verify error boundary degradation for malformed ML analysis stats.
- [TEA Automation] Validated deterministic execution of 142 total passing tests.

### File List
- modified: `src/green_rock/entrypoints/streamlit_app.py`
- added: `tests/e2e/test_streamlit_outcomes_board.py`
- modified: `tests/e2e/test_streamlit_strategy_returns.py`

### Change Log
- Added `pd.DataFrame` creation using `strategy_returns` data.
- Added `st.dataframe` rendering component at the bottom of the Streamlit app.
- Handled gracefully the empty `strategy_returns` case with `st.info`.
- Added end-to-end tests for both rendering the dataframe and fallback cases.

### Review Findings

- [x] [Review][Patch] Business Logic in Presentation Layer — Constructing pd.DataFrame inside Streamlit view introduces data transformation into presentation layer. Contradicts AC specifying it must be in streamlit_app.py vs hexagonal architecture.
- [x] [Review][Patch] Missing Benchmarking Statistics — AC 1 mandates multiple stats like "Max Drawdown, etc." but only Cumulative Return is displayed.
- [x] [Review][Patch] Hardcoded logic/configuration in UI [streamlit_app.py] — rf_features and strategy names are hardcoded in the presentation layer.
- [x] [Review][Patch] Unsafe defaulting of missing strategy returns to 0.0 [streamlit_app.py] — Using `.get(key, 0.0)` for missing returns misleadingly implies flat performance instead of missing data.
- [x] [Review][Patch] Missing type validation/Error Boundaries in calculations [streamlit_app.py] — `divergence_pct` and format math assume valid floats, risking TypeError crashes if upstream data is missing/None.
- [x] [Review][Patch] Broad exception swallowing and leakage [streamlit_app.py] — Catching bare Exception and rendering raw errors to UI exposes internal traces.
- [x] [Review][Patch] Superficial E2E Testing and Mocking [tests/e2e/test_streamlit_outcomes_board.py] — Tests patch internal methods heavily, lack error assertions, and omit coverage of the ml_analysis failure path.
- [x] [Review][Patch] Incomplete variable tracking [streamlit_app.py] — Truthiness checks on strategy_returns mask potentially malformed data.
- [x] [Review][Patch] Inconsistent Iconography [streamlit_app.py] — Mixed unicode escape sequences and emojis for UI warnings.
- [x] [Review][Patch] Misleading Comments [streamlit_app.py] — Comment implies only Act 2 degrades gracefully, but failure impacts Acts 3 and 4 as well.
- [x] [Review][Patch] Dangerous HTML Injection [streamlit_app.py] — `unsafe_allow_html=True` used for simple small tag styling.
- [x] [Review][Patch] Test Mock Divergence [tests/e2e/test_streamlit_outcomes_board.py] — Mock target_col default differs from production call signature.
- [x] [Review][Patch] Destructive Data Formatting [streamlit_app.py] — Formatting floats to string percentages before DataFrame creation disables st.dataframe numerical sorting.
- [x] [Review][Patch] Inconsistent Typography for Act 4 [streamlit_app.py] — Act 4 uses st.subheader instead of st.markdown "### Act 4:" consistent with other Acts.
- [x] [Review][Patch] Uncoordinated Error State UX [streamlit_app.py] — Disjointed warning and info banners if ML pipeline fails.
- [x] [Review][Defer] Layout Boilerplate Duplication [streamlit_app.py] — Duplicated `st.columns([0.7, 0.3])` layouts. — deferred, pre-existing
- [x] [Review][Defer] Brittle Tuple Unpacking [streamlit_app.py] — Assuming exactly 4 returns from pipeline run. — deferred, pre-existing
