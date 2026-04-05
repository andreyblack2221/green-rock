---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-04-03'
inputDocuments: [
  bmad_files/planning-artifacts/prd.md,
  bmad_files/planning-artifacts/prd-validation-report.md,
  bmad_files/planning-artifacts/ux-design-specification.md,
  bmad_files/planning-artifacts/ux-design-directions.html,
  docs/green-rock-initial-prd.md
]
workflowType: 'architecture'
project_name: 'green-rock'
user_name: 'Andrey'
date: '2026-04-03'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
- **Data Pipeline:** Fetching live data from `yfinance` and `FRED`, with an explicit mandate to seamlessly fall back to a bundled CSV snapshot without pipeline failure.
- **Quant Logic:** Processing data through an MA crossover baseline and a Random Forest classification model, comparing their results against traditional 60/40 benchmarking. 
- **Visualization:** Orchestrating a clean, data-dense web UI composed of Plotly interactive charts for explainable AI (Waterfall and Feature Importance visualizations).

**Non-Functional Requirements:**
- **Performance:** Strict service level requirements for load time (<10s live / <5s static) and chart re-rendering (<500ms).
- **Resilience:** Unbreakable demo flow. Seamless failover handling from live network timeouts to local datasets under 2 seconds.
- **Maintainability & Reproducibility:** Enforced modularity structure, static random seeding, fixed package dependencies, and simple cyclomatic complexity (<10 per function).

**Scale & Complexity:**
Project scale focuses heavily on data logic and fail-safes over intricate user-management or complex databases.

- Primary domain: Data Science / Quant App (Python `Streamlit`)
- Complexity level: Medium (Due to data validation and deterministic fallback mechanisms)
- Estimated architectural components: 4 core modules (Data Handler, Model Pipeline, Visualization Builders, Streamlit App Orchestrator).

### Technical Constraints & Dependencies

- **Platform:** Streamlit Cloud (Direct GH deployment, single-page `layout="wide"` container bounds). 
- **Dependencies:** Strictly using python-native dependencies (e.g. Scikit-learn, Pandas) and Streamlit's native integrations (Plotly wrapper). No external databases (e.g., Postgres); entirely file-system or memory-backed.
- **Design Guidelines:** Dark mode is explicitly discouraged for a Light Classic "Bloomberg" look; no custom complex React components. 

### Cross-Cutting Concerns Identified

- **Fault Tolerance Strategy:** Ensuring API rate-limits and timeouts never present tracebacks to front-end users. 
- **State Synchronization:** Maintaining a reliable global variable indicating `LIVE` or `CACHED` data modes, propagated seamlessly through all visual components.
- **Transparency & Explainability:** Propagating ML feature weights explicitly alongside classification outputs throughout the data flow so visual layers can always map 'why' a decision was reached.

## Starter Template Evaluation

### Primary Technology Domain

Python Data Science Fully-Stacked Web Application (Streamlit) based on project requirements analysis.

### Starter Options Considered

- **Streamlit Native Scaffolding (`streamlit init`):** The officially supported CLI command that generates the modern optimal project structure.
- **Custom FastAPI + React Stack:** Rejected. Violates the strict simplicity and dependency constraints outlined in the PRD, and breaks from the core "financial quant" presentation identity. Do not over-engineer.

### Selected Starter: Official Streamlit Scaffolding

**Rationale for Selection:**
Streamlit's native CLI (`streamlit init`), combined with the community-standard modular folder structure, strictly adheres to the low-complexity mandate. It provides built-in configuration for our Light Classic theme (`.streamlit/config.toml`) and naturally handles our `@st.cache_data` needs for the invisible data fallbacks.

**Initialization Command:**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit init
mkdir -p .streamlit src/green_rock/adapters src/green_rock/domain src/green_rock/service_layer src/green_rock/entrypoints tests/unit tests/integration tests/e2e data
touch .streamlit/config.toml docker-compose.yml Dockerfile Makefile requirements.txt
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
Python 3.10+, executing strictly in a localized `.venv` environment for pure reproducibility.

**Styling Solution:**
Handled natively via Streamlit's injected `.streamlit/config.toml`. No external CSS frameworks or Tailwind necessary, ensuring the UI remains robust during demos.

