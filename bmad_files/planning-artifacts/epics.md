---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories]
inputDocuments: 
  - bmad_files/planning-artifacts/prd.md
  - bmad_files/planning-artifacts/architecture.md
  - bmad_files/planning-artifacts/ux-design-specification.md
---

# green-rock - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for green-rock, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: System can fetch daily price data for SPY, TLT, and GLD from an external market data provider
FR2: System can fetch 10Y-2Y yield curve spread data from an external economic data provider
FR3: System can calculate rolling volatility from price data
FR4: System can fall back to a bundled static data snapshot when external data calls fail
FR5: System can display a notification indicating whether live or cached data is in use
FR6: System can validate fetched data for missing dates, zero/negative prices, and duplicates before processing
FR7: System can produce a normalized, date-aligned data structure combining all data sources
FR8: System can classify market risk regimes as Low, Medium, or High using a moving-average crossover baseline model
FR9: System can classify market risk regimes as Low, Medium, or High using a trained Random Forest classifier
FR10: System can train the classifier deterministically to ensure reproducible results across runs
FR11: System can split training and test data respecting time ordering (no future data leakage)
FR12: System can map risk regimes to 3-bucket allocation weights (equities-heavy, balanced, defensive)
FR13: System can calculate portfolio returns for both models' allocation strategies
FR14: System can calculate returns for a 60/40 stock-bond benchmark
FR15: System can calculate returns for an S&P 500 buy-and-hold benchmark
FR16: System can display comparison of all strategies' performance
FR17: User can view a regime timeline chart with color-coded bands (green/yellow/red) overlaid on price data
FR18: User can view an Explainable AI (XAI) Risk Attribution Waterfall chart showing why the model shifted regimes today
FR19: User can view a feature importance bar chart showing which inputs drive Random Forest classifications overall
FR20: User can view a model comparison showing baseline vs. Random Forest regime outputs side-by-side
FR21: User can view benchmark performance comparison across all strategies
FR22: User can access all views from a single web-based interactive dashboard page
FR23: User can run the dashboard locally via a single startup command
FR24: System can be deployed to a cloud hosting environment directly from the version control repository
FR25: User can run the project using only bundled static data (no API keys required for first run)
FR26: System provides a one-step installer for all required dependencies

### NonFunctional Requirements

NFR1: [Load Time] Dashboard initial load time must be < 5 seconds as measured by automated performance testing when using static fallback data to ensure a smooth demo experience
NFR2: [Load Time] Dashboard initial load time must be < 10 seconds as measured by automated performance testing when fetching live external data to prevent user abandonment
NFR3: [Render Performance] All chart views must render in < 500ms as measured by browser profiling tools after data is loaded to ensure fluent navigation between views
NFR4: [Training Performance] Model training must complete in < 30 seconds as measured by internal execution timers on a standard 4-core machine to allow rapid iterative backtesting
NFR5: [Fallback Reliability] System must switch to static fallback data within 2 seconds as measured by fault-injection testing when primary market data APIs return 4xx/5xx errors or timeout
NFR6: [Fallback Reliability] System must switch to static fallback data within 2 seconds as measured by fault-injection testing when economic APIs return 4xx/5xx errors or timeout
NFR7: [Status Clarity] System must display a visible data source indicator on the primary UI as measured by visual inspection during usability testing
NFR8: [Modularity] Code must be organized into decoupled modules (data ingestion, modeling, visualization) as measured by a dependency graph analyzer to ensure independent maintainability
NFR9: [Documentation] All financial logic functions must include docstrings explaining the mathematical reasoning as measured by code review and documentation coverage tools
NFR10: [Complexity] No individual function may exceed a cyclomatic complexity of 10 as measured by static analysis tools to ensure logic remains simple enough to explain during an interview
NFR11: [Reproduculity] All project package dependencies must be strictly version-pinned in a lockfile mechanism as measured by CI/CD dependency scanning to prevent silent behavior changes across runs

### Additional Requirements

