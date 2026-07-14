# Study Report — [Project or Study Title]

| Field | Details |
|---|---|
| Research Project | {{ cookiecutter.project_name }} |
| Study Scope | [One-sentence scope of the research question, model, dataset, or system studied] |
| Methodological Approach | [Hypothesis-driven computational study / experimental analysis / benchmark validation / other] |
| Generated | [YYYY-MM-DD] |
| Last Updated | [YYYY-MM-DD] |
| Report Status | DRAFT / INTERIM / UPDATED / FINAL |
| Primary Sources | [background/01_initial_question.md](../background/01_initial_question.md); [ANALYSIS_01.md](ANALYSIS_01.md); [add additional analysis files] |

---

## How to Use This Template

Use this file to create a project-level research synthesis at any major checkpoint. It can be written after one iteration, after a phase transition, before a handoff, before paper drafting, or at the end of the project. Unlike `ANALYSIS_XX.md`, which interprets one experiment or iteration, the study report synthesizes the whole research state so far — whether the project is still in progress or complete.

Recommended workflow:

1. Copy this file to `STUDY_REPORT.md` in the same `analysis/` folder. If you want to preserve a dated snapshot alongside the living document, also save a copy such as `analysis/reports/STUDY_REPORT_YYYYMMDD.md`.
2. Read the research audit trail: `background/`, `hypotheses/`, `experiments/`, `results/logs/`, `results/figures/`, `analysis/`, and `prompts/intellectual_contribution.md`.
3. Fill every section from evidence in the project files, not from memory.
4. Keep the framing as an actual research report. Do not describe the project as a demo, template exercise, or AI-code-generation example.
5. Set `Report Status` to reflect where the project actually stands:
   - `DRAFT` — first pass, sections still being filled in.
   - `INTERIM` — accurate as of the current iteration, but the project is still active and conclusions may change.
   - `UPDATED` — a prior report was revised because new iterations changed the conclusions.
   - `FINAL` — the project has reached its planned end state and no further iterations are expected.

---

## 1. Executive Summary

[Write 2-4 paragraphs summarizing the research question, the main positive findings, the main negative or boundary findings, and the significance of the current evidence.]

Include:

- The central research objective.
- The strongest supported conclusion.
- Any important unsupported or partially supported hypothesis.
- What the current results imply for future work.

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

[State boundaries honestly. Include omitted mechanisms, missing validation data, scale limits, uncertainty not modeled, or conditions outside the current evidence base.]

---

## 3. Research Audit Trail

The research record connects each hypothesis to its implementation, evidence, interpretation, and current status.

| Iteration | Hypothesis | Script or Method | Log or Evidence | Analysis | Status |
|---|---|---|---|---|---|
| 01 | [HYPOTHESIS_01.md](../hypotheses/HYPOTHESIS_01.md) | [script_01_description.py](../experiments/01_synthetic/script_01_description.py) | [script_01_*.log](../results/logs/script_01_*.log) | [ANALYSIS_01.md](ANALYSIS_01.md) | SUPPORTED / REFUTED / PARTIALLY SUPPORTED / INCONCLUSIVE |
| 02 | [HYPOTHESIS_02.md](../hypotheses/HYPOTHESIS_02.md) | [script_02_description.py](../experiments/01_synthetic/script_02_description.py) | [script_02_*.log](../results/logs/script_02_*.log) | [ANALYSIS_02.md](ANALYSIS_02.md) | SUPPORTED / REFUTED / PARTIALLY SUPPORTED / INCONCLUSIVE |

Notes:

- [Flag any hypothesis file whose status has not yet been updated even though an analysis file contains the final interpretation.]
- [Flag any missing logs, missing figures, or incomplete analysis files.]

---

## 4. Results Matrix

| Result Area | Best or Representative Case | Main Quantitative Outcome | Interpretation |
|---|---:|---:|---|
| [Result area 1] | [Parameters / data subset / method] | [Metric values] | [What the result means] |
| [Result area 2] | [Parameters / data subset / method] | [Metric values] | [What the result means] |
| [Boundary or negative result] | [Conditions tested] | [Observed limit or failure mode] | [Why this matters] |

Use this matrix to make the whole project legible at a glance.

---

## 5. Iteration-Level Findings

