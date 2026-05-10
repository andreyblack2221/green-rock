# Story 2.1: Random Forest Classifier Pipeline

## Story Foundation
**Story ID:** 2.1
**Story Key:** 2-1-random-forest-classifier-pipeline
**Epic:** Epic 2: Transparent ML Classification Engine
**Status:** done

**User Story:**
As a quantitative modeler,
I want to train a Random Forest model strictly enforcing time-boundaries and deterministic parameters,
So that I can generate robust risk regime classifications without introducing forward data leakage or unexplainable run-to-run changes.

**Acceptance Criteria:**
- **Given** the normalized data structure is ready for modeling
  **When** the model splits the data into training and testing sets
  **Then** it forcibly respects time ordering, ensuring test data strictly originates temporally after training data
  **And** no random row shuffling occurs prior to the temporal split
- **Given** the Random Forest model is instantiated
  **When** the `fit` and `predict` cycles execute
  **Then** the model strictly utilizes a hard-coded random seed state to ensure deterministic, reproducible results across container runs
  **And** it accurately predicts risk regimes (Low, Medium, High) for the out-of-sample test period
  **And** this implementation remains fully cordoned within the `domain/` layer without Streamlit DOM dependencies

---

## Developer Context & Guardrails

### Technical Requirements
- **Model:** `RandomForestClassifier` from Scikit-Learn.
- **Data Split:** Must use strict time-based boundary (e.g. `TimeSeriesSplit` or simple list slicing over sorted dates). NO `train_test_split` with `shuffle=True`.
- **Determinism:** Pass `random_state=42` (or another fixed integer) to the RandomForest model.
- **Classes:** Model output classes must be explicitly mapped to ["Low", "Medium", "High"].
- **Logic placement:** `src/green_rock/domain/quant_model.py`.

### Architecture Compliance
- **Decoupled Architecture:** NO `import streamlit as st` anywhere in `domain/` or `utils/`.
- **Function Parameters:** Input to mathematical functions should be pure Python structures (Pandas DataFrames, Series, lists).
- **Naming Conventions:** All variables and functions MUST be `snake_case`. Pandas DataFrames MUST use snake_case for column headers if not already standard.
- **Cyclomatic Complexity:** Functions in the model must have a cyclomatic complexity of < 10. Split into smaller functions if needed.
- **Exceptions:** Use standard Python exceptions for validation, UI manages visuals.

### Library & Framework Requirements
- **Scikit-learn:** `sklearn.ensemble.RandomForestClassifier`
- **Pandas:** Strictly return clean Pandas structures to be displayed by Streamlit later.

### File Structure Requirements
- **Modify:** `src/green_rock/domain/quant_model.py` (add Random Forest logic next to the existing MA baseline logic).
- **Modify:** `src/green_rock/service_layer/pipeline.py` (orchestrate the model fetching out classification results if appropriate for Epic 2).
- **Do not modify:** Visualizations or Streamlit app logic in this story. That will be done in subsequent stories or `entrypoints/`.

### Testing Requirements
- **Unit Tests:** Must add unit tests in `tests/unit/test_domain.py` testing the deterministic result given a fixed input dataset (i.e. if run 10 times, returns same predictions).
- **Mock Data:** Same mock linear progression `spy_close` used in step 1.4 can be used here. (See: `test_domain.py` linear progression DataFrame construction for synthetic predictability). Don't use live fetching inside unit tests.

### Git Intelligence & Previous Learnings
- **Previous Commit Context:** Commit `a207c9c` successfully implemented `domain` isolation for the baseline models. Maintain that pattern.
- **Testing Context:** Synthetic linear data used in previous domain tests ensures perfectly predictable outcomes. Continue using that paradigm instead of fetching live data in unit tests.

### Project Context Reference
- Ensure adherence to all PRD FR9-FR11 requirements for this Epic.

## Status Update
- **Completion Note:** Ultimate context engine analysis completed - comprehensive developer guide created. Status changed to ready-for-dev.

## Tasks/Subtasks

- [x] Task 1: Create failing unit tests for the deterministic Random Forest model in `tests/unit/test_domain.py`, utilizing the `spy_close` mock linear progression data.
- [x] Task 2: Implement time-series split and `RandomForestClassifier` logic in `src/green_rock/domain/quant_model.py` mapping to ["Low", "Medium", "High"], strictly observing deterministic `random_state=42`.
- [x] Task 3: Modify `src/green_rock/service_layer/pipeline.py` to support classification orchestration optionally alongside baseline logic.

### Review Findings
- [x] [Review][Patch] Missing bounds validation for `test_ratio` [src/green_rock/domain/quant_model.py]
- [x] [Review][Patch] Missing check for required columns in DataFrame before fitting [src/green_rock/domain/quant_model.py]
- [x] [Review][Patch] Target output regimes not strictly validated against expected labels ["Low", "Medium", "High"] [src/green_rock/domain/quant_model.py]
- [x] [Review][Defer] Single regime class in training data is not gracefully handled [src/green_rock/domain/quant_model.py] — deferred, pre-existing

## Dev Agent Record

### Debug Log
- N/A

### Completion Notes
- All acceptance criteria satisfied.
- Unit tests validating time-based splitting and deterministic `random_state=42` outcomes were created in `tests/unit/test_domain.py`.
- `train_and_predict_rf` function was added to `src/green_rock/domain/quant_model.py` strictly restricting itself to model training and predicting without polluting UI boundaries. Time splits are exact list slicing without shuffling.
- `DataPipeline` in `src/green_rock/service_layer/pipeline.py` enhanced with a full `run_pipeline` orchestration method to allow configurable executions of baseline and ml models.
- All 52 tests passing locally, no architectural rules violated.

## File List
- src/green_rock/domain/quant_model.py
- src/green_rock/service_layer/pipeline.py
- tests/unit/test_domain.py

## Change Log
- Added `train_and_predict_rf` ML domain model.
- Added deterministic Random Forest unit tests.
- Modified `DataPipeline` adding `run_pipeline` method for end-to-end processing.
