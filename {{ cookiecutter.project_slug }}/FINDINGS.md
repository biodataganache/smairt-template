# Findings Ledger: {{ cookiecutter.project_name }}

> Layer 2 of 3: durable, curated long-term memory. This is "what we have learned
> that is still true." It is loaded every session, so keep it small and curated. It
> is not a running log (that is the `analysis/` archive, layer 3).
>
> The one rule that makes long-term recall work is promotion. When a result graduates
> from "a number in one iteration" to "a fact that should shape future work," add it
> here with full scope. Before designing any new experiment, read this file first.

---

## The non-negotiable rule: no bare verdicts

A finding is never an unscoped verdict like "X doesn't work." It is a claim paired
with the context it was found in. Every entry MUST carry a `Scope:` field. A finding
without a scope is a bug, because it cannot be re-validated when the data changes.

When the dataset, scale, or phase changes, demote older narrow-scope findings to
`needs-revalidation`. Re-test before relying on them, record the new result under its
new scope, and link the two. Keep both: "X fails at N=500 but holds at N=50k" is a
stronger claim than either run alone, because it localizes the boundary.

### Entry format

```
### F-NNN: <short descriptive title>
- Claim:      <the durable statement, one sentence>
- Scope:      <size N, phase, and any condition the claim depends on>
- Metric:     <the headline number; optional but recommended>
- Data:       <dataset/source used: path, accession, or name + split>
- Evidence:   <analysis/ANALYSIS_XX.md, results/logs/script_XX*.log, script>
- Status:     established | provisional | needs-revalidation | superseded-by F-NNN | refuted
- Date:       <YYYY-MM-DD>, iter <NN>
- Supersedes: <F-NNN and one line on why, if applicable>
```

`Data` names what you ran on (the provenance pointer). `Scope` is the regime the claim
is bound to (size, phase, conditions). They are different: two findings can share the
same `Data` but hold under different `Scope`.

**Status values**
- `established`: confirmed within its scope; rely on it inside that scope.
- `provisional`: seen in a narrow setting; not yet confirmed at scale or other phases.
- `needs-revalidation`: the scope has since changed; do not trust until re-tested.
- `superseded-by F-NNN`: a later, wider-scope finding replaces it (kept for history).
- `refuted`: tested and does not hold; nothing replaced it. Prevents retrying it.

**ID rule:** `F-NNN` is stable and monotonic. Never reuse or renumber an ID. The
`Supersedes` and `superseded-by` links form the history graph, so a claim's evolution
is always reconstructable.

---

## Established Findings

<!-- Promote durable results here, newest at top. Delete nothing; supersede or refute
     instead. The block below is illustrative; remove it once you have real findings. -->

<!-- EXAMPLES (remove):

### F-017: Frequency weighting improves AUPRC at scale
- Claim:      frequency weighting improves AUPRC on the real dataset
- Scope:      N approx 50k, phase 03_real, fusion model
- Metric:     AUPRC 0.81 vs 0.74 unweighted
- Data:       data/real/transcriptomics_v3.parquet (train split)
- Evidence:   analysis/ANALYSIS_17.md, results/logs/script_17_freqweight.log
- Status:     established
- Date:       2026-05-02, iter 17
- Supersedes: F-007 (failed at N approx 500; that was a small-sample artifact)

### F-007: Frequency weighting did not help on preliminary data
- Claim:      frequency weighting gave no measurable lift
- Scope:      N approx 500, phase 01_synthetic
- Metric:     AUPRC 0.62 vs 0.63 unweighted (within noise)
- Data:       synthetic, generator seed 42
- Evidence:   analysis/ANALYSIS_07.md, results/logs/script_07_freqweight.log
- Status:     superseded-by F-017
- Date:       2026-03-11, iter 7

### F-031: Attention pooling beats mean pooling (one split only)
- Claim:      attention pooling over the sequence beats mean pooling
- Scope:      one real-data split, fold 1; not yet cross-validated
- Metric:     AUPRC 0.84 vs 0.81 on fold 1
- Data:       data/real/transcriptomics_v3.parquet (fold 1)
- Evidence:   analysis/ANALYSIS_31.md, results/logs/script_31_attnpool.log
- Status:     provisional
- Date:       2026-06-01, iter 31

-->

## Requirements / Must-Holds

<!-- Established findings that translate into a standing rule for all future scripts.
     Cite the finding each rule came from. -->
- <!-- e.g. Always split by site before training (from F-009); random splits leak batch signal. -->

## Dead Ends

<!-- Approaches confirmed not to work, WITH scope and the refuting finding.
     Prevents re-running them. -->
- <!-- e.g. PCA to 50 components before fusion loses signal (F-022, refuted). -->

---

## Results Log (optional)

<!-- A scannable numeric history. The ledger above holds interpreted claims; this
     holds the raw headline numbers per run. Keep full output in results/logs/. -->

| iter | script              | data        | metric | value | vs prev |
|------|---------------------|-------------|--------|-------|---------|
|      |                     |             |        |       |         |
