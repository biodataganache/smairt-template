# Findings Ledger — {{ cookiecutter.project_name }}

> **Layer 2 of 3: durable, curated long-term memory.** This is "what we have learned
> that is still true." It is loaded every session, so keep it small and curated —
> not a running log (that's the `analysis/` archive, layer 3).
>
> The one rule that makes long-term recall work: **promotion.** When a result
> graduates from "a number in one iteration" to "a fact that should shape future
> work," add it here with full scope. Before designing any new experiment, read this
> file first.

---

## The non-negotiable rule: no bare verdicts

A finding is **never** a universal truth like "X doesn't work." It is a claim bound
to the context it was found in. Every entry MUST carry a `Scope:` field. A finding
without a scope is a bug.

When the dataset, scale, or phase changes, narrower-context findings become
**provisional** — re-validate before relying on them, record the new result with its
new scope, and link the two. Keep both: *"X fails on small data but works at scale"*
is a richer, truer finding than either run alone.

### Entry format

```
### F-NNN: <short title>
- Claim:      <what is true>
- Scope:      <dataset, size N, phase, key conditions>
- Evidence:   <analysis/ANALYSIS_XX.md, results/logs/script_XX*.log>
- Status:     established | provisional | needs-revalidation | superseded-by F-NNN
- Supersedes: <F-NNN and one line on why, if applicable>
- Date:       <YYYY-MM-DD> · iter <XX>
```

**Status values**
- `established` — confirmed in its scope; rely on it within that scope.
- `provisional` — seen in a narrow context; not yet confirmed at scale/other phases.
- `needs-revalidation` — context has since changed; do NOT trust until re-tested.
- `superseded-by F-NNN` — a later, wider-scope finding replaces it (keep for history).

---

## Established Findings

<!-- Promote durable results here. Newest at top. Delete nothing — supersede instead. -->

<!-- Example (remove once you have real findings):

### F-002: Frequency weighting improves AUPRC at scale
- Claim:      frequency weighting helps the model
- Scope:      real dataset (N≈50k), phase 03_real
- Evidence:   analysis/ANALYSIS_17.md, results/logs/script_17*.log
- Status:     established
- Supersedes: F-001 (failed on synthetic N≈500 — small-sample artifact)
- Date:       2026-05-02 · iter 17

### F-001: Frequency weighting did not help on preliminary data
- Claim:      frequency weighting gave no measurable lift
- Scope:      synthetic dataset (N≈500), phase 01_synthetic
- Evidence:   analysis/ANALYSIS_07.md, results/logs/script_07*.log
- Status:     superseded-by F-002 (re-tested at scale; was a small-sample artifact)
- Date:       2026-03-11 · iter 7
-->

## Requirements / Must-Holds

<!-- Established findings that translate into a standing rule for all future scripts.
     e.g. "Always apply frequency weighting (F-002). Always seed with SEED=42." -->
-

## Dead Ends

<!-- Approaches confirmed not to work, WITH scope. Prevents re-running them. -->
-