**Testing Framework & Architecture Guardrails:**
- **Strict Decoupling:** To prevent the natural "monolithic script" tendency of Streamlit, the system enforces a strict boundary between UI and Logic. 
- **Pure Python `utils/`:** All logic in `utils/` (data fetching, CSV fallback handling, Random Forest logic) must be pure Python and completely unaware of the Streamlit DOM. This allows 100% test coverage via `pytest` without spinning up the browser environment.
- **Deterministic State:** The fallback logic must resolve entirely *before* injecting into `st.session_state` to prevent UI flakiness.

**Code Organization:**
Strictly follows Layered/Hexagonal Architecture for high testability and production readiness, including explicit Config files, Docker configurations, and multi-tier testing schemas.
- `src/green_rock/domain/` → Pure business rules and models (e.g., Random Forest logic).
- `src/green_rock/adapters/` → I/O boundaries (e.g., `yfinance` fetching, CSV reads/writes).
- `src/green_rock/service_layer/` → Application use cases connecting adapters to the domain.
- `src/green_rock/entrypoints/` → UI orchestration (Streamlit apps and visualizations).
- `tests/` → Tiered testing (`unit`, `integration`, `e2e`) with explicit configurations (`conftest.py`).
- `docker-compose.yml` & `Dockerfile` → Standardized containerization and service orchestration.

**Development Experience:**
Live hot-reloading native to `streamlit run src/green_rock/entrypoints/streamlit_app.py`, combined with high-confidence TDD via explicit `pytest` tiers.

**Note:** Project initialization using this command should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- **Data Caching:** Full Pipeline Final-State Caching guarantees sub-500ms dashboard interactions.
- **Data Validation:** Hard Strict Validation paired with Automated Single-CSV Snapshotting guarantees the demo never crashes due to external API failures.

**Important Decisions (Shape Architecture):**
- **Structural Decoupling:** `scikit-learn` model logic and the Streamlit frontend visualization are strictly decoupled to allow testability.

**Deferred Decisions (Post-MVP):**
- **Real-Time Database Setup:** Deferred indefinitely. Relying on Streamlit's cache and local CSVs perfectly matches the PRD's simplicity mandate.

### Data Architecture

- **Caching Strategy:** Full Pipeline Final-State Caching natively managed via Streamlit's `@st.cache_data`.
- **Validation Engine:** Hard Strict Validation. `yfinance` fetches are screened for missing day rows or NaNs. If irregularities are detected, the system trips the breaker over to local data.
- **Snapshot Storage:** Offline data is handled by a single `data/static_snapshot.csv` master file, generated reliably by an isolated offline Python utility script that will be built prior to the app.

### Authentication & Security

- System is entirely public presentation software and requires no Authentication. 
- **Data Security:** The `static_snapshot.csv` contains only public market pricing data and requires no encryption at rest.

### API & Communication Patterns

- **API Flow:** Unidirectional batch fetch. The system fetches daily interval data from Yahoo Finance (`yfinance`) and FRED purely for historical calculations.
- **Error Handling:** Complete Silent Fallback. Front-end users will never see stack trace errors from API rate-limiting or timeouts. Any exception during extraction seamlessly triggers the local CSV injection.

### Frontend Architecture

- **Rendering Layer:** Exclusively `Streamlit (v1.55+)` natively paired with `Plotly`. 
- **State Management:** Uses native `st.session_state` to propagate a global `data_source` flag (`LIVE` vs `CACHED`) so the UI can accurately label the data provenance to the interviewer. All other charts are stateless reactive renders.

### Infrastructure & Deployment

- **Hosting:** Streamlit Cloud (Free Tier), deployed seamlessly from the GitHub branch.
- **CI/CD Approach:** The offline CSV snapshot is committed directly inside the repository. This guarantees that a fresh cloud deployment essentially "works out of the box" without needing external environment variables.

### Decision Impact Analysis

**Implementation Sequence:**
1. Scaffold project structure and `.venv` wrapper.
2. Build `scripts/generate_snapshot.py` to create the ultimate `static_snapshot.csv`.
3. Implement `utils/data_loader.py` demonstrating the live-fetch and automatic fallback tripwire.
4. Integrate `scikit-learn` inside `utils/model_pipeline.py`.
5. Wire up the final visual Pitch Deck sequence inside `streamlit_app.py`.

