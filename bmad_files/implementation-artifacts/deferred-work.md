## Deferred from: code review (1-1-initial-application-scaffolding-visual-theming.md)
- Non-deterministic dependencies: requirements.txt uses `>=` instead of lockfile. (Pre-existing/MVP scaffolding scope).
- Absence of static analysis tooling: No ruff/black/mypy. (Pre-existing/MVP scaffolding scope).

## Deferred from: code review of 1-2-offline-data-snapshot-generator (2026-04-07)
- Price tickers concatenated without outer-join between them — `pd.concat(dfs, axis=1)` silently misaligns if tickers have different trading day coverage. Consider switching to `yf.download()` for batch fetch. [scripts/generate_snapshot.py:22]
- Hardcoded `start_date = "2010-01-01"` with no CLI arguments — no way to regenerate a shorter snapshot without editing source. Out of scope for this story; could be a future enhancement.
- `.normalize()` assumes daily data granularity — brittle if yfinance upstream ever returns intraday timestamps. Acceptable risk for current use case.

## Deferred from: code review of 1-3-resilient-data-fetcher (2026-04-07)
- F-7: `FileRepository` path resolution via `__file__` depth navigation (3× `os.path.dirname`) is fragile for installed packages (e.g., `pip install -e .` with different depth). Consider `importlib.resources` or env-var-based override. [file_repository.py:12-14]
- F-9: `test_file_repository` patches `pandas.read_csv` globally rather than `green_rock.adapters.file_repository.pd.read_csv`. Works but less isolated; standard practice is to patch at the point of use. [tests/unit/test_file_repository.py:8]
- F-12: `read_snapshot` does not validate that expected columns (`spy_close`, `tlt_close`, etc.) exist after loading the CSV. A schema change in `static_snapshot.csv` would silently produce a DF with wrong columns. [file_repository.py:16-27]
- F-15: `ffill(limit=5)` + trailing `dropna()` silently trims rows that couldn't be forward-filled with no log warning. If large gaps exist at the beginning of the date range, the effective start date shifts silently. [data_fetcher.py:74]

## Deferred from: code review of 1-4-baseline-ma-crossover-classifier (2026-04-09)
- DataFrame shorter than `long_window` returns all `None` / `np.nan` values in `baseline_regime` with no exception raised — silently empty classification output with no caller warning. [quant_model.py]
- No index-sorting requirement documented — an unsorted or duplicate DatetimeIndex passed to `rolling().mean()` would produce incorrect window calculations with no error. Consider validating or documenting this precondition. [quant_model.py]

## Deferred from: code review of 1-5-narrative-shell-interactive-timeline-presentation (2026-04-09)
- `render_badge` defined at module scope rather than inside `main()` — doesn't break functionality but reduces encapsulation and testability. [streamlit_app.py:4-12]
- Silent empty chart produced when both `spy_close` and `baseline_regime` columns are absent from the DataFrame — graceful degradation but no user-facing warning or error. Adding `st.warning()` would improve UX. [visualizations.py:14-56]

## Deferred from: code review of 2-1-random-forest-classifier-pipeline (2026-04-26)
- Single regime class in training data is not gracefully handled. If `y_train` contains only one unique risk regime class, `RandomForestClassifier` might fail or perform trivially. [src/green_rock/domain/quant_model.py]

## Deferred from: code review of 2-2-feature-importance-extraction-visualization.md (2026-05-02)
- Perfect Overlap / Zero Variance Edge Case: Plotly renders empty X-axis if importances are exactly 0.0 with no warning. [src/green_rock/entrypoints/visualizations.py]
- Hardcoded Feature Brittleness: Tying UI rendering strictly to expected ML transformations. [src/green_rock/entrypoints/streamlit_app.py:311]

## Deferred from: code review of 3-1-daily-xai-risk-waterfall-visualization (2026-05-02)
- F-3: `run_pipeline` always returns `None` for XAI position (4th tuple element). The `compute_rf` branch trains a classifier but never calls `calculate_daily_xai_attribution`. XAI data is only available through `compute_ml_analysis`, making the 4th return position misleading. Pre-existing structural choice from Story 2.x. [pipeline.py:73]
- F-7: E2E boot test patches `green_rock.domain.quant_model.train_and_predict_rf` but `streamlit_app.py` calls `pipeline.compute_ml_analysis()` instead. The mock intercepts at the domain import within pipeline.py which still works, but the target doesn't reflect the actual call chain and is fragile. [test_streamlit_boot.py:12]

## Deferred from: code review of 4-1-financial-allocation-benchmarking-engine.md (2026-05-08)
- Redundant Model Training in `pipeline.py`: run_pipeline trains RF, and compute_ml_analysis trains identical model. Calling sequentially trains twice. (Pre-existing)
- Silent Semantic Shifting in XAI `quant_model.py`: If class not seen, falls back. Pre-existing XAI logic.
- O(N) Lookup Inside a Tight Loop in XAI `quant_model.py`: Inefficient lookup. Pre-existing.
- Flawed Benchmark Math (Implicit Daily Rebalancing) `quant_model.py`: Computes 60/40 applying `[0.60, 0.40]` to daily returns, mathematically assumes daily rebalancing.
- Naive Time-Series Slicing `quant_model.py`: split index by simple subtraction. Pre-existing.
- Lazy Test Imports in `test_app.py`: hides imports inside test method. Pre-existing.
- Misleading Waterfall Readability `visualizations.py`: relative contributions format. Pre-existing (Story 3.1).
- Sweeping Warnings Under the Rug in `pyproject.toml`: globally ignores `NotOpenSSLWarning`. Pre-existing.
- Incomplete Type Hitting for `main()` `streamlit_app.py`: missing type hint. Pre-existing.
- XAI calculate_daily_xai_attribution NaNs in features `quant_model.py`: NaNs in features -> ValueError. Pre-existing.
- XAI calculate_daily_xai_attribution non-tree model `quant_model.py`: non-tree model -> AttributeError. Pre-existing.
- XAI calculate_comparative_metrics NaNs in is_test `quant_model.py`: NaNs in is_test -> ValueError. Pre-existing.
- XAI plot_xai_waterfall base_value None `visualizations.py`: base_value None -> TypeError. Pre-existing.

## Deferred from: code review of 4-2-final-outcomes-documentation-board (2026-05-08)
- Layout Boilerplate Duplication [streamlit_app.py] — Duplicated `st.columns([0.7, 0.3])` layouts. (Pre-existing/Accepted Streamlit pattern)
- Brittle Tuple Unpacking [streamlit_app.py] — Assuming exactly 4 returns from pipeline run. (Standard Python, deferring for now)
