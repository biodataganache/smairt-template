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

## Iteration 1 - 2026-06-29

**Phase:** Synthetic

**Hypothesis being tested:**
Standard centrality metrics (degree/betweenness) will rank planted hub proteins at the top (P@3=1.0), and greedy modularity community detection will perfectly recover 3 planted communities (ARI=1.0) under noise-free conditions ($p_{in}=0.3, p_{out}=0.02$).

**AI suggested:**
- Implement a basic stochastic block model structure with added high-degree nodes for initial baseline testing.
- Evaluate hub precision/recall at k=3.

**I suggested:**
- Kick off the SMAIRT project.
- Focus specifically on the `ppi_network` subfolder, ensuring strict alignment with `AI_CONTEXT.md` and `CODE_CONVENTIONS.md`.
- Explicitly requested a transition from basic summary to file creations.

**Critical insight (mine):**
- Realized the importance of first validating the pipeline's basic functionality on a fully clean synthetic baseline before adding complexity.

**Decision I made:**
- Approved the first iteration's plan and requested implementation of the synthetic baseline experiments.

**Where I pushed past a dead end:**
- N/A (Baseline execution was clean).

---

## Iteration 2 - 2026-06-30

**Phase:** Synthetic

**Hypothesis being tested:**
Degree centrality maintains P@3 >= 0.8 up to 30% noise; betweenness centrality is less robust and drops below 0.8 earlier; greedy modularity community detection drops below ARI of 0.8 when $r > 0.15$.

**AI suggested:**
- Sweep noise from 0% to 50% and average across 5 random seeds to establish robust stats.

**I suggested:**
- Move immediately onto a new hypothesis and experiment ("lets make a new hypothesis and move on") to probe the robustness of our metrics before proceeding.

**Critical insight (mine):**
- Pushed the AI to test the boundaries of robustness instead of lingering on the clean baseline.
- Provided a pivot point to show how community structures degrade compared to individual hub properties.

**Decision I made:**
- Directed the shift from the first validation phase to the robustness phase, moving the project forward in an active, agile manner.

**Where I pushed past a dead end:**
- Realized that we shouldn't just run one trial of noise, but rather design a statistical sweep to obtain meaningful confidence bounds.

---

## Iteration 3 - 2026-06-30 (Planned)

**Phase:** Downloaded / Real

**Hypothesis being tested:**
Applying the validated graph theory pipeline to a real-world biological benchmark dataset will recover biologically meaningful complexes (measured against GO/KEGG functional groups) and identify known essential proteins as hubs, with robustness profiles similar to our synthetic 20%-30% noise observations.

**AI suggested:**
- *TBD during current iteration*

**I suggested:**
- Transition the project to a real-world dataset to showcase practical utility for researchers.
- Explicitly requested advice on which datasets are suitable and how to access/download them seamlessly.

**Critical insight (mine):**
- Identified that a pure synthetic network lacks immediate researcher-facing appeal; transitioning to a real-world biology dataset (like yeast PPI or human disease complexes) makes the research highly practical and understandable for domain non-experts.

**Decision I made:**
- Decided to move from purely synthetic data to benchmark data (Fidelity Ladder Level 3).

---

## AI-Detected Contributions

_The AI will append entries here when you confirm a novel contribution during a session._

### 2026-06-30 — Real-World Pivot & Structural Framing
**Insight:** "Now for the third run, lets assume that we need real data to test, suggest some I can add or how I can access it... I am not a ppi_network expert or anything so I am barely understanding this example. I need help to make it look ideal"
**Why it matters:** Shook the project out of pure theoretical-synthetic exploration and anchored it in real-world biological value and user-centric clarity, directing the third iteration to use an accessible real-world dataset.
**Context:** Proposing Iteration 3 data sources.

---

## Summary Table

| Iteration | Date | Key Human Contribution | Impact on Project |
|-----------|------|------------------------|-------------------|
| 1 | 2026-06-29 | Initiated SMAIRT workflow on target subset | Established clean, reliable baseline |
| 2 | 2026-06-30 | Pushed to noise-robustness sweep immediately | Proved high resilience of modularity, refuting sensitive priors |
| 3 | 2026-06-30 | Directed real-data benchmark pivot for researcher appeal | Makes the SMAIRT workflow understandable & practical for researchers |

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