**Cross-Component Dependencies:**
- The Dashboard (`streamlit_app.py`) relies entirely on the structural shape of the DataFrame returned by `utils/model_pipeline.py`. This clear contractual boundary allows the UI to stay dumb while the ML module handles all the complex math.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
3 areas where AI agents could make conflicting structural or naming choices.

### Naming Patterns

**Code & Data Naming Conventions:**
- **Strict `snake_case`:** All Python variables, function names, and file names must utilize `snake_case` per standard PEP-8 guidelines. 
- **DataFrame Boundaries:** Pandas DataFrame columns must be explicitly mapped to `snake_case` immediately upon extraction from `yfinance` or FRED. NO spaces or capital letters are permitted in column headers (e.g., `closing_price`, not `Closing Price`).

### Structure Patterns

**File Organization Patterns:**
- Isolated Utility Architecture. No Streamlit visual API calls (`st.dataframe`, `st.metric`) may be executed inside the `utils/` directory. All calculations must return pure Python data structures (Dicts/DataFrames) or Plotly Figure objects to be rendered strictly by `streamlit_app.py`.

### Format Patterns

**Data Exchange Formats:**
- **Date Standardization:** All timezone-aware datasets fetched from external APIs must be normalized to standard `YYYY-MM-DD` naive formats or unified to UTC before performing DataFrame joins to prevent silent merge conflicts.

### Communication Patterns

**State Management Patterns:**
- **Session State Notation:** Streamlit session state access must exclusively use dictionary string notation (e.g., `st.session_state["data_mode"] = "LIVE"`) rather than dot notation. This standard avoids attribute injection errors during dynamic programming block execution.

### Process Patterns

**Error Handling Patterns:**
- **Decoupled Exceptions:** The backend utility modules (`utils/`) must never `import streamlit`. If an error occurs (e.g., `yfinance` timeout), the module should `raise` a standard Python Exception. Handling the error visually is strictly the responsibility of `streamlit_app.py` via an explicit `try/except` block encapsulating the module execution.

### Enforcement Guidelines

**All AI Agents MUST:**
- Write exclusively in `snake_case`.
- Utilize String dictionary syntax for `st.session_state["keys"]`.
- Raise standard Python exceptions rather than importing Streamlit logs in the backend logic.

### Pattern Examples

**Good Examples:**
```python
# Function strictly uses snake_case, standard exceptions, and pure Python
def fetch_closing_price(ticker_symbol: str) -> pd.DataFrame:
    if not ticker_symbol:
        raise ValueError("Ticker symbol is required")
    # ... logic returning a cleaned dataframe
```

**Anti-Patterns:**
```python
# AVOID: Streamlit imported in utils, camelCase, dot notation on state
import streamlit as st

def fetchClosingPrice():
    st.error("Failed to fetch") # Anti-Pattern: UI bleeding into backend logic
    st.session_state.dataMode = "failed" # Anti-Pattern: dot notation, camelCase
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
green-rock/
├── Dockerfile                  # Container build config
├── Makefile                    # Task shortcuts (e.g., make test)
├── docker-compose.yml          # Container orchestration
├── requirements.txt            # Dependency definitions
├── configs/                    # Application and environment configurations
├── .streamlit/
│   └── config.toml             # Streamlit Light Classic themes and settings
├── data/
│   └── static_snapshot.csv     # The verified offline fallback dataset
├── src/
│   └── green_rock/
│       ├── __init__.py
│       ├── adapters/           # I/O adapters (outbound calls)
│       │   ├── data_fetcher.py # yfinance & FRED data ingestion
│       │   └── file_repository.py # Interfacing with static_snapshot.csv
│       ├── domain/             # Pure quant business rules (no external constraints)
│       │   └── quant_model.py  # Random Forest logic and MA crossover logic
│       ├── service_layer/      # Application use-cases
│       │   └── pipeline.py     # Orchestrating data fetching -> domain processing
│       └── entrypoints/        # Inbound adapters (UI and endpoints)
│           ├── streamlit_app.py # Final UI orchestrator
│           └── visualizations.py # Plotly Chart generation
├── tests/
│   ├── conftest.py             # Shared pytest fixtures
│   ├── e2e/
│   │   └── test_ui.py          # End-to-end user flows
│   ├── integration/
│   │   └── test_adapters.py    # Testing data fetching & CSV loading
│   └── unit/
│       ├── test_domain.py      # Testing pure mathematical output
│       └── test_services.py    # Testing orchestration flow
├── .gitignore
└── README.md
```