- Starter Template: Use official Streamlit CLI Scaffolding natively and explicitly initialize the predetermined hex architecture structure (`adapters/`, `domain/`, `service_layer/`, `entrypoints/`, `tests/`) as a required first step for Epic 1 Story 1.
- Strict isolation boundary: Reusable component and Quant logic inside `domain` must NEVER `import streamlit`. Use Pure Python patterns and decouple dependencies.
- Fallback data orchestration: Read offline CSV `data/static_snapshot.csv` immediately on API timeout/error without surfacing red stack traces to frontend users.
- Development restrictions: Use Python `snake_case` patterns strictly and dictionary-based session_state (e.g., `st.session_state["key"]`).

### UX Design Requirements

UX-DR1: Establish a "Pitch Deck Scroll" vertical layout with 3 explicit visual phases ("Acts") separated by `st.markdown("---")` dividers.
UX-DR2: Set up Light Classic Streamlit Theme configuration globally in `.streamlit/config.toml` (White bg, Slate Blue primary, Institutional Grey metrics). 
UX-DR3: Ensure universal color coding across all interactive states: Forest Green (#388E3C) and Crimson (#D32F2F) only for risk/outcomes.
UX-DR4: Implement the "Hero Component": an interactive XAI Waterfall Chart via Plotly `go.Waterfall`, fully scaling to container width and styled to UX color tokens.
UX-DR5: Inject a Custom HTML State Context Badge in top right corner representing Live API Sync vs Static Demo Mode with green/amber visual borders.
UX-DR6: Utilize `layout="wide"`, wrap qualitative textual narrative sequentially in `st.columns` constraint blocks while letting Visualizations occupy full container width.
UX-DR7: Configure all Plotly visual chart integrations with `use_container_width=True` and minimized layout margins to ensure perfect mobile responsiveness.
UX-DR8: Standardize Benchmark performance layout exclusively using `st.dataframe` formatting to fulfill accessibility contrast expectations intuitively.

### FR Coverage Map

FR1: Epic 1 - Fetch daily asset prices
FR2: Epic 1 - Fetch yield curve spread
FR3: Epic 1 - Calculate rolling volatility
FR4: Epic 1 - Static data fallback
FR5: Epic 1 - Live vs cached badge notification
FR6: Epic 1 - Data validation (dates, NaN)
FR7: Epic 1 - Normalized data structuring
FR8: Epic 1 - Baseline MA classification
FR9: Epic 2 - Random Forest classification
FR10: Epic 2 - Deterministic classifier training
FR11: Epic 2 - Time-ordered train/test splits
FR12: Epic 4 - Risk regimes allocation weights
FR13: Epic 4 - Portfolio return calculation
FR14: Epic 4 - 60/40 benchmark returns
FR15: Epic 4 - SP500 benchmark returns
FR16: Epic 4 - Comparing strategies performance
FR17: Epic 1 - Regime timeline visualization
FR18: Epic 3 - XAI Waterfall chart implementation
FR19: Epic 2 - Feature importance bar chart
FR20: Epic 2 - Model outcome comparison view
FR21: Epic 4 - Benchmark performance view
FR22: Epic 1 - Streamlit dashboard setup
FR23: Epic 1 - Local runner setup
FR24: Epic 1 - Cloud compatibility
FR25: Epic 1 - Offline first-run capability
FR26: Epic 1 - Single installer (`requirements.txt`)

## Epic List

### Epic 1: The Resilient Baseline Dashboard
Users can securely launch a professionally themed single-page dashboard that successfully fetches market data (or falls back invisibly to a local snapshot) and cleanly visualizes the simple moving-average risk timeline as our firm anchor point.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR17, FR22, FR23, FR24, FR25, FR26

### Epic 2: Transparent ML Classification Engine
Users can compare the Random Forest risk predictions side-by-side against the baseline, and view the global feature importance chart to understand what drives the intelligence.
**FRs covered:** FR9, FR10, FR11, FR19, FR20

### Epic 3: Explainable AI Risk Attribution (The XAI Reveal)
Users can easily unpack the Machine Learning's specific daily decision-making process through an intuitive, full-width "Hero" Waterfall chart explaining exactly why today's risk regime was chosen.
**FRs covered:** FR18

### Epic 4: Strategy Benchmarking & Outcomes
Users can validate the investment thesis by mapping regimes to asset allocations, then comparing the final financial returns of the ML model, the baseline, and standard market benchmarks.
**FRs covered:** FR12, FR13, FR14, FR15, FR16, FR21

## Epic 1: The Resilient Baseline Dashboard

Users can securely launch a professionally themed single-page dashboard that successfully fetches market data (or falls back invisibly to a local snapshot) and cleanly visualizes the simple moving-average risk timeline as our firm anchor point.

### Story 1.1: Initial Application Scaffolding & Visual Theming

As a builder and demonstrator,
I want the Streamlit web application environment, decoupled architectural folders, and global visual theme fully configured,
So that I can easily deploy the code to a cloud environment and ensure all subsequent features follow a uniform, institutional "Light Classic" aesthetic.

**Acceptance Criteria:**

**Given** the developer has cloned the repository
**When** they run an environment installation using `requirements.txt` and launch `streamlit run src/green_rock/entrypoints/streamlit_app.py`
**Then** the application launches successfully on a single local web page without errors
**And** the project directory rigidly contains `adapters/`, `domain/`, `service_layer/`, and `entrypoints/` folders

**Given** the application is running
**When** the user views the baseline UI
**Then** the UI utilizes Streamlit's `layout="wide"` configuration
**And** the UI adopts the Light Classic theme via `.streamlit/config.toml` (White background, Slate Blue primary color, Charcoal text, Institutional Grey secondary backgrounds)

**Given** the codebase is pushed to version control
**When** a Streamlit Cloud environment targets the repository 
**Then** it natively identifies the setup and runs the bare dashboard without manual configuration

### Story 1.2: Offline Data Snapshot Generator

As a developer,
I want an isolated script to fetch and save clean market data to a local file,
So that I can bundle a guaranteed-to-work dataset within the repository for unbreakable offline demonstrations.

**Acceptance Criteria:**

**Given** the developer runs the standalone `scripts/generate_snapshot.py` utility
**When** the script executes
**Then** it successfully requests historical price data (SPY, TLT, GLD) and yield curve data
**And** it normalizes the data to a single date-aligned structure with `snake_case` column headers and no missing date gaps
**And** it saves the cleaned output exclusively to `data/static_snapshot.csv` without modifying the Streamlit environment state

### Story 1.3: Resilient Data Fetcher

As a dashboard viewer,
I want the application to automatically serve data robustly regardless of internet connectivity or API limits,
So that my experience exploring the data is never interrupted by stack traces or loading errors.

**Acceptance Criteria:**

**Given** an active internet connection and available API limits
**When** the `adapters/data_fetcher.py` attempts to fetch live data upon application load
**Then** the application retrieves the normalized data array from Yahoo Finance and FRED
**And** it dynamically calculates a rolling volatility column based on the price data

**Given** the external API times out, rate limits, or returns 4xx/5xx errors
**When** the application attempts to fetch data
**Then** the service layer gracefully catches the pure Python exception within 2 seconds
**And** it seamlessly reads from the local `adapters/file_repository.py` (`data/static_snapshot.csv`) instead
**And** the UI state tracking dictionary (`st.session_state["data_source"]`) is securely updated to reflect the fallback (e.g. from "LIVE" to "CACHED") without crashing

### Story 1.4: Baseline MA Crossover Classifier

As a skeptical evaluator,
I want a simple, universally understood Moving-Average quantitative model to establish current risk,
So that I have a reliable baseline against which the Machine Learning model's performance can be judged.

**Acceptance Criteria:**

**Given** the resilient data dataframe has been successfully loaded into memory
**When** it passes into the `domain/` layer quantitative functions
**Then** the logic calculates a simple Moving-Average crossover (e.g., short MA vs long MA) 
**And** it outputs an explicit Market Risk classification mapping: "Low", "Medium", or "High" for every row
**And** the logic is written entirely in pure Python, maintaining no dependencies on Streamlit rendering

**Given** the risk classifications are returned
**When** code tests or reviews are run on the function
**Then** the function explicitly retains a cyclomatic complexity under 10
**And** the function is fully documented with a docstring explaining the math

### Story 1.5: Narrative Shell & Interactive Timeline Presentation

As an evaluator reviewing the UI,
I want to be guided horizontally through the data thesis while easily identifying risk regimes,
So that I can comprehend the baseline claims instantly before viewing the complex ML model.

**Acceptance Criteria:**

**Given** the Streamlit application is actively rendering
**When** the layout is drawn
**Then** it enforces a strict "Pitch Deck Scroll" vertical hierarchy separated by explicit `st.markdown("---")` chapter divider lines
**And** the textual narrative is securely encapsulated using `st.columns` to prevent visually endless text wrap on large screens

**Given** the baseline risk timeline is rendered on screen using `st.plotly_chart`
**When** the timeline is drawn over the price data
**Then** it dynamically takes up the full container width (`use_container_width=True`) and zeroes out unnecessary layout margins
**And** the background bands explicitly enforce strict UX-DR3 color coding (Forest Green for Low risk periods, Crimson for High risk, Amber for Warning) mapped natively to Plotly

**Given** the UI has loaded data
**When** the user looks at the top right of the dashboard
**Then** an injected Custom HTML State Badge prominently reflects the session status displaying either a green line for 'Live API Sync' or an amber line for 'Static Demo Mode' based entirely on `st.session_state`

## Epic 2: Transparent ML Classification Engine

Users can compare the Random Forest risk predictions side-by-side against the baseline, and view the global feature importance chart to understand what drives the intelligence.

### Story 2.1: Random Forest Classifier Pipeline

As a quantitative modeler,
I want to train a Random Forest model strictly enforcing time-boundaries and deterministic parameters,
So that I can generate robust risk regime classifications without introducing forward data leakage or unexplainable run-to-run changes.

**Acceptance Criteria:**

**Given** the normalized data structure is ready for modeling
**When** the model splits the data into training and testing sets
**Then** it forcibly respects time ordering, ensuring test data strictly originates temporally after training data
**And** no random row shuffling occurs prior to the temporal split

**Given** the Random Forest model is instantiated
**When** the `fit` and `predict` cycles execute
**Then** the model strictly utilizes a hard-coded random seed state to ensure deterministic, reproducible results across container runs
**And** it accurately predicts risk regimes (Low, Medium, High) for the out-of-sample test period
**And** this implementation remains fully cordoned within the `domain/` layer without Streamlit DOM dependencies

### Story 2.2: Feature Importance Extraction & Visualization

As an evaluator assessing the model's transparency,
I want to clearly see which quantitative inputs most heavily dictated the Random Forest model's overall learned behavior,
So that I can verify the model is weighing logical economic factors (like yield spreads) rather than noise.

**Acceptance Criteria:**

**Given** the Random Forest model has completed training
**When** the model artifacts are accessed
**Then** it programmatically extracts the ordered mathematical feature importances (e.g., Rolling Volatility, Bond Price Momentum, etc.)

**Given** the feature importance data is passed to the presentation layer
**When** the UI renders the visualization
**Then** it displays a Plotly horizontally-oriented Bar Chart
**And** the chart dynamically conforms to the container width (`use_container_width=True`) with UX-DR7 minimal margins for mobile edge-to-edge readability

### Story 2.3: Baseline vs. ML Outcome Comparison View

As a dashboard viewer,
I want to observe the ML model's regime classifications explicitly juxtaposed against the simpler baseline moving-average,
So that I can visually and quickly verify the value added by injecting Machine Learning complexity.

**Acceptance Criteria:**

**Given** both the Baseline MA model and Random Forest model have finalized computations
**When** the dashboard renders Act 2 of the narrative
**Then** it explicitly displays a side-by-side or stacked visual comparison (e.g., dual metric cards or a comparative plot) of both model outputs across identical time periods
**And** any numerical "deltas" correctly display improved accuracy or divergence using universal financial up/down indicator logic native to `st.metric`

## Epic 3: Explainable AI Risk Attribution (The XAI Reveal)

Users can easily unpack the Machine Learning's specific daily decision-making process through an intuitive, full-width "Hero" Waterfall chart explaining exactly why today's risk regime was chosen.

### Story 3.1: Daily XAI Risk Waterfall Visualization

As an evaluator reviewing the complex Random Forest model,
I want to view a familiar Waterfall chart that cleanly breaks down exactly which quantitative features shifted the model into the current day's risk regime,
So that I can directly trust the model's intelligence and verify it is not acting as an unexplainable "black box."

**Acceptance Criteria:**

**Given** the Random Forest model has executed its prediction for the most recent day in the dataset
**When** the risk attribution logic runs
**Then** it successfully extracts the directional contributions of each individual feature (e.g., how much volatility added or detracted from the final risk classification)

**Given** the dashboard renders "Act 3" of the scrolling narrative
**When** the XAI visualization is displayed
**Then** it utilizes the `go.Waterfall` Plotly object as the project's "Hero Component"
**And** it dynamically claims 100% of the horizontal screen container, rather than being squeezed into vertical columns
**And** it applies dynamic coloring perfectly matching the UX color tokens (e.g., Forest Green for risk-reducing variables, Crimson for risk-increasing variables, Slate Blue for the total benchmark)

**Given** the user views the rendered Waterfall chart
**When** they hover their mouse or touch over an individual bar on the chart
**Then** an exact numerical breakdown clearly states the weight that variable played in the daily decision

## Epic 4: Strategy Benchmarking & Outcomes

Users can validate the investment thesis by mapping regimes to asset allocations, then comparing the final financial returns of the ML model, the baseline, and standard market benchmarks.

### Story 4.1: Financial Allocation & Benchmarking Engine

As a quantitative modeler,
I want to programmatically map theoretical risk regimes into executable portfolio allocations and calculate their historical returns alongside traditional benchmarks,
So that I can mathematically prove whether the Machine Learning model actually generated better financial outcomes than simple rule-based investing.

**Acceptance Criteria:**

**Given** the array of risk classifications (Low, Medium, High) from both models is complete
**When** the allocation mapping logic fires within the `domain/` layer
**Then** it rigidly maps "Low Risk" to an equities-heavy portfolio configuration, "Medium Risk" to a balanced configuration, and "High Risk" to a defensive allocation weighting
**And** it calculates the cumulative portfolio returns for those dynamic weights over the life of the testing dataset.

**Given** the dynamic model returns are calculated
**When** the benchmark execution runs
**Then** it successfully calculates parallel historical returns for a standard "60/40 Stock-Bond" portolio and a pure "100% S&P 500 Buy-and-Hold" strategy over the exact same time period for comparison

### Story 4.2: Final Outcomes Documentation Board

As an evaluator finishing my review of the application,
I want to see a clear, un-styled, purely data-driven matrix comparing all strategies side-by-side,
So that I can quickly extract the final bottom-line numbers without hunting through complex tooltips.

**Acceptance Criteria:**

**Given** the `service_layer` has orchestrated all models and returned the final benchmarking statistics (e.g. Cumulative Return, Max Drawdown, etc.) for all four strategy variants (ML, Baseline, 60/40, SP500)
**When** the UI renders the final chapter of the vertical scroll
**Then** it displays a highly accessible, stark data matrix summarizing the outcomes

**Given** the final matrix is rendering
**When** the user attempts to evaluate the data
**Then** the matrix utilizes Streamlit's native `st.dataframe` component exactly per UX-DR8, ensuring high legibility and standard tabular contrasts without requiring custom CSS or dense chart interaction mapping