Repeat this subsection for each major iteration, track, or phase that materially changes the project conclusions.

### Iteration [XX] — [Short Title]

#### Goal

[What was this iteration trying to determine?]

Sources: [HYPOTHESIS_XX.md](../hypotheses/HYPOTHESIS_XX.md), [ANALYSIS_XX.md](ANALYSIS_XX.md)

#### Method

[Briefly describe what was run, what inputs were used, and what conditions were tested.]

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| [Metric 1] | [Expected value or direction] | [Observed value] | Success / Partial / Failed / Inconclusive |
| [Metric 2] | [Expected value or direction] | [Observed value] | Success / Partial / Failed / Inconclusive |

#### Interpretation

[Explain whether the hypothesis was supported, what the result means scientifically, and any boundaries or caveats discovered.]

#### Generated Artifacts

- Log or evidence: [script_XX_*.log](../results/logs/script_XX_*.log)
- Figure: [figure_name.png](../results/figures/figure_name.png)
- Data or table: [artifact_name.ext](../results/[path]/artifact_name.ext)

---

## 6. Cross-Iteration Comparison

| Metric or Decision Point | Iteration 1 | Iteration 2 | Iteration 3 | Current Interpretation |
|---|---:|---:|---:|---|
| [Shared metric] | [Value] | [Value] | [Value] | [Trend or decision] |
| [Boundary condition] | [Value] | [Value] | [Value] | [What changed] |

### Trend Across the Study

[Describe how the research evolved. Note improvements, regressions, parameter boundaries, failure modes, and decisions that changed because of evidence.]

---

## 7. Key Scientific Conclusions

1. [Conclusion supported by evidence.]
2. [Conclusion supported by evidence.]
3. [Important boundary, limitation, or unsupported prediction.]
4. [Implication for the broader research question.]

Each conclusion should be traceable to an analysis file or result artifact.

---

## 8. Human Intellectual Contributions

Source: [intellectual_contribution.md](../prompts/intellectual_contribution.md)

| Iteration or Decision Point | Human Contribution | Why It Mattered |
|---|---|---|
| [Iteration 01] | [Decision, insight, critique, or pivot] | [Effect on the research direction] |
| [Iteration 02] | [Decision, insight, critique, or pivot] | [Effect on the research direction] |

[Summarize the role of human interpretation, domain judgment, and decisions to pivot, continue, or stop. Keep the focus on research provenance rather than tool usage.]

---

## 9. Reproducibility Manifest

### Scripts and Methods

| Script or Method | Purpose | Primary Output |
|---|---|---|
| [script_01_description.py](../experiments/01_synthetic/script_01_description.py) | [Purpose] | [Log, figure, table, model, etc.] |

### Logs and Evidence

| Log or Evidence | Notes |
|---|---|
| [script_01_*.log](../results/logs/script_01_*.log) | [Final selected run / exploratory run / failed run / validation run] |

### Figures and Tables

| Figure or Table | Notes |
|---|---|
| [figure_name.png](../results/figures/figure_name.png) | [What it shows] |

### Interpretation Files

| File | Purpose |
|---|---|
| [ANALYSIS_01.md](ANALYSIS_01.md) | [What this analysis interpreted] |

---

## 10. Limitations and Caveats

1. [Modeling limitation.]
2. [Data limitation.]
3. [Statistical or uncertainty limitation.]
4. [Generalization limitation.]
5. [Operational or implementation limitation.]

State limitations as research boundaries, not apologies.

---

## 11. Recommended Next Steps

1. [Most important follow-up study or validation step.]
2. [Robustness or sensitivity analysis.]
3. [Higher-fidelity model, external dataset, or real-data validation.]
4. [Documentation, publication, or handoff step.]

Each next step should follow logically from the evidence and limitations above.

---

## 12. Final Assessment

[Write this as a research conclusion, not as a description of a template, demonstration, or AI workflow.]

### Primary Findings

- [Finding 1.]
- [Finding 2.]
- [Finding 3.]

### Research Significance

[Explain what the project now establishes, what decision it supports, and what boundary condition it identifies.]

### Methodological Assessment

[Explain whether the research process adequately distinguished robust findings from unsupported assumptions. Mention failed hypotheses only insofar as they strengthened the scientific record.]
