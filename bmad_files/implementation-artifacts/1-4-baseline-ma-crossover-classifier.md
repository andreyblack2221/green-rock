# Story 1.4: Baseline MA Crossover Classifier

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a skeptical evaluator,
I want a simple, universally understood Moving-Average quantitative model to establish current risk,
So that I have a reliable baseline against which the Machine Learning model's performance can be judged.

## Acceptance Criteria

1. **Given** the resilient data dataframe has been successfully loaded into memory
2. **When** it passes into the `domain/` layer quantitative functions
3. **Then** the logic calculates a simple Moving-Average crossover (e.g., short MA vs long MA) 
4. **And** it outputs an explicit Market Risk classification mapping: "Low", "Medium", or "High" for every row
5. **And** the logic is written entirely in pure Python, maintaining no dependencies on Streamlit rendering
6. **Given** the risk classifications are returned
7. **When** code tests or reviews are run on the function
8. **Then** the function explicitly retains a cyclomatic complexity under 10
9. **And** the function is fully documented with a docstring explaining the math

## Tasks / Subtasks

- [x] Task 1: Create Baseline Model in Domain Layer (AC: 1, 2, 3)
  - [x] Create `src/green_rock/domain/quant_model.py` (if it does not exist)
  - [x] Implement `calculate_baseline_regime(df: pd.DataFrame) -> pd.DataFrame` moving average function
- [x] Task 2: Implement Risk Mapping and Strict Guardrails (AC: 4, 5, 8, 9)
  - [x] Add explicit mathematical docstrings to the function
  - [x] Map calculations to "Low", "Medium", "High" regimes and assign to a new `snake_case` column like `baseline_regime`
  - [x] Ensure function cyclomatic complexity < 10
  - [x] Ensure absolutely no `streamlit` import in the domain
- [x] Task 3: Unit Testing (AC: 7)
  - [x] Create/Modify `tests/unit/test_domain.py` to test different market pricing regimes and verify correct mappings

### Review Findings

- [x] [Review][Decision] Warm-up rows return `np.nan`, not a classification (AC 4) — resolved: raise `ValueError` if `len(df) < long_window`; warm-up rows documented as `np.nan` by design [quant_model.py:53]
- [x] [Review][Patch] Remove unused standalone `import numpy as np` — kept and used for `np.nan` [quant_model.py:6]
- [x] [Review][Patch] Nullify rows where `short_ma` is NaN (not just `long_ma`) — warm_up_mask covers both [quant_model.py:60]
- [x] [Review][Patch] Add input validation for `short_window` and `long_window` (positive integers, short < long) [quant_model.py:43-51]
- [x] [Review][Patch] Remove exploratory scratch-note comments from test file [test_domain.py]
- [x] [Review][Patch] Add regime-specific assertions — deterministic Low/High tests added [test_domain.py]
- [x] [Review][Patch] Use `np.nan` consistently instead of Python `None` for missing `baseline_regime` [quant_model.py:62]
- [x] [Review][Patch] Export `calculate_baseline_regime` from `domain/__init__.py` public API [domain/__init__.py]
- [x] [Review][Defer] DataFrame shorter than `long_window` returns all `None` values with no exception — silently empty output [quant_model.py] — deferred, pre-existing design choice
- [x] [Review][Defer] No index-sorting requirement documented — unsorted/duplicate DatetimeIndex would produce incorrect rolling window results [quant_model.py] — deferred, pre-existing

## Dev Notes

### Dev Agent Guardrails & Technical Requirements
- Implement data processing solely with pure Python and Pandas.
- Incorporate simple but clear explicit moving averages logic on the data.
- Include thorough docstrings outlining mathematical rules, as mandated by NFR9.
- Use explicit `snake_case` patterns continually.

### Architecture Compliance
- Logic MUST reside in `src/green_rock/domain/` layer. 
- NEVER `import streamlit as st` anywhere in `domain/` layer (strictly forbidden).
- The function should take a DataFrame as input, and output an explicitly annotated DataFrame or identical sized structure with a new derived metric column.

### Library & Framework Requirements
- Pandas natively (`df['spy_close'].rolling(window=...).mean()`).
- Avoid Scikit-learn for this baseline story.

### File Structure Requirements
- Modify/Create: `src/green_rock/domain/__init__.py`
- Modify/Create: `src/green_rock/domain/quant_model.py`
- Modify/Create: `tests/unit/test_domain.py`

### Testing Requirements
- Use `pytest`. Test pure mathematical outcomes (e.g., provide explicit mock rows resulting in high / low regimes).
- The domain layer is pure logical application behavior decoupled from data; no `yfinance` fetches needed during test.

### Previous Story Intelligence
- Data pipeline currently emits a dataframe with explicit `snake_case` variables like `spy_close` and timezone-normalized indexes. The domain function can reliably assume `spy_close` will be present under normal circumstances.

### Reference Project Architecture
- See `bmad_files/planning-artifacts/architecture.md` for explicit structural mandates and pattern examples. Do NOT deviate.

### Story Completion Status
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List
- Implemented `calculate_baseline_regime` in `src/green_rock/domain/quant_model.py`.
- Used Pandas vectorized logic to compute trailing Moving-Average values.
- Mapped ratios strictly to "Low", "Medium", and "High" into a new `baseline_regime` column directly.
- Added comprehensive mathematical docstrings explaining ratio comparisons.
- No references to Streamlit were introduced to the domain layer.
- Implemented associated unit tests in `tests/unit/test_domain.py`.
- All tests pass (incl. 17 pipeline regressions) demonstrating complete architectural compliance.

### File List
- src/green_rock/domain/__init__.py (Created)
- src/green_rock/domain/quant_model.py (Created)
- tests/unit/test_domain.py (Created)
