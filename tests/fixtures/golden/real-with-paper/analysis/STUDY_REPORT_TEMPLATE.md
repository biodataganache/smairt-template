# Study Report - [Project or Study Title]

| Field | Details |
|---|---|
| Research Project | Golden Paper Study |
| Study Scope | [One-sentence scope] |
| Methodological Approach | [Hypothesis-driven computational study / benchmark validation / other] |
| Generated | [YYYY-MM-DD] |
| Last Updated | [YYYY-MM-DD] |
| Report Status | DRAFT / INTERIM / UPDATED / FINAL |
| Primary Sources | [Link background and analysis files] |

## How to Use This Template

Use this template to create `analysis/STUDY_REPORT.md` at a major checkpoint or when the
researcher requests a project-level synthesis. The generated project does not create an
empty living report in advance. Unlike `ANALYSIS_XX.md`, which interprets one experiment,
the study report synthesizes the research state across iterations and phases.

1. Copy this file to `analysis/STUDY_REPORT.md`.
2. Read `background/`, `hypotheses/`, `experiments/`, `results/logs/`, `results/figures/`,
   `analysis/`, and `prompts/intellectual_contribution.md`.
3. Fill every section from durable evidence, not memory.
4. Use `INTERIM` while conclusions may change and `FINAL` only when no further work is planned.

## 1. Executive Summary

[Summarize the research question, strongest positive finding, important negative or boundary
finding, and significance of the current evidence.]

## 2. Project Question and Study Scope

### Central Question

[State the research question clearly.]

### Study Scope

[Describe included models, datasets, phases, systems, or algorithm families.]

### Model, Data, or Experimental Context

[Describe sources, assumptions, constants, preprocessing, and access constraints.]

### What This Study Is Designed to Resolve

[State the uncertainty, gap, or decision addressed.]

### What This Study Does Not Resolve

[State omitted mechanisms, missing validation, scale limits, and other boundaries.]

## 3. Research Audit Trail

| Iteration | Hypothesis | Script or Method | Log or Evidence | Analysis | Status |
|---|---|---|---|---|---|
| 01 | `hypotheses/HYPOTHESIS_01.md` | `experiments/01_synthetic/script_01.py` | `results/logs/script_01_*.log` | `analysis/ANALYSIS_01.md` | [Status] |

Flag missing logs, figures, analyses, and hypothesis status updates here.

## 4. Results Matrix

| Result Area | Representative Case | Main Quantitative Outcome | Interpretation |
|---|---|---:|---|
| [Positive result] | [Conditions] | [Metrics] | [Meaning] |
| [Boundary result] | [Conditions] | [Limit] | [Why it matters] |

## 5. Iteration-Level Findings

Repeat this section for each iteration or phase that materially changes the conclusions.

### Iteration [XX] - [Short Title]

#### Goal

[What uncertainty did this iteration address?]

#### Method

[What ran, with which inputs and conditions?]

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| [Metric] | [Expected] | [Observed] | Success / Partial / Failed / Inconclusive |

#### Interpretation

[Explain the hypothesis assessment, scientific meaning, boundaries, and caveats.]

#### Generated Artifacts

- Log: `results/logs/[name].log`
- Figure: `results/figures/[name]`
- Analysis: `analysis/ANALYSIS_XX.md`

## 6. Cross-Iteration Comparison

| Metric or Decision | Iteration 1 | Iteration 2 | Iteration 3 | Current Interpretation |
|---|---:|---:|---:|---|
| [Shared metric] | [Value] | [Value] | [Value] | [Trend or decision] |

[Describe improvements, regressions, parameter boundaries, and evidence-driven pivots.]

## 7. Key Scientific Conclusions

1. [Evidence-supported conclusion.]
2. [Evidence-supported conclusion.]
3. [Important limitation or unsupported prediction.]

Link each conclusion to an analysis or result artifact.

## 8. Human Intellectual Contributions

Source: `prompts/intellectual_contribution.md`

| Decision Point | Human Contribution | Why It Mattered |
|---|---|---|
| [Iteration] | [Decision, critique, or pivot] | [Effect on research direction] |

## 9. Reproducibility Manifest

### Scripts and Methods

| Script or Method | Purpose | Primary Output |
|---|---|---|
| [Path] | [Purpose] | [Log, figure, table, or model] |

### Logs and Evidence

| Log or Evidence | Notes |
|---|---|
| [Path] | [Selected, exploratory, failed, or validation run] |

### Figures and Tables

| Figure or Table | Source and Notes |
|---|---|
| [Path] | [Source script and what it shows] |

### Interpretation Files

| File | Purpose |
|---|---|
| [Path] | [What this analysis interpreted] |

## 10. Limitations and Caveats

1. [Modeling limitation.]
2. [Data limitation.]
3. [Statistical or uncertainty limitation.]
4. [Generalization limitation.]
5. [Operational limitation.]

State limitations as research boundaries, not apologies.

## 11. Recommended Next Steps

1. [Most important follow-up study.]
2. [Robustness or sensitivity analysis.]
3. [External or real-data validation.]
4. [Documentation, publication, or handoff step.]

## 12. Final Assessment

### Primary Findings

- [Finding 1.]
- [Finding 2.]
- [Finding 3.]

### Research Significance

[What does the project establish, what decision does it support, and what boundary does it identify?]

### Methodological Assessment

[Did the process distinguish robust findings from unsupported assumptions?]
