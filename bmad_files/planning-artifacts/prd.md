---
stepsCompleted: [step-01-init, step-02-discovery, step-02b-vision, step-02c-executive-summary, step-03-success, step-04-journeys, step-05-domain, step-06-innovation, step-07-project-type, step-08-scoping, step-09-functional, step-10-nonfunctional, step-11-polish]
inputDocuments:
  - docs/green-rock-initial-prd.md
  - bmad_files/brainstorming/brainstorming-session-2026-03-24-1647.md
  - docs/meetings.md
workflowType: 'prd'
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 1
  projectDocs: 2
classification:
  projectType: web_app
  domain: fintech
  complexity: high
  projectContext: greenfield
lastEdited: '2026-03-30'
editHistory:
  - date: '2026-03-30'
    changes: 'Removed implementation leakage, rewrote NFRs for measurability, added Fintech compliance sections.'
---

# Product Requirements Document - green-rock

**Author:** Andrey
**Date:** 2026-03-26

## Executive Summary

"Does machine learning actually beat simple rules for market regime detection?" Green-rock answers this with a backtested, side-by-side comparison. Unlike typical "predict stock prices with ML" projects, green-rock focuses on risk regime classification — a fundamentally different and more institutionally relevant problem.

The system classifies current market risk regimes (Low / Medium / High) using a Random Forest model trained on ETF returns, rolling volatility, and yield curve data — then compares its performance against a moving-average crossover baseline. Both strategies are benchmarked against a classic 60/40 stock-bond split and S&P 500 buy-and-hold. Every classification is traceable to the features that drove it. The result — whether ML outperforms or not — is documented transparently, because the finding itself is the value.

The project serves a dual purpose: as a standalone demonstration of how institutional teams evaluate trading models — baseline comparison, benchmark validation, and explainability — and as a hands-on learning vehicle for building real-world skills end-to-end — from data pipelines to model validation to interactive dashboards. The process of building it mirrors the day-to-day work of a quantitative analyst — making the builder job-ready, not just interview-ready.

The system is deliberately scoped to three ETFs — SPY (equities), TLT (bonds), GLD (gold) — representing the core asset classes that shift during regime changes. Rigor and interpretability are prioritized over complexity.

### What Makes This Special

The honest framing — baseline vs. ML, benchmarked against real portfolios — mirrors how institutional teams evaluate models internally. Rather than presenting a black box, the system prioritizes transparency at every layer. The centerpiece visualizations are an Explainable AI (XAI) Risk Attribution Waterfall chart and a feature importance chart that answer "WHY does the model classify this regime?" This signals awareness of explainable AI — the dominant concern in institutional finance today. Most portfolio projects demonstrate a model. This one demonstrates a **scientific process**: hypothesis, comparison, benchmark, and clear visual explanation suitable for cold-emailing non-technical PMs.

### Elevator Pitch

> "I built a system that uses Random Forest to classify market risk regimes — low, medium, high — and dynamically shifts ETF allocation between equities, bonds, and gold. I compared it against a simple moving-average baseline and benchmarked both against 60/40 buy-and-hold. The interesting finding was that the ML model anticipated the 2020 crash faster than the baseline."

## Project Classification

| Attribute | Value |
|-----------|-------|
| **Project Type** | Web application (Streamlit dashboard with Python data pipeline backend) |
| **Domain** | Quantitative finance — investment management |
| **Approach** | Deliberate simplicity with institutional rigor |
| **Project Context** | Greenfield — new build from scratch |
| **Estimated Effort** | ~60 hours over 4 weeks at 15 hrs/week |

## Success Criteria

### User Success

- **Confidence test:** After completing the project, you can explain the full pipeline — from data sources to regime classification to allocation logic — without looking at notes
- **Interview readiness:** You can answer "walk me through your project" in 2 minutes, covering the scientific question, methodology, and findings
- **Domain fluency:** You understand WHY you chose these data inputs, WHY regime classification (not price prediction), and WHY explainability matters to institutional firms
- **"Aha" moment:** When an interviewer asks "what did you learn?" you have a genuine, specific answer — not a rehearsed one

### Business Success

