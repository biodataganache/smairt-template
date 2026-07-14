# Hypothesis 06 — Embeddings separate families that differ ONLY by pairwise covariation

## Status: PENDING

## Background

Iteration 05 ([`ANALYSIS_05.md`](../analysis/ANALYSIS_05.md)) tested whether
mean-pooled embeddings separate two families. The trained model separated them
(AUC 0.9998) and the composition control was correctly at chance (0.486), but the
**untrained random-init model also separated** them (AUC 0.978): because the two
families differed by motif **position**, and position is injected by the model's
position embeddings *before* any training, the architecture solved the task for
free. That experiment therefore could not attribute separation to *learning*
(logged as [`KNOWN_PATTERNS.md`](../prompts/KNOWN_PATTERNS.md) §2.3).

This iteration fixes the design so that separation is possible **only** for a model
that has learned a content dependency that self-attention must discover.

## Hypothesis Statement

**Prediction**: Construct two families that are identical in (i) per-sequence
composition, (ii) every single-column marginal distribution, and (iii) motif
position — differing **only** in a *pairwise covariation* between two fixed columns
`i` and `j`:

- **Family A (coupled)**: the residue at column `j` is set equal to the residue at
  column `i` (perfect coupling).
- **Family B (independent)**: columns `i` and `j` are drawn independently.

Because each column's marginal is identical across families (both uniform over the
alphabet at `i` and `j`), neither composition nor position nor any single-position
statistic can distinguish the families — **only the joint (i, j) distribution
differs**. A trained nano-MLM, whose self-attention can condition column `j`'s
prediction on column `i`, will learn this dependency and its embeddings will
separate the families. An **untrained** model and a **composition** baseline will
both be at **chance**.

**Rationale**: Capturing a pairwise dependency requires routing information between
positions — exactly what attention does and what fixed position embeddings cannot.
Equal marginals neutralize the position-embedding shortcut that confounded
iteration 05.

**Success criteria**: see sub-hypotheses.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_06_covariation_families.py`
- **Phase**: synthetic
- **Data**: L=50, uniform background. Coupling columns `i=15`, `j=35`. N=1000 per
  family (2000 total). Family A: `seq[j] = seq[i]`. Family B: `seq[i], seq[j]`
  independent. (Marginals at i and j are uniform in BOTH families.) Family labels
  held out from training; used only for evaluation.
- **Model/training**: identical to script_03–05 (d_model=64, 4 heads, 2 layers,
  ff=128, 30 epochs, lr=1e-3, batch 128, 80/20 split, masked-residue objective).
- **Embedding**: mean-pooled encoder output (64-d per sequence).
- **Probes/metrics**: logistic-regression probe AUC (held-out), PCA for viz.
- **Controls**: same probe on (1) untrained random-init embeddings and (2) raw
  composition vectors — both must be at chance.
- **Mechanistic check**: masked accuracy at column `j` when column `i` is visible,
  Family A vs Family B. The model should predict `j` well above chance for Family A
  (it can copy from `i`) and only at chance for Family B.

## Sub-Hypotheses

### H_06A: Trained embeddings separate the families
- **Success criteria**: logistic-regression probe AUC on held-out embeddings ≥ 0.90.

### H_06B: Both controls are at chance (separation is *learned*)
- **Success criteria**: untrained-model probe AUC ≤ 0.60 **and** composition probe
  AUC ≤ 0.60. (This is the criterion iteration 05 failed; it is the whole point.)

### H_06C: The learned signal is the (i, j) coupling
- **Success criteria**: masked accuracy at column `j` (with `i` unmasked) is
  clearly higher for Family A than Family B (gap ≥ 0.30), and Family B's `j`
  accuracy is near chance (≤ 0.15). Confirms the model exploits the planted
  dependency, not an artifact.

## Dependencies

- torch (CPU 2.12.1), numpy, matplotlib
- Reuses model/training/eval design from
  [`script_05_two_family_embeddings.py`](../experiments/01_synthetic/script_05_two_family_embeddings.py)
- Directly addresses [`ANALYSIS_05.md`](../analysis/ANALYSIS_05.md) fix and
  [`KNOWN_PATTERNS.md`](../prompts/KNOWN_PATTERNS.md) §2.3

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Seed | 1024 |
| Sequence length | 50 |
| Coupling columns | i=15, j=35 |
| Family A | `seq[j] = seq[i]` (coupled) |
| Family B | i, j independent |
| Marginals | uniform at i and j in BOTH families |
| Corpus | N=1000/family (2000 total) |
| Model | d_model=64, nhead=4, layers=2, ff=128 |
| Epochs / lr / batch / val | 30 / 1e-3 / 128 / 0.2 |
| Metrics | probe AUC, PCA, conditional masked acc at j |

## Results

*(Filled in after experiment runs — see [`analysis/ANALYSIS_06.md`](../analysis/ANALYSIS_06.md))*

## Notes

- This is the airtight version of the project's embedding claim: equal marginals
  remove every shortcut (composition AND position), so a passing untrained control
  at chance plus a high trained AUC isolates *learning* as the cause.
- A passing H_06C is the mechanistic smoking gun: the model separates families
  *because* it learned to copy residue `i` into `j` for the coupled family.
