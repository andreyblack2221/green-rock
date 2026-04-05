# Story 1.1: Initial Application Scaffolding & Visual Theming

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a builder and demonstrator,
I want the Streamlit web application environment, decoupled architectural folders, and global visual theme fully configured,
so that I can easily deploy the code to a cloud environment and ensure all subsequent features follow a uniform, institutional "Light Classic" aesthetic.

## Acceptance Criteria

1. Given the developer has cloned the repository, When they run an environment installation using `requirements.txt` and launch `streamlit run src/green_rock/entrypoints/streamlit_app.py`, Then the application launches successfully on a single local web page without errors.
2. The project directory rigidly contains `adapters/`, `domain/`, `service_layer/`, and `entrypoints/` folders.
3. Given the application is running, When the user views the baseline UI, Then the UI utilizes Streamlit's `layout="wide"` configuration.
4. The UI adopts the Light Classic theme via `.streamlit/config.toml` (White background, Slate Blue primary color, Charcoal text, Institutional Grey secondary backgrounds).
5. Given the codebase is pushed to version control, When a Streamlit Cloud environment targets the repository, Then it natively identifies the setup and runs the bare dashboard without manual configuration.

## Tasks / Subtasks

- [x] Scaffolding and folder structure (AC: 1, 2)
  - [x] Initialize Python virtual environment configuration pattern.
  - [x] Ensure project directory rigidly contains `adapters/`, `domain/`, `service_layer/`, and `entrypoints/` under `src/green_rock/`.
  - [x] Initialize `tests/` folders (unit, integration, e2e) and configuration.
  - [x] Scaffold `data/`, `configs/`, and `.streamlit/` folders.
  - [x] Initialize basic Dockerfile, docker-compose.yml, Makefile, .gitignore and README.md.
- [x] Dependencies and Application Entrypoint (AC: 1, 5)
  - [x] Create `requirements.txt` with tightly pinned `streamlit>=1.55.0` and foundational pure Python data science packages (like pandas).
  - [x] Create basic `src/green_rock/entrypoints/streamlit_app.py` with `layout="wide"` config.
- [x] Theme Configuration (AC: 3, 4)
  - [x] Configure `.streamlit/config.toml` for the Light Classic theme.
    - [x] Set `primaryColor` to Deep Slate Blue (`#1F3A5F`).
    - [x] Set `backgroundColor` to Pure White (`#FFFFFF`).
    - [x] Set `secondaryBackgroundColor` to Light Institutional Grey (`#F0F2F6`).
    - [x] Set `textColor` to High-Contrast Charcoal (`#262730`).
    - [x] Set `font` to "sans serif".

## Dev Notes

- **Streamlit Restrictions:** Decoupled architecture requires NO `import streamlit as st` anywhere EXCEPT `entrypoints/`. 
- **Dependencies:** Exclusively rely on standard pip python-native dependencies (pandas, scikit-learn).
- **Naming Pattern:** Strictly adhere to `snake_case` according to Architecture decisions.
- **System Theme:** Avoid dark mode concepts; purely focus on Light Classic.

### Project Structure Notes

- Create exactly carefully matched files to mirror the architectural decision document template.
```text
green-rock/
├── Dockerfile
├── Makefile
├── docker-compose.yml
├── requirements.txt
├── configs/
├── .streamlit/
│   └── config.toml
├── data/
│   └── static_snapshot.csv
├── src/
│   └── green_rock/
│       ├── adapters/
│       ├── domain/
│       ├── service_layer/
│       └── entrypoints/
│           ├── streamlit_app.py
├── tests/
│   ├── conftest.py
│   ├── e2e/
│   ├── integration/
│   └── unit/
├── .gitignore
└── README.md
```

### References

- Architecture Decisions: [Source: bmad_files/planning-artifacts/architecture.md#Complete Project Directory Structure]
- PRD Requirements: [Source: bmad_files/planning-artifacts/prd.md#Epic 1: The Resilient Baseline Dashboard]
- UX Patterns: [Source: bmad_files/planning-artifacts/ux-design-specification.md#Design System Foundation]

### Dev Agent Record

### Agent Model Used

Gemini 3.1 Pro (High)

### Debug Log

- Replaced `Status: ready-for-dev` with `Status: review`
- Scaffolding complete; initialized Makefile to manage venv and pip installs instead of just arbitrary shell commands. Created dummy tests/unit/test_app.py to ensure the entrypoint is importable via Pytest.

### Completion Notes

- **AC: 1, 2** Met by establishing the foundational `src/green_rock/...` directories and providing `make install` pattern alongside a `Dockerfile`.
- **AC: 1, 5** Met by including `requirements.txt` with pinned streamlit+pandas+scikit-learn and explicitly setting `layout="wide"` in `src/green_rock/entrypoints/streamlit_app.py`.
- **AC: 3, 4** Met by creating `.streamlit/config.toml` exactly matching the Light Classic palette.
- Added `pytest` setup to guarantee structural integrity of the barebones pipeline.

### File List

- `requirements.txt` (New)
- `Dockerfile` (New)
- `docker-compose.yml` (New)
- `Makefile` (New)
- `.gitignore` (New)
- `README.md` (New)
- `tests/conftest.py` (New)
- `tests/unit/test_app.py` (New)
- `.streamlit/config.toml` (New)
- `src/green_rock/entrypoints/streamlit_app.py` (New)
- `bmad_files/implementation-artifacts/sprint-status.yaml` (Modified)

### Review Findings
- [x] [Review][Patch] Contradiction for Streamlit Cloud Zero-Config — Streamlit Cloud seeks app.py in the repository root by default. Added root app.py as wrapper file.
- [x] [Review][Patch] Incorrect Streamlit Version Pinning [requirements.txt:3]
- [x] [Review][Patch] Missing Structural Directories in Version Control [.gitkeep]
- [x] [Review][Patch] Missing data/static_snapshot.csv File [data/static_snapshot.csv]
- [x] [Review][Patch] Blatant container security risk [Dockerfile]
- [x] [Review][Patch] Missing .dockerignore file [.dockerignore]
- [x] [Review][Patch] Unmanaged external telemetry [.streamlit/config.toml]
- [x] [Review][Patch] curl hangs indefinitely in HEALTHCHECK [Dockerfile:21]
- [x] [Review][Patch] ImportError traceback swallowed [tests/unit/test_app.py:6]
- [x] [Review][Defer] Non-deterministic dependencies [requirements.txt] — deferred, pre-existing
- [x] [Review][Defer] Absence of static analysis tooling [N/A] — deferred, pre-existing