- **Career positioning:** A completed project on GitHub that demonstrates analytical thinking in quantitative finance — ready for when the right opportunity comes
- **Narrative ownership:** You can tell the story of this project as real-world applicable work, not an academic exercise
- **No deadline pressure:** Success is measured by quality of understanding, not speed of delivery. Weeks 1-4 timeline from brainstorming is a guide, not a deadline

### Technical Success

- **It runs:** The dashboard loads, data flows, models classify, charts display — a working demo that never breaks during a live showing (CSV fallback ensures this)
- **It's simple:** Code is clean and understandable — not over-engineered. You can explain every piece of it. If a section feels too complex, simplify it
- **It's honest:** Results are whatever the data shows. If ML doesn't beat the baseline, that's documented as a finding, not hidden as a failure

### Measurable Outcomes

| Outcome | Measure | Priority |
|---------|---------|----------|
| Can explain the full pipeline verbally | 2-minute walkthrough without notes | 🔴 Must |
| Working demo with no crashes | Dashboard loads + charts render from CSV fallback | 🔴 Must |
| Understands regime classification vs price prediction | Can articulate the difference and why it matters | 🔴 Must |
| Feature importance chart renders | Shows which inputs drive regime detection | 🔴 Must |
| Can answer "what did you learn?" | Has 3 genuine, specific takeaways | 🟡 Should |
| Baseline vs ML comparison visible | Side-by-side view in dashboard | 🟡 Should |
| Code is simple enough to explain line-by-line | No "black box" sections you can't walk through | 🟡 Should |