### Architectural Boundaries

**API Boundaries:**
- The Application UI (`entrypoints/streamlit_app.py`) **never** directly touches internet APIs. 
- All external calls to Yahoo Finance and FRED are strictly cordoned off inside `adapters/data_fetcher.py`.

**Component Boundaries:**
- **UI Space:** The `entrypoints` layer is the only layer legally allowed to `import streamlit as st`. It simply asks the `service_layer` for fully processed data dictionaries/DataFrames, formats them via `visualizations.py`, and displays them on the screen.
- **Logic Space:** The `domain` layer contains standard pure Python mathematical components, completely isolated from Streamlit dependencies and I/O logic.

**Data Boundaries:**
- The `service_layer` handles the error-handling fallback orchestration: it attempts to fetch via `adapters/data_fetcher`. If it hits a timeout or missing data, it immediately reads from `adapters/file_repository` (which maps to `data/static_snapshot.csv`).

### Requirements to Structure Mapping

**Epic/Feature Mapping:**
- **Data Pipeline (EPIC-01):** Implemented inside `adapters/data_fetcher.py` and `adapters/file_repository.py`.
- **Model Pipeline (EPIC-02):** Pure math implemented inside `domain/quant_model.py`. The execution of this math flow is orchestrated by `service_layer/pipeline.py`.
- **UI & Visualization (EPIC-03):** Visual layout lives in `entrypoints/streamlit_app.py` via chart components derived from `entrypoints/visualizations.py`.

### File Organization Patterns

**Source Organization:**
- Development is driven by explicit layer contracts. Running `pytest tests/unit/` validates the math immediately. Running `pytest tests/integration/` validates live API dependencies are working. Full visual checks are done via `streamlit run src/green_rock/entrypoints/streamlit_app.py`.

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
All architectural decisions are highly compatible. Python, Streamlit, Pandas, and Scikit-learn represent the gold-standard stack for Quant analysis. The strictly enforced boundary separating `scikit-learn` logic from Streamlit's reactive DOM prevents the most common class of Streamlit memory leak errors.

**Pattern Consistency:**
`snake_case` paired with `st.session_state` Dictionary addressing stringently protects against naming collision errors when multiple AI agents attempt to write code.

**Structure Alignment:**
The pure-logic `utils/` directory perfectly aligns with the requirement for robust testing, guaranteeing that `pytest` can run completely in isolation without requiring a browser driver.

### Requirements Coverage Validation ✅

**Epic/Feature Coverage:**
- EPIC-01 (Data Pipeline): Fully mapped to `data_loader.py` and `static_snapshot.csv`.
- EPIC-02 (Model Logic): Fully mapped to `model_pipeline.py` using `scikit-learn`.
- EPIC-03 (Visualization): Fully mapped to `visualizations.py` and `streamlit_app.py`.

**Functional Requirements Coverage:**
The fallback logic constraint is structurally guaranteed by the `try/Except` wrapper inside standard pure python.

**Non-Functional Requirements Coverage:**
The strict Performance NFR (<500ms interaction) is guaranteed by our early decision to adopt Full Pipeline Final-State Caching.

### Implementation Readiness Validation ✅

**Decision Completeness:**
All Streamlit and structural framework constraints are explicitly documented.

**Structure Completeness:**
The specific 10-file repository tree is locked, ensuring AI implementation agents do not invent arbitrary modules or files. 

### Gap Analysis Results

**Nice-to-Have Gaps:**
- Deployment caching techniques inside Streamlit Cloud's internal environments could be optimized further if data fetch sizes become gigantic, but this is a low priority for MVP size datasets.

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined

**✅ Implementation Patterns**
- [x] Naming conventions established
- [x] Structure and boundary patterns defined

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION
**Confidence Level:** HIGH

**Key Strengths:**
Extremely resilient. The Hard Strict Validation mechanism falling back elegantly to a local CSV guarantees an "unbreakable" demonstration flow, which is the paramount business value of the dashboard.

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented.
- Use Python `snake_case` implementation patterns consistently.
- Respect the strict separation between `utils/` components and `streamlit_app.py`.

**First Implementation Priority:**
Initialize the python `.venv` and execute standard `requirements.txt` installation, then construct the `scripts/generate_snapshot.py` to freeze the fallback data.
