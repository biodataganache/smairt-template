# Analysis Plan

## Project: Golden Paper Study

**Researcher**: Grace Paper
**Created**: [DATE]
**Last Updated**: [DATE]

---

## 1. Overview

A normalized real-data Paper golden project.

**Research Question**: Not yet recorded

This is a living document. Update it when the plan changes, and record why in the
`Revisions` section at the bottom rather than silently editing a target.

---

## 2. Tracks

A track is a direction of inquiry, spanning as many iterations as it takes. Each track
has one or more hypotheses and produces its own evidence.

| Track | Question it answers | Hypotheses | Phase | Status |
|---|---|---|---|---|
| A | [What this direction settles] | HYPOTHESIS_01, HYPOTHESIS_02 | synthetic | Not started |
| B | [What this direction settles] | HYPOTHESIS_03 | downloaded | Not started |

Status: `Not started`, `Active`, `Paused`, `Complete`, `Abandoned`. An abandoned track
stays listed with its reason; a direction ruled out is a result.

---

## 3. Execution framework

### 3.1 How an iteration works

An iteration is one attempt: one script, the log it produced, and the interpretation of
that log. Iterations are numbered across the whole project in the order the work
happened, so the numbers read as a timeline.

```
hypotheses/HYPOTHESIS_01.md              the prediction and the criteria
experiments/01_synthetic/script_04_*.py   the attempt
results/logs/script_04_*.log              what it produced, unedited
analysis/ANALYSIS_04.md                   what it means
```

`analysis/ITERATION_LOG.md` carries one row per iteration, so the sequence of attempts
is readable without opening each analysis.

### 3.2 Single points and panels

A **single point** iteration tests one change and answers one question. A **panel**
iteration probes several candidate directions at once and returns one result per probe.

A panel is still one iteration. Record each probe separately: a panel of eight that
yields three improvements, one regression, and four null results has produced three
findings, not one. Collapsing it into a single verdict discards most of the work.

### 3.3 Shared code

Functions used by more than one experiment belong in `scripts/shared/`, imported as
`from scripts.shared.<module> import ...`. Keep experiment scripts readable as a record
of what was done; move only genuinely reusable machinery.

### 3.4 Computational resources

- [ ] Local machine
- [ ] HPC cluster
- [ ] Cloud

---

## 4. Track detail

### Track A - [Name]

**Question**: [What does this track settle?]

**Hypotheses**: `hypotheses/HYPOTHESIS_01.md`

**Data inputs**:
- [Files and their provenance record]

**Planned iterations**:

| # | Kind | What it tests | Depends on |
|---|---|---|---|
| 1 | single | [Baseline] | — |
| 2 | panel | [Candidate variations] | Iteration 1 |

**Expected outputs**:
- Interpretations: `analysis/ANALYSIS_XX.md`
- Figures: [Which figures, and what each is evidence for]

### Track B - [Name]

**Question**: [What does this track settle?]

**Hypotheses**: `hypotheses/HYPOTHESIS_03.md`

**Data inputs**:
- [Files and their provenance record]

**Planned iterations**:

| # | Kind | What it tests | Depends on |
|---|---|---|---|
| 1 | single | [First attempt] | Track A complete |

---

## 5. Evaluation framework

### 5.1 Metrics

| Metric | What it measures | Target | Why this target |
|---|---|---|---|
| [Metric] | [Description] | [Value] | [Justification recorded before running] |

A target chosen after seeing the data is not a target. Record the justification when the
target is set.

### 5.2 Validation

- [ ] [Baseline or negative control]
- [ ] [Held-out or independent data]
- [ ] [Repetition across seeds]

---

## 6. Figure plan

Every figure is evidence for a specific claim. Name the claim, not just the subject.

### Main figures

| Figure | Claim it supports | Iteration | Status |
|---|---|---|---|
| Fig 1 | [The claim] | [NN] | Not started |

### Supplementary figures

| Figure | Claim it supports | Iteration | Status |
|---|---|---|---|
| S1 | [The claim] | [NN] | Not started |

---

## 7. Data requirements

| Dataset | Location | Format | Size | Status |
|---|---|---|---|---|
| [Name] | `data/[phase]/[path]` | [Format] | [Size] | Available |
| [Name] | `data/[phase]/[path]` | [Format] | [Size] | Needed |

---

## 8. Hypotheses

The full statement, criteria, and design live in `hypotheses/`. This is the index.

| ID | Statement | Track | Tested by | Status |
|---|---|---|---|---|
| HYPOTHESIS_01 | [Short form] | A | Iteration [NN] | PENDING |
| HYPOTHESIS_02 | [Short form] | A | Not yet | PENDING |

Status: `PENDING`, `SUPPORTED`, `REFUTED`, `PARTIALLY SUPPORTED`, `INCONCLUSIVE`.

---

## 9. Reproducibility

- Random seed: [value], recorded in each script that uses randomness
- Parameters: stated in the script or a config file it reads, not passed ad hoc
- Environment: captured so a run can be repeated

### Checklist

- [ ] Every iteration has a row in `analysis/ITERATION_LOG.md`
- [ ] Every numeric claim traces to a specific log file
- [ ] Panel results are recorded per probe, not summarized
- [ ] Negative and null results are recorded, not dropped
- [ ] Figures name the claim they support

---

## 10. Revisions

| Date | What changed | Why |
|---|---|---|
| [DATE] | Initial plan | — |
