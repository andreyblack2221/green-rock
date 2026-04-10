# Story 1.5: Narrative Shell & Interactive Timeline Presentation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an evaluator reviewing the UI,
I want to be guided horizontally through the data thesis while easily identifying risk regimes,
So that I can comprehend the baseline claims instantly before viewing the complex ML model.

## Acceptance Criteria

1. **Given** the Streamlit application is actively rendering
2. **When** the layout is drawn
3. **Then** it enforces a strict "Pitch Deck Scroll" vertical hierarchy separated by explicit `st.markdown("---")` chapter divider lines
4. **And** the textual narrative is securely encapsulated using `st.columns` to prevent visually endless text wrap on large screens
5. **Given** the baseline risk timeline is rendered on screen using `st.plotly_chart`
6. **When** the timeline is drawn over the price data
7. **Then** it dynamically takes up the full container width (`use_container_width=True`) and zeroes out unnecessary layout margins
8. **And** the background bands explicitly enforce strict UX-DR3 color coding (Forest Green for Low risk periods, Crimson for High risk, Amber for Warning) mapped natively to Plotly
9. **Given** the UI has loaded data
10. **When** the user looks at the top right of the dashboard
11. **Then** an injected Custom HTML State Badge prominently reflects the session status displaying either a green line for 'Live API Sync' or an amber line for 'Static Demo Mode' based entirely on `st.session_state`

## Dev Notes

### Dev Agent Guardrails & Technical Requirements
- Establish the "Pitch Deck Scroll" vertical layout for Streamlit.
- Do not create hidden tabs. Use sequential scrolling layout.
- The UI must utilize Streamlit's `layout="wide"`.
- Use specific color codes strictly: Forest Green `#388E3C` for Low risk, Crimson `#D32F2F` for High risk, Amber `#FBC02D` for Warning.
- Implement Plotly visualizations using `st.plotly_chart(fig, use_container_width=True)` in `src/green_rock/entrypoints/streamlit_app.py`.
- Ensure visualizations are generated entirely in `src/green_rock/entrypoints/visualizations.py` and returned as Plotly elements to `streamlit_app.py`.
- Custom HTML/CSS Pill for the state status should use `st.markdown(html, unsafe_allow_html=True)`. Read `st.session_state["data_source"]` which should be populated by `pipeline.py` or fallback orchestration.

### Architecture Compliance
- Keep purely visual plotting logic in `src/green_rock/entrypoints/visualizations.py`. It should return a Plotly `Figure` without calling `st.plotly_chart` itself.
- Application orchestration happens in `src/green_rock/entrypoints/streamlit_app.py`. It calls the visualizations and renders them linearly.
- Never place backend math or data extraction logic in entrypoints.
- Enforce the `snake_case` policy. Use `st.session_state["data_source"]` dictionary notation instead of attribute assignment.

### Library & Framework Requirements
- Streamlit
- Plotly `graph_objects` or `express` for the interactive timeline chart.
- Ensure the plot has minimal margins (`margin=dict(l=0, r=0, t=30, b=0)`).

### File Structure Requirements
- Modify/Create: `src/green_rock/entrypoints/streamlit_app.py`
- Modify/Create: `src/green_rock/entrypoints/visualizations.py`

### Testing Requirements
- E2E or Unit UI rendering test verification if Streamlit's AppTest API is available. Or verify component returns valid Plotly objects.

### Previous Story Intelligence
- `data_source` should be stored in `st.session_state["data_source"]` containing "LIVE" or "CACHED" values (from Epic 1's previous orchestrations).
- Dataframes produced by `pipeline.py` and `quant_model.py` contain `baseline_regime` column ("Low", "Medium", "High", or null for warmups) and `spy_close` for asset pricing.

### Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created.

## Tasks/Subtasks

- [x] Task 1: Implement `src/green_rock/entrypoints/visualizations.py` with Plotly logic for baseline risk timeline
- [x] Task 2: Modify `src/green_rock/entrypoints/streamlit_app.py` to add strict "Pitch Deck Scroll" vertical hierarchy
- [x] Task 3: Encapsulate textual narrative safely using `st.columns`
- [x] Task 4: Inject Custom HTML State Badge reflecting session status

### Review Findings

**Decision Needed:**
- [x] [Review][Decision] Badge placement — chose Option B: inject badge using `position:fixed` CSS at top of `main()`, before any column layout. Badge now persists during scroll. ✅ Fixed.

**Patch:**
- [x] [Review][Patch] `float: right` CSS unreliable in Streamlit — removed `float:right`; badge now uses `position:fixed` exclusively. [streamlit_app.py] ✅ Fixed.
- [x] [Review][Patch] `test_app.py` calls real `DataPipeline` without mocking — AppTest runs in isolated context; mocks cannot propagate. Test now uses `timeout=10` and `pytest.skip` guard when snapshot is absent. [tests/unit/test_app.py] ✅ Fixed.
- [x] [Review][Patch] vrect end-date off-by-one — `dates[end] + pd.Timedelta(days=1)` used as exclusive end boundary. [visualizations.py] ✅ Fixed.
- [x] [Review][Patch] Badge rendered with `"UNKNOWN"` on pipeline error — badge now only rendered when `data_source` is present in `session_state`. [streamlit_app.py] ✅ Fixed.
- [x] [Review][Patch] Single-row regime array produces zero-width vrect — single-row guard added; renders one direct vrect before exiting block-detection loop. [visualizations.py] ✅ Fixed.
- [x] [Review][Patch] `test_app.py` HTML pill assertion unreliable — replaced with dedicated `render_badge` unit tests that patch `st.markdown` directly; integration test checks `position: fixed` in markdown output. [tests/unit/test_app.py] ✅ Fixed.

**Deferred:**
- [x] [Review][Defer] `render_badge` defined at module scope rather than inside `main()` [streamlit_app.py:4-12] — deferred, pre-existing style; doesn't break functionality but reduces encapsulation
- [x] [Review][Defer] Silent empty chart when both `spy_close` and `baseline_regime` are absent [visualizations.py:14-56] — deferred, graceful degradation; a `st.warning` would improve UX but is not required by any AC

## Dev Agent Record

### Debug Log
- N/A

### Completion Notes
- All acceptance criteria satisfied.
- Baseline Plotly timeline chart implemented securely enforcing strict UX-DR3 color coding.
- Main Streamlit layout updated using `st.markdown("---")` for the Pitch Deck Scroll hierarchy, and `st.columns` used for text wrapping.
- Custom state badge added using HTML pill injected via unsafe HTML markdown, displaying LIVE or CACHED status natively derived from DataPipeline.
- Automated tests pass locally and dependencies on Streamlit / Plotly added appropriately.

## File List

- src/green_rock/entrypoints/visualizations.py
- src/green_rock/entrypoints/streamlit_app.py
- tests/unit/test_visualizations.py
- tests/unit/test_app.py
- requirements.txt

## Change Log

- Added visualizations entrypoint containing Plotly code.
- Main layout replaced entirely using Streamlit blocks for the "Narrative Shell" and plotting logic.
- Installed `plotly` as a required dependency.
- Fixed an import file mismatch error on existing tests by renaming duplicate test module `test_generate_snapshot.py` to `test_snapshot_gen.py`.
