# Intellectual Contribution Log

Track where YOU made the critical steps vs. where AI generated ideas.

---

## Why This Matters
What you bring to the process is an important thing to track. This is where
the AI moves from being a prompt-driven engine for generating stuff to
a scientific tool that enables exploration of gaps and what will and won't work
for a specific scientific question.
---

## How to Use This File

For each iteration, document:
1. What AI suggested
2. What YOU suggested
3. Where YOU made critical insights—especially at dead ends or turning points
4. Key decisions you made that shaped the direction of the project

---

## Iteration 1 - 2026-07-13

**Phase:** Synthetic

**Hypothesis being tested:**
Single-scenario SIRD validation: with `R0 > 1`, infected should grow to a peak, decline, and preserve `S + I + R + D = N`.

**AI suggested:**
- Implement the first synthetic SIRD scenario using `N=1000`, `I0=1`, `beta=0.3`, `gamma=0.1`, and `mu=0.01`.
- Use `solve_ivp`, `TeeLogger`, a four-curve plot, and an audit trail with hypothesis/log/analysis artifacts.

**I suggested:**
- Start with a single, checkable scenario before writing broader sweeps.
- Treat the conservation check `S + I + R + D = N` as the explicit solver-validation criterion rather than trusting curves by appearance alone.

**Critical insight (mine):**
- Solver credibility depends on invariant checks and non-negativity, not just plausible SIRD curves.

**Decision I made:**
- Require explicit conservation and non-negativity checks before accepting the synthetic baseline.

**Where I pushed past a dead end:**
- Redirected the workflow from plotting-only validation toward assertion-based numerical validation.

---

## Iteration 2 - 2026-07-13

**Phase:** Synthetic

**Hypothesis being tested:**
Sweeping `beta` should reveal the `R0 = 1` growth/fade threshold and show infected peaks growing and shifting with transmission rate.

**AI suggested:**
- Sweep beta values across the theoretical threshold while holding `gamma=0.1` and `mu=0.01` fixed.
- Report peak infected count, peak timing, conservation error, and final recovered/deceased fractions.

**I suggested:**
- The second iteration should explicitly locate the `R0 = 1` threshold separating outbreaks that fade immediately from outbreaks that grow.
- The beta sweep should show infected peak size growing and peak timing shifting.

**Critical insight (mine):**
- The key scientific validation is the threshold behavior, not just the existence of a peak in one baseline scenario.

**Decision I made:**
- Prioritize beta-sweep validation before moving to death-rate or real-data analyses.

**Where I pushed past a dead end:**
- Clarified that a single `R0 > 1` demonstration was insufficient for the project goal.

---

## Iteration 3 - 2026-07-13

**Phase:** Synthetic

**Hypothesis being tested:**
Sweeping `mu` should change the final recovered/deceased split, and lowering `beta` should flatten the curve.

**AI suggested:**
- Sweep `mu` at fixed `beta` and `gamma` to test whether observed final `D/R` matches `mu/gamma`.
- Compare multiple beta values at fixed `mu` to show lower and later infected peaks.

**I suggested:**
- Report final size as fraction recovered versus deceased at long time.
- Discuss the flatten-the-curve interpretation of lowering `beta`.
- Record the key judgment call about which intervention to prioritize and why.

**Critical insight (mine):**
- The scientific reasoning is the intervention-priority judgment, not only the numerical sweep output.

**Decision I made:**
- Prioritize lowering `beta` as the first intervention lever because it directly reduces simultaneous infections and hospital burden.

**Where I pushed past a dead end:**
- Expanded the workflow from numerical validation into interpretable public-health reasoning.

---

## Iteration 4 - 2026-07-13

**Phase:** Downloaded

**Hypothesis being tested:**
A deterministic SIRD model can be fit to a downloaded public COVID-19 time series to estimate effective `beta`, `gamma`, `mu`, and `R0`, but uncertainty and limitations will be substantial.

**AI suggested:**
- Use a reproducible downloaded-data pipeline with cached JHU CSSE COVID-19 data.
- Fit Italy's early COVID-19 active/recovered/deceased curves with bounded least squares and bootstrap `R0` uncertainty.