*Product scope details — including MVP feature set, phased roadmap, and risk mitigation — are consolidated in the [Project Scoping & Phased Development](#project-scoping--phased-development) section below.*

## User Journeys

### Journey 1: Andrey — Exploring Results Through the Dashboard (Primary User, Success Path)

**Opening Scene:** Andrey has just finished building the data pipeline and models. He opens the Streamlit dashboard for the first time with real data loaded. He's curious but uncertain — *did this actually work?*

**Rising Action:** The regime timeline loads — green, yellow, and red bands stretched across a price chart. He scrolls through time and sees the model flagged March 2020 as "High Risk" — right when COVID crashed the market. *"It caught that."* He switches to the feature importance chart and sees that rolling volatility spiked as the top driver during that period. He starts to understand WHY the model made its call.

**Climax:** He clicks to the model comparison view. The MA Crossover baseline also caught the COVID crash — but 3 days later. The Random Forest caught it earlier because it weighted correlation breakdown alongside volatility. For the first time, he can articulate *exactly* why ML added value in this specific case. He feels something click — this isn't abstract anymore.

**Resolution:** Andrey can now explain the pipeline, the models, and the specific moments where they diverge — with real data examples. He has a story, not just a project. *He's ready to talk about this confidently.*

**Requirements revealed:** Regime timeline visualization, feature importance chart, model comparison view, date-range navigation, clear labeling of regime periods.

---

### Journey 2: Andrey — Data Doesn't Load (Primary User, Edge Case)

**Opening Scene:** Andrey opens the dashboard on a Saturday to practice his demo walkthrough. The external market data API is down for maintenance. The page shows an error where the charts should be.

**Rising Action:** The system detects the API failure and automatically falls back to the static snapshot. A small notice appears: *"Using cached data (last updated: YYYY-MM-DD)."* All charts render normally from the static fallback.

**Climax:** Everything works. The demo is intact. Andrey realizes the CSV fallback isn't just a backup — it's what makes this demo reliable.

**Resolution:** He practices his full walkthrough without interruption. During the actual interview, if anything goes wrong with live data, the CSV fallback catches it silently.

**Requirements revealed:** CSV fallback mechanism, graceful error handling, fallback notification, data source indicator.

---

### Journey 3: The Interviewer — 5-Minute Demo (Demo Viewer)

**Opening Scene:** A portfolio manager at an asset management firm opens a link Andrey shared. The Streamlit dashboard loads. The interviewer has 5 minutes between meetings and is scanning quickly — *"Is this another toy project?"*

**Rising Action:** The first thing they see is a regime timeline — colored bands over a familiar price chart. They recognize the COVID crash, the 2022 rate hike period. *"Okay, this uses real data."* Next, they see an Explainable AI (XAI) Risk Attribution Waterfall chart detailing exactly why the model shifted regimes today. *"This person understands how to unpack an ML model for a non-technical PM."* They notice the feature importance chart next — rolling volatility and yield curve spread are the top drivers.

**Climax:** The model comparison view shows both the simple baseline and the Random Forest side by side. The interviewer sees that both caught major events, but the ML model caught some earlier. More importantly, the interviewer thinks: *"This person didn't just build a model — they asked whether it was worth building, and made its decisions completely transparent."* That's the question institutional teams actually ask internally.

**Resolution:** The interviewer remembers two things: (1) the honest "does ML beat rules?" framing, and (2) the feature importance transparency. They add a note: *"Invite for second round — shows analytical rigor, not just coding."*

**Requirements revealed:** Fast initial load, clear visual hierarchy (regime timeline first), intuitive navigation between views, no login/setup required, works from a shared link.

---

### Journey 4: GitHub Visitor — Clone and Run (Self-Service User)

**Opening Scene:** A technical recruiter or peer finds the project on GitHub. They see the README, skim the architecture, and want to try it. They clone the repo.

**Rising Action:** They run `pip install -r requirements.txt` and then `streamlit run app.py`. The dashboard loads using the included CSV data — no API keys needed, no setup friction.

**Climax:** It works on the first try. They see the same charts Andrey showed in his interview. The code structure is clean enough to follow.

**Resolution:** The visitor thinks: *"This person builds things that actually run."* The project earns a GitHub star and maybe a follow-up question.

**Requirements revealed:** Clear README with setup instructions, requirements.txt, single-command startup, CSV data included in repo, no API key requirements for first run.

### Journey Requirements Summary

| Capability | Revealed By Journey | Priority |
|---|---|---|
| Regime timeline visualization (color-coded) | J1, J3 | 🔴 Must |
| XAI Risk Attribution Waterfall chart | J3 | 🔴 Must |
| Feature importance chart | J1, J3 | 🔴 Must |
| Model comparison view (baseline vs RF) | J1, J3 | 🔴 Must |
| CSV fallback with graceful error handling | J2, J4 | 🔴 Must |
| Fast initial dashboard load | J3 | 🔴 Must |
| Clear visual hierarchy (what to see first) | J3 | 🟡 Should |
| No-setup first run (CSV included, no API keys) | J4 | 🟡 Should |
| README with setup instructions | J4 | 🟡 Should |
| Data source indicator (live vs cached) | J2 | 🟢 Nice |
| Date-range navigation | J1 | 🟢 Nice |

## Domain-Specific Requirements

### Data Integrity

- **Price data validation:** Verify no missing dates, no zero/negative prices, no duplicate entries in yfinance data before feeding into models
- **FRED data alignment:** Yield curve data (10Y-2Y) must be aligned to the same trading dates as ETF price data — handle weekends/holidays consistently
- **CSV snapshot versioning:** When saving CSV fallback, include the date range and download timestamp so results are traceable

### Reproducibility

- **Random seed control:** Set explicit random seeds for Random Forest training so results are identical across runs
- **Dependency pinning:** Pin all Python package versions in requirements.txt to prevent silent behavior changes
- **CSV fallback as ground truth:** The included CSV snapshot serves as the reproducible baseline — any demo or presentation should run against this fixed dataset

### Backtesting Integrity

- **No forward-looking bias:** The model must only train on data available BEFORE the prediction period. Train/test split must respect time ordering (no random shuffle of time-series data)
- **Clear train/test boundaries:** Document where the training period ends and the test period begins — make this visible in the dashboard

### Data Licensing

- **yfinance:** Free for personal and educational use (Yahoo Finance terms of service)
- **FRED:** Public U.S. government data, freely available for any use (Federal Reserve Economic Data)
- **No restrictions** on using either source for a portfolio project

### Institutional Control & Compliance (Theoretical MVP Level)

- **Compliance Matrix:** System must theoretically align with internal audit standards by logging every model configuration change and data extraction timestamp to a read-only audit file
- **Security Architecture:** System must not expose raw external API keys in client-side code, relying exclusively on secure server-side environment variables
- **Audit Requirements:** All regime classification shifts must be exportable alongside the exact feature weights that drove the decision at that timestamp to satisfy compliance review
- **Fraud Prevention:** System must employ immutable data ingestion pipelines where raw input data (prices, yield curves) cannot be manually overwritten or edited prior to model scoring

## Web Application Specific Requirements

### Project-Type Overview

Green-rock is a **Streamlit-based single-page dashboard** with a Python data pipeline backend. Unlike a traditional web app, the UI framework (Streamlit) handles routing, layout, and interactivity — the focus is on data visualization and analytical output rather than complex frontend engineering.

### Deployment Strategy

| Mode | Purpose | Technology |
|------|---------|------------|
| **Local** | Live interview demos, development | `streamlit run app.py` on laptop |
| **Streamlit Cloud** | Async sharing via URL, recruiter review | Free tier deployment from GitHub repo |

- Streamlit Cloud deploys directly from the GitHub repo — no separate CI/CD needed
- CSV fallback ensures the deployed version works without API rate limits or connectivity issues
- Both modes must produce identical visual output

### Browser Compatibility

- **Target:** Modern browsers (Chrome, Firefox, Safari)
- **Primary demo browser:** Whichever Andrey uses during interviews (likely Chrome)
- **No IE/Edge legacy support needed**
- Streamlit handles cross-browser compatibility natively

*Performance targets are defined in the [Non-Functional Requirements](#non-functional-requirements) section (NFR1–NFR4).*

### Implementation Considerations

- **No SEO required** — not a public-facing discovery product
- **No authentication** — open access, no login
- **Basic mobile responsiveness** — dashboard must render legibly on mobile devices so the waterfall chart and key visualizations can be viewed via cold email links on phones. Streamlit handles basic responsive layout natively.
- **Streamlit handles accessibility basics** — no additional a11y work required for MVP

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-solving MVP — prove the scientific question ("Does ML beat simple rules?") can be answered with real data, visualized clearly, and explained confidently.

**Scoping Principle:** Breadth over depth. All 7 build steps completed at a basic working level. A complete but simple demo is more impressive than a half-finished polished one.

**Resource Requirements:** Solo developer, ~15 hrs/week, ~60 hours total. Coding is a learning curve — expect some steps to take longer than estimated. No hard deadline.

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**
- ✅ J1: Builder explores results through dashboard
- ✅ J2: Data doesn't load → CSV fallback
- ✅ J3: Interviewer views 5-minute demo
- ✅ J4: GitHub visitor clones and runs (partial — README may be minimal)

**Must-Have Capabilities (8-Step Build Sequence):**

| Step | Capability | "Good Enough" Bar |
|------|-----------|-------------------|
| 1 | Data pipeline (yfinance + FRED + CSV) | Data loads into a clean dataframe without errors |
| 2 | MA Crossover baseline model | Classifies regimes, output matches expected format |
| 3 | Random Forest classifier | Trains and classifies, produces feature importances |
| 4 | Benchmark backtest (vs 60/40, S&P) | Returns comparison table/numbers |
| 5 | Streamlit dashboard | Loads and displays all views on a single page |
| 6 | Feature importance chart | Bar chart renders with correct feature names |
| 7 | Model comparison view | Side-by-side output visible |
| 8 | XAI Risk Attribution Waterfall chart | Visualizes specific metric contributions to today's risk score |

*After step 4, you have a complete demoable engine. Steps 5-8 wrap it in presentation.*

### Post-MVP Features

**Phase 2 (Polish & Rigor):**
- Walk-forward validation (backtesting rigor)
- Risk-adjusted metrics (Sharpe, Sortino, MaxDD)
- Model confidence score gauge
- README with architecture diagram
- "3 Things I Learned" findings document
- Visual polish on dashboard (colors, layout, branding)

**Phase 3 (Expansion):**
- Multi-asset expansion beyond 3 ETFs
- Additional ML models (gradient boosting, etc.)
- Live data refresh (not just historical)
- Portfolio optimization layer (mean-variance)

### Risk Mitigation Strategy

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| **Coding takes longer than expected** | 🔴 High | Keep each step at "good enough" bar. Don't polish until all 7 complete. Use AI coding assistants for guidance. |
| **yfinance/FRED API unavailable** | 🟡 Medium | CSV fallback built into step 1. Demo never depends on live API. |
| **Random Forest doesn't beat baseline** | 🟢 Low risk (it's fine) | Document honestly. "I tested it" IS the story. The finding is the value. |
| **Streamlit learning curve** | 🟡 Medium | Streamlit is simpler than most frameworks. Start with minimal layout, add charts one at a time. |
| **Scope creep** | 🟡 Medium | Apply 3-pillar filter: "Does it strengthen AI detection, model comparison, or benchmarked results?" If no → v2. |

## Functional Requirements

### Data Pipeline

- **FR1:** System can fetch daily price data for SPY, TLT, and GLD from an external market data provider
- **FR2:** System can fetch 10Y-2Y yield curve spread data from an external economic data provider
- **FR3:** System can calculate rolling volatility from price data
- **FR4:** System can fall back to a bundled static data snapshot when external data calls fail
- **FR5:** System can display a notification indicating whether live or cached data is in use
- **FR6:** System can validate fetched data for missing dates, zero/negative prices, and duplicates before processing
- **FR7:** System can produce a normalized, date-aligned data structure combining all data sources

### Risk Regime Classification

- **FR8:** System can classify market risk regimes as Low, Medium, or High using a moving-average crossover baseline model
- **FR9:** System can classify market risk regimes as Low, Medium, or High using a trained Random Forest classifier
- **FR10:** System can train the classifier deterministically to ensure reproducible results across runs
- **FR11:** System can split training and test data respecting time ordering (no future data leakage)

### Allocation Logic

- **FR12:** System can map risk regimes to 3-bucket allocation weights (equities-heavy, balanced, defensive)

### Benchmarking

- **FR13:** System can calculate portfolio returns for both models' allocation strategies
- **FR14:** System can calculate returns for a 60/40 stock-bond benchmark
- **FR15:** System can calculate returns for an S&P 500 buy-and-hold benchmark
- **FR16:** System can display comparison of all strategies' performance

### Visualization & Dashboard

- **FR17:** User can view a regime timeline chart with color-coded bands (green/yellow/red) overlaid on price data
- **FR18:** User can view an Explainable AI (XAI) Risk Attribution Waterfall chart showing why the model shifted regimes today
- **FR19:** User can view a feature importance bar chart showing which inputs drive Random Forest classifications overall
- **FR20:** User can view a model comparison showing baseline vs. Random Forest regime outputs side-by-side
- **FR21:** User can view benchmark performance comparison across all strategies
- **FR22:** User can access all views from a single web-based interactive dashboard page

### Deployment & Accessibility

- **FR23:** User can run the dashboard locally via a single startup command
- **FR24:** System can be deployed to a cloud hosting environment directly from the version control repository
- **FR25:** User can run the project using only bundled static data (no API keys required for first run)
- **FR26:** System provides a one-step installer for all required dependencies

## Non-Functional Requirements

### Performance

- **NFR1:** [Load Time] Dashboard initial load time must be < 5 seconds as measured by automated performance testing when using static fallback data to ensure a smooth demo experience
- **NFR2:** [Load Time] Dashboard initial load time must be < 10 seconds as measured by automated performance testing when fetching live external data to prevent user abandonment
- **NFR3:** [Render Performance] All chart views must render in < 500ms as measured by browser profiling tools after data is loaded to ensure fluent navigation between views
- **NFR4:** [Training Performance] Model training must complete in < 30 seconds as measured by internal execution timers on a standard 4-core machine to allow rapid iterative backtesting

### Integration Reliability

- **NFR5:** [Fallback Reliability] System must switch to static fallback data within 2 seconds as measured by fault-injection testing when primary market data APIs return 4xx/5xx errors or timeout
- **NFR6:** [Fallback Reliability] System must switch to static fallback data within 2 seconds as measured by fault-injection testing when economic APIs return 4xx/5xx errors or timeout
- **NFR7:** [Status Clarity] System must display a visible data source indicator on the primary UI as measured by visual inspection during usability testing

### Code Maintainability

- **NFR8:** [Modularity] Code must be organized into decoupled modules (data ingestion, modeling, visualization) as measured by a dependency graph analyzer to ensure independent maintainability
- **NFR9:** [Documentation] All financial logic functions must include docstrings explaining the mathematical reasoning as measured by code review and documentation coverage tools
- **NFR10:** [Complexity] No individual function may exceed a cyclomatic complexity of 10 as measured by static analysis tools to ensure logic remains simple enough to explain during an interview
- **NFR11:** [Reproduculity] All project package dependencies must be strictly version-pinned in a lockfile mechanism as measured by CI/CD dependency scanning to prevent silent behavior changes across runs
