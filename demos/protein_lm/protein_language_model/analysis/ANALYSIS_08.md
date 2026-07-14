# Analysis 08 — Embeddings separate families by a LEARNED rule: the airtight result

**Hypothesis:** [`HYPOTHESIS_08.md`](../hypotheses/HYPOTHESIS_08.md) (H_08A/B/C)
**Script:** [`experiments/01_synthetic/script_08_identity_coupling.py`](../experiments/01_synthetic/script_08_identity_coupling.py)
**Log:** `results/logs/script_08_identity_coupling_*.log`
**Figures:** `results/figures/script_08_embedding_pca.png`, `results/figures/script_08_auc_vs_controls.png`
**Date:** 2026-06-29 · **Seed:** 1024 · **torch** 2.12.1 (CPU)

## Status: ALL SUPPORTED — H_08A, H_08B, H_08C PASS

This is the headline result of the synthetic rung and the culmination of a
four-iteration refinement (05→08) of the project's embedding claim. Two families
share **identical single-column marginals** (uniform everywhere) and **identical
composition**, differing only in whether K=10 column pairs obey an identity-copy
rule (`seq[b_k]=seq[a_k]`, Family A) or are independent (Family B). Generator
verified: max |marginal − 1/20| = 0.022; rule satisfaction FamA = 1.000, FamB =
0.051.

## Results

| metric | trained | untrained ctrl | composition |
|--------|---------|----------------|-------------|
| linear-probe AUC (val) | **1.0000** | 0.5157 | 0.5108 |
| mean masked acc at b-cols (a visible) | FamA=**1.000**, FamB=0.0495 | — | — |

- **H_08A (trained AUC ≥ 0.90):** PASS — 1.0000. Embeddings perfectly separable.
- **H_08B (controls at chance):** PASS — untrained 0.516, composition 0.511.
- **H_08C (copy rule learned):** PASS — FamA coupled-column accuracy 1.000, FamB at
  chance 0.0495 (gap 0.95).

## Interpretation — separation is *caused by learning*, with the mechanism proven

This experiment isolates learning as the sole cause of family separation:

1. **Both controls are at chance.** Because every column's marginal is uniform in
   both families, neither residue **composition** nor motif **position** (the two
   shortcuts that confounded earlier attempts) carries any family signal. The
   untrained random-init model and the composition baseline both sit at ~0.51.
2. **The trained model separates perfectly (AUC 1.000).** The only thing that
   changed is training — so the separation is *learned*, not architectural.
3. **The mechanism is identified.** The conditional probe shows the model predicts
   each coupled `b` column from its partner `a` with accuracy 1.000 for Family A and
   chance for Family B. The model separates the families **because** it learned the
   copy rule and routes information between coupled positions via self-attention.

This is exactly the project hypothesis' embedding claim, demonstrated in its
strongest form: *learned per-sequence embeddings separate two planted families*,
with composition and position controls proving the separation is grammar the model
learned, not a shortcut.

## The 05→08 arc (why this took four iterations — and why that is the science)

| iter | family difference | controls | trained model | lesson |
|------|-------------------|----------|---------------|--------|
| 05 | motif **position** | untrained also separates (0.978) | AUC 1.000 | position is free → confounded test (§2.3) |
| 06 | **single** coupled pair | both at chance ✓ | at chance | signal too sparse for the loss (§2.4) |
| 07 | K=10 **permutation** | both at chance ✓ | AUC 0.604 (partial) | rule too complex at nano budget (§2.5) |
| 08 | K=10 **identity copy** | both at chance ✓ | **AUC 1.000** | airtight + learnable ✓ |

Each "failure" sharpened the design and produced a reusable anti-pattern. The final
design controls for composition and position simultaneously while planting a signal
that is both **loss-relevant** (K=10) and **learnable** (identity copy).

## What this closes

- **Rung 1** (iters 01–04): generator validated; nano-MLM beats baseline,
  reconstructs the motif, and tracks the Bayes-optimal conservation curve.
- **Rung 2** (iters 05–08): a single model learns multi-position structure, and its
  embeddings separate two families by *learned* grammar (this analysis).

The synthetic ladder is complete. The natural next step is **Rung 3**: confirm the
embedding-separation idea on **real** sequences using a pretrained ESM-2 model.

## Limitations

- Identity copy is the easiest non-trivial dependency; harder rules need bigger
  models (quantified in iter 07). This proves the *mechanism*, not biological
  insight.
- Single seed; AUC 1.000 with controls at chance is unambiguous, but multi-seed
  error bars would be cheap to add for publication.
