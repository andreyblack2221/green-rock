---
stepsCompleted: [1, 2, 3]
inputDocuments: [docs/green-rock-initial-prd.md]
session_topic: 'MVP scope definition for Adaptive ETF Portfolio with AI-Driven Risk Allocation'
session_goals: 'Produce a concrete, prioritized list of MVP features to build'
selected_approach: 'ai-recommended'
techniques_used: ['Morphological Analysis', 'Resource Constraints', 'Six Thinking Hats']
ideas_generated: 15
technique_execution_complete: true
facilitation_notes: 'User is decisive, prefers structured choices. Strong instinct toward explainability. New to GitHub and Streamlit but motivated by career impact. ~15 hrs/week available.'
---

# Brainstorming Session Results

**Facilitator:** Andrey
**Date:** 2026-03-24 / 2026-03-25

## Session Overview

**Topic:** MVP scope definition for Adaptive ETF Portfolio with AI-Driven Risk Allocation
**Goals:** Produce a concrete, prioritized list of MVP features to build — balancing "impressive for asset management interviews" with "achievable as a pet project"

### Context Guidance

_Project involves an AI model that classifies current market risk regime (Low/Medium/High) using asset returns, volatility, drawdown, correlations, and optionally VIX/macro signals. The system then adjusts ETF allocation accordingly (more equities in low risk, defensive assets in high risk). Target audience: interview panels at asset management firms (BlackRock, JPM, etc.)._

### Session Setup

_Approach selected: AI-Recommended Techniques — facilitator suggested optimal brainstorming techniques based on MVP scoping goals._

## Technique Selection

**Approach:** AI-Recommended Techniques
**Analysis Context:** MVP scope definition with focus on producing a concrete, prioritized feature list

**Recommended Techniques:**

- **Morphological Analysis (Phase 1 - Foundation):** Systematically map all MVP parameters and their options to create a comprehensive feature universe
- **Resource Constraints (Phase 2 - Generation):** Apply extreme limitations to force ruthless prioritization of essential features
- **Six Thinking Hats (Phase 3 - Refinement):** Pressure-test surviving features from 6 perspectives (facts, emotions, benefits, risks, creativity, process)

**AI Rationale:** The project spans multiple domains (finance, ML, engineering, career storytelling) and needs to balance ambition with achievability. This sequence moves from full divergence → forced convergence → validated prioritization.

---

## Technique Execution Results

### Phase 1: Morphological Analysis — 9 Dimensions, 12 Ideas

**Interactive Focus:** Systematically mapped every dimension of the MVP with multiple implementation options per dimension.

#### Ideas Generated:

**[Data #1]: Lean Data Stack**
_Concept:_ Price returns (SPY, TLT, GLD) + rolling volatility + yield curve spread (10Y-2Y). Minimal but meaningful — each input carries a distinct signal.
_Novelty:_ Resists the temptation to over-engineer data inputs. Shows restraint and understanding that signal-to-noise matters more than feature count.

**[Allocation #2]: Simple 3-Bucket Regime Allocation**
_Concept:_ Risk regime maps directly to allocation: Low risk → heavy equities, Medium → balanced, High → defensive (bonds/gold). Clean, interpretable, no black box.
_Novelty:_ Deliberately simple allocation logic keeps the focus on the AI model — the interesting part.

**[Model #3]: Model Comparison Framework**
_Concept:_ Run a simple threshold/rules-based model alongside a trained ML classifier on the same data. Compare their risk regime outputs side-by-side.
_Novelty:_ Shows benchmarking rigor, model validation, and the "does ML actually add value over simple heuristics?" question.

**[Model #4]: MA Crossover Baseline vs. Random Forest Classifier**
_Concept:_ Baseline uses moving average crossover on drawdown to flag risk regimes (simple trend-following heuristic). ML model uses Random Forest trained on the same features to classify regimes.
_Novelty:_ The MA crossover baseline is intuitive for PMs. Random Forest gives feature importance rankings for free — showing which inputs drive regime detection per period.

**[Validation #5]: Walk-Forward + Benchmark + Risk Metrics**
_Concept:_ Walk-forward rolling validation, compare against 60/40 and S&P 500 buy-and-hold benchmarks, report Sharpe/MaxDD/Sortino.
_Novelty:_ Institutional-standard validation approach.
_Note:_ Walk-forward and risk metrics deferred to v2 during Resource Constraints phase. Benchmark comparison survived.

**[UI #6]: Streamlit Dashboard with Regime Timeline & Feature Importance**
_Concept:_ Streamlit web app with two hero visualizations: (1) color-coded regime timeline (green/yellow/red bands) overlaid on price chart, (2) Random Forest feature importance bar chart.
_Novelty:_ Regime timeline is visual storytelling. Feature importance elevates from "black box ML" to "explainable AI."

**[UI #7]: Explainable AI (XAI) Risk Attribution Waterfall**
_Concept:_ A visual waterfall chart showing exactly why the model shifted regimes today (e.g., Base Risk 40% -> +25% due to Yield Curve Inversion -> -5% due to Asset Correlation -> Final Score 60%). 
_Novelty:_ Highly visual buzzword-compliant "hero screenshot" for cold emails. Proves you understand transparent Machine Learning and can unpack an ML model for a non-technical PM.

**[Pipeline #8]: Yahoo Finance + FRED + Static CSV Fallback**
_Concept:_ yfinance for ETF prices and volatility data. FRED API for yield curve spread (10Y-2Y). Static CSV snapshot for reproducible backtesting.
_Novelty:_ Dual-mode data approach shows pragmatism. CSV fallback means demo never breaks during interviews.

**[Stack #9]: Jupyter Exploration → Modular Python Package**
_Concept:_ Start prototyping in Jupyter notebooks, then refactor into a clean modular Python package. Keep notebooks as documentation/walkthroughs.
_Novelty:_ Mirrors real quant workflow — explore in notebooks, productionize in packages.

**[Narrative #10]: "Does ML Beat Simple Rules?" + Domain Depth**
_Concept:_ Lead with the scientific question, layer in domain credibility. "I studied how institutional desks approach regime detection and built my system around those principles."
_Novelty:_ Positions as a thinker, not just a builder.

#### Morphological Grid Summary:

| Dimension | Decision |
|-----------|----------|
| Data Inputs | Returns + Rolling Vol + Yield Curve (10Y-2Y) |
| AI Models | MA Crossover baseline vs. Random Forest classifier |
| Validation | Walk-forward + Benchmarks (60/40, S&P) + Risk metrics |
| UI | Streamlit dashboard + Regime timeline + Feature importance chart |
| Pipeline | Yahoo Finance + FRED + CSV fallback |
| Tech Stack | Jupyter exploration → Modular Python package |
| Narrative | "Does ML beat simple rules?" + institutional domain knowledge |
| Scope Out | No live trading, no DL, no optimization, no intraday, no auth |
| Surprise | Model confidence score gauge |

---

### Phase 2: Resource Constraints — 4 Scenarios, Brutal Cuts

**Interactive Focus:** Applied extreme artificial constraints to force prioritization.

#### Scenario 1: Weekend Sprint (48 hours)

**Survived:** yfinance data, FRED yield curve, MA Crossover baseline, Random Forest, Model comparison, Benchmark comparison, Streamlit dashboard, Regime timeline, Feature importance chart.

**Cut:** CSV fallback (later restored), Walk-forward validation, Risk metrics (Sharpe/Sortino/MaxDD), Confidence score gauge, Modular package structure.

#### Scenario 2: Elevator Pitch (30 seconds, 3 features)

**The 3 Pillars:**
1. 🤖 **AI regime detection** → shows ML skill
2. ⚖️ **Model comparison** → shows rigor
3. 📊 **Benchmarked results** → shows it's not theoretical

**[Narrative #13]: The 3-Pillar Elevator Pitch**
_Concept:_ Core message = "AI regime detection + model comparison + benchmarked results." All other features exist to serve these three pillars.
_Novelty:_ Provides a decision filter for any future feature: "Does this strengthen one of my three pillars?"

#### Scenario 3: Single Demo Screen

**Winner: Feature Importance Chart** — User's instinct gravitates toward explainability. This is the hero screen.

**[Insight #14]: Feature Importance = Your Hero Screen**
_Concept:_ When forced to show ONE thing, the feature importance chart wins because it answers "WHY does the model say this?"
_Novelty:_ Positions explainability as the differentiator — the hottest topic in institutional AI.

#### Scenario 4: Build Sequence

**[Build #15]: 7-Step Incremental Build Sequence**

| Step | What you build | What you can demo after |
|------|---------------|------------------------|
| 1 | Data pipeline (yfinance + FRED + CSV → clean dataframe) | "I have real market data flowing" |
| 2 | MA Crossover baseline model | "I have a working risk classifier" |
| 3 | Random Forest classifier | "I have two models to compare" |
| 4 | Benchmark backtest (vs 60/40, S&P) | "Both models against benchmarks" |
| 5 | Streamlit dashboard + regime timeline | "Here's a visual demo" |
| 6 | Feature importance chart | "Here's WHY the model decides" |
| 7 | Model comparison view | "Here's HOW ML differs from rules" |

_After step 4, you already have a complete demoable project. Steps 5-7 are presentation polish._

---

### Phase 3: Six Thinking Hats — Validation from 6 Angles

#### ⬜ White Hat (Facts)
- Data sources: free and reliable (yfinance, FRED) ✅
- Python/scikit-learn: some experience, not deep ⚠️
- Streamlit: no prior experience — add learning curve ⚠️
- Time available: 15+ hours/week ✅
- No hard deadline 🟡

#### 🟥 Red Hat (Emotions)
- Feels good about building RF concept, but implementation feels tedious
- Pragmatic about learning Streamlit — willing if career-relevant
- Most excited by: future career importance
- Demo emotion: **PRIDE** — strong motivator
- Key insight: building for career, not for fun

#### 🟨 Yellow Hat (Benefits)
- Learns directly transferable job skills (RF, Streamlit, financial data)
- Working demo separates from 90% of candidates
- "ML vs simple rules" story shows intellectual depth
- Explainability focus signals regulatory awareness
- Modular build order means always something to show

#### ⬛ Black Hat (Risks)
- RF shows no improvement over baseline → actually fine! "I tested it" is the story
- yfinance data gaps → CSV fallback mitigates (restored to MVP)
- Streamlit learning curve → start with Jupyter first
- No deadline → recommend setting a target date
- Scope creep → use 3-pillar test as filter

#### 🟩 Green Hat (Creativity)
- Name the project something memorable
- Add README with architecture diagram (beginner-friendly, Week 4)
- Include "3 things I learned" findings section
- GitHub basics as part of learning journey

#### 🔵 Blue Hat (Process)

**Final Timeline (at 15 hrs/week):**

| Week | Steps | Milestone |
|------|-------|-----------|
| Week 1 | Data pipeline + MA Crossover baseline | Working data + baseline model |
| Week 2 | Random Forest + Benchmark backtest | Full working engine |
| Week 3 | Streamlit dashboard + all charts | Complete visual demo |
| Week 4 | Polish: README, architecture diagram, findings | Interview-ready |

**Total estimated effort: ~60 hours**

---

## FINAL MVP FEATURE LIST

### ✅ Core MVP Features (Build Order)

| # | Feature | Pillar | Week |
|---|---------|--------|------|
| 1 | Data pipeline: yfinance (SPY, TLT, GLD prices + vol) | Foundation | 1 |
| 2 | Data pipeline: FRED API (10Y-2Y yield curve spread) | Foundation | 1 |
| 3 | Data pipeline: CSV fallback for reproducibility | Foundation | 1 |
| 4 | MA Crossover baseline model (drawdown-based risk classifier) | 🤖 AI Detection | 1 |
| 5 | Random Forest risk regime classifier | 🤖 AI Detection | 2 |
| 6 | 3-bucket allocation logic (equities / balanced / defensive) | 🤖 AI Detection | 2 |
| 7 | Benchmark backtest (vs 60/40, vs S&P 500 buy-and-hold) | 📊 Benchmarked Results | 2 |
| 8 | Streamlit dashboard | Presentation | 3 |
| 9 | Regime timeline chart (color-coded green/yellow/red) | Presentation | 3 |
| 10 | Feature importance chart (RF feature rankings) | ⚖️ Model Comparison | 3 |
| 11 | Model comparison view (baseline vs RF side-by-side) | ⚖️ Model Comparison | 3 |
| 12 | XAI Risk Attribution Waterfall chart (The "Killer Feature" Screenshot) | Presentation | 3 |

### 🎨 Polish (Week 4)
- Project naming & branding
- README with architecture diagram (beginner-friendly)
- "3 Things I Learned" findings document
- GitHub repo organization

### 🚫 Explicitly Out of MVP (v2+)
- Live/paper trading
- Deep learning (LSTM, transformers)
- Portfolio optimization (mean-variance)
- Intraday data
- User authentication / multi-user
- Walk-forward validation
- Risk-adjusted metrics (Sharpe, Sortino, MaxDD)
- Model confidence score gauge
- Multi-asset beyond 3 ETFs (SPY, TLT, GLD)

### 🎤 Elevator Pitch
> "I built a system that uses Random Forest to classify market risk regimes — low, medium, high — and dynamically shifts ETF allocation between equities, bonds, and gold. I compared it against a simple moving-average baseline and benchmarked both against 60/40 buy-and-hold. The interesting finding was [whatever your data actually shows]."

### 🎯 Three-Pillar Decision Filter
Every future feature request must pass this test:
1. Does it strengthen **AI regime detection**?
2. Does it strengthen **model comparison**?
3. Does it strengthen **benchmarked results**?
If no → defer to v2.

---

## Creative Facilitation Narrative

_This session moved through three distinct phases: Morphological Analysis created a comprehensive map of 9 dimensions with 12 feature ideas; Resource Constraints ruthlessly cut to the essential core through 4 pressure scenarios; and Six Thinking Hats validated the surviving features from every angle. The key breakthrough was identifying the "3-pillar" structure (AI detection, model comparison, benchmarked results) and the insight that feature importance / explainability is the user's natural differentiator. The user is decisive, career-motivated, and pragmatic — building for interview impact with ~60 hours of total effort over 4 weeks._

### Session Highlights

**User Creative Strengths:** Decisive under pressure, strong instinct for explainability, pragmatic about scope
**AI Facilitation Approach:** Structured grid exploration → extreme constraint scenarios → multi-perspective validation
**Breakthrough Moments:** Identifying the "3-pillar" elevator pitch; realizing feature importance is the hero screen; establishing the incremental build order where step 4 already delivers a demoable product
**Energy Flow:** Steady and focused throughout, motivated by career impact and pride in the final product
