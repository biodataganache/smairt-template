# Final Report — [Project or Study Title]

| Field | Details |
|---|---|
| Research Project | [Project name] |
| Study Scope | [One-sentence scope of the research question, model, dataset, or system studied] |
| Methodological Approach | [Hypothesis-driven computational study / experimental analysis / benchmark validation / other] |
| Generated | [YYYY-MM-DD] |
| Last Updated | [YYYY-MM-DD] |
| Report Status | DRAFT / ACTIVE / UPDATED / FINAL |
| Primary Sources | [background/01_initial_question.md](../background/01_initial_question.md); [ANALYSIS_01.md](ANALYSIS_01.md); [add additional analysis files] |

---

## How to Use This Template

Use this file to create a project-level research synthesis at any major checkpoint. It can be written after one iteration, after a phase transition, before a handoff, before paper drafting, or at the end of the project. Unlike `ANALYSIS_XX.md`, which interprets one experiment or iteration, the final report synthesizes the whole research state so far.

Recommended workflow:

1. Copy this file to `FINAL_REPORT.md` or to a dated version such as `FINAL_REPORT_YYYYMMDD.md`.
2. Read the research audit trail: `background/`, `hypotheses/`, `experiments/`, `results/logs/`, `results/figures/`, `analysis/`, and `prompts/intellectual_contribution.md` where present.
3. Fill every section from evidence in the project files, not from memory.
4. Keep the framing as an actual research report. Do not describe the project as a demo, template exercise, or AI-code-generation example.
5. Mark the report status as `UPDATED` whenever new iterations change the conclusions.

---

## 1. Executive Summary

[Write 2-4 paragraphs summarizing the research question, the main positive findings, the main negative or boundary findings, and the significance of the current evidence.]

---

## 2. Project Question and Study Scope

### Central Question

[State the research question in one clear sentence.]

### Study Scope

[Describe what is included in this report: model, dataset, phase, organism, system, algorithm family, etc.]

### Model, Data, or Experimental Context

[Describe the model, data source, assumptions, and any relevant constants or domain-specific constraints.]

### What This Study Is Designed to Resolve

[Explain the specific uncertainty, gap, or decision this research addresses.]

### What This Study Does Not Resolve

[State boundaries honestly.]

---

## 3. Research Audit Trail

| Iteration | Hypothesis | Script or Method | Log or Evidence | Analysis | Status |
|---|---|---|---|---|---|
| 01 | [Hypothesis file](../hypotheses/HYPOTHESIS_01.md) | [Script or method](../experiments/01_synthetic/script_01_description.py) | [Log or evidence](../results/logs/script_01_*.log) | [ANALYSIS_01.md](ANALYSIS_01.md) | SUPPORTED / REFUTED / PARTIALLY SUPPORTED / INCONCLUSIVE |

---

## 4. Final Results Matrix

| Result Area | Best or Representative Case | Main Quantitative Outcome | Interpretation |
|---|---:|---:|---|
| [Result area] | [Parameters / data subset / method] | [Metric values] | [What the result means] |

---

## 5. Iteration-Level Findings

### Iteration [XX] — [Short Title]

#### Goal

[What was this iteration trying to determine?]

#### Method

[Briefly describe what was run, what inputs were used, and what conditions were tested.]

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| [Metric] | [Expected value or direction] | [Observed value] | Success / Partial / Failed / Inconclusive |

#### Interpretation

[Explain whether the hypothesis was supported, what the result means scientifically, and any boundaries or caveats discovered.]

---

## 6. Cross-Iteration Comparison

| Metric or Decision Point | Iteration 1 | Iteration 2 | Iteration 3 | Current Interpretation |
|---|---:|---:|---:|---|
| [Shared metric] | [Value] | [Value] | [Value] | [Trend or decision] |

---

## 7. Key Scientific Conclusions

1. [Conclusion supported by evidence.]
2. [Important boundary, limitation, or unsupported prediction.]
3. [Implication for the broader research question.]

---

## 8. Human Intellectual Contributions

| Iteration or Decision Point | Human Contribution | Why It Mattered |
|---|---|---|
| [Iteration 01] | [Decision, insight, critique, or pivot] | [Effect on the research direction] |

---

## 9. Reproducibility Manifest

### Scripts and Methods

| Script or Method | Purpose | Primary Output |
|---|---|---|
| [Script](../experiments/01_synthetic/script_01_description.py) | [Purpose] | [Output] |

### Logs and Evidence

| Log or Evidence | Notes |
|---|---|
| [Log](../results/logs/script_01_*.log) | [Notes] |

### Figures and Tables

| Figure or Table | Notes |
|---|---|
| [Figure](../results/figures/figure_name.png) | [What it shows] |

---

## 10. Limitations and Caveats

1. [Modeling limitation.]
2. [Data limitation.]
3. [Generalization limitation.]

---

## 11. Recommended Next Steps

1. [Most important follow-up study or validation step.]
2. [Robustness or sensitivity analysis.]
3. [Higher-fidelity model, external dataset, or real-data validation.]

---

## 12. Final Assessment

### Primary Findings

- [Finding 1.]
- [Finding 2.]
- [Finding 3.]

### Research Significance

[Explain what the project now establishes, what decision it supports, and what boundary condition it identifies.]

### Methodological Assessment

[Explain whether the research process adequately distinguished robust findings from unsupported assumptions.]
