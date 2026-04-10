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