**I suggested:**
- Proceed to fitting `beta`, `gamma`, and `mu` to a small published outbreak time series.
- Use a downloaded public COVID-19 time series in `data/downloaded`, with a script that fetches data or reads cached data if available.

**Critical insight (mine):**
- Moving to real/public data should preserve reproducibility through caching and provenance, rather than relying on an undocumented manual data extract.

**Decision I made:**
- Use downloaded public COVID-19 data for the next fidelity step.

**Where I pushed past a dead end:**
- Advanced the project from synthetic validation into a real published-data fitting problem while retaining auditability.

---

## AI-Detected Contributions

_The AI will append entries here when you confirm a novel contribution during a session._

### 2026-07-13 — Validation Before Trusting Curves
**Insight:** The user required explicit conservation and non-negativity checks before trusting SIRD curves.
**Why it matters:** This set the numerical credibility standard for the project and prevented visual-only validation.
**Context:** During Iteration 1 solver validation.

### 2026-07-13 — Synthetic Fidelity Ladder Before Real Fitting
**Insight:** The user directed the project to validate one scenario, then sweep `beta`, then sweep `mu`, before fitting real outbreak data.
**Why it matters:** This created a rigorous progression from mechanistic correctness to interpretability before confronting noisy real data.
**Context:** During planning and execution of Iterations 1–3.

### 2026-07-13 — Intervention Judgment as Science
**Insight:** The user emphasized that the key judgment call—such as prioritizing lowering `beta` versus shortening infectious period—is part of the science.
**Why it matters:** This reframes the model from a plotting exercise into a tool for public-health reasoning.
**Context:** During Iteration 3 interpretation.

### 2026-07-13 — Reproducible Downloaded-Data Transition
**Insight:** The user chose a downloaded public COVID-19 time series with caching rather than an undocumented local/manual dataset.
**Why it matters:** This preserved reproducibility and provenance while moving the project beyond synthetic validation.
**Context:** During Iteration 4 real-data fitting.

<!-- Example entry (AI will follow this format):
### [DATE] — [Short Title]
**Insight:** "[User's words or paraphrase]"
**Why it matters:** [Brief explanation of impact on project direction]
**Context:** During [what you were working on]
-->

---

## Summary Table

| Iteration | Date | Key Human Contribution | Impact on Project |
|-----------|------|------------------------|-------------------|
| 1 | 2026-07-13 | Required a single checkable scenario with explicit conservation/non-negativity validation | Established solver credibility standard |
| 2 | 2026-07-13 | Required beta sweep across `R0 = 1` threshold | Demonstrated growth/fade mechanism rather than only one plausible curve |
| 3 | 2026-07-13 | Required final-size death-rate sweep and intervention-priority judgment | Connected model output to public-health interpretation |
| 4 | 2026-07-13 | Chose downloaded public COVID-19 data with caching/provenance | Moved project into reproducible published-data fitting |

---

## Types of Contributions to Track

### Conceptual Contributions
- Novel questions or framings
- Connections between disparate ideas
- Recognizing patterns AI missed

### Methodological Contributions
- Suggesting approaches AI didn't think of
- Deciding which path to pursue at branch points
- Identifying when to pivot

### Interpretive Contributions
- Seeing implications AI missed
- Recognizing when results seem inconsistent or unexpected
- Connecting results to broader context

### Critical Judgment
- Knowing when an approach isn't working
- Recognizing limitations of AI suggestions
- Deciding what is sufficient vs. what needs more work

---

## Reflection Questions

Ask yourself at the end of each iteration:

1. Where did I provide direction that AI wouldn't have come up with?
2. Did I recognize a dead end before AI did?
3. What connections did I make between domains or ideas?
4. Where did I exercise judgment about what to pursue?
5. What would have happened if I had simply accepted AI suggestions without critical evaluation?

---

## Remember

AI excels at regression toward the mean. It may not be giving you anything really
novel in the way of new gaps or innovation. However, it can move you quickly
to the frontier of what's known. Identifying genuine gaps and making
really innovative connections requires human insight. That's what you're tracking here.
