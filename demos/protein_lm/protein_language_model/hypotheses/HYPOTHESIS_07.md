# Hypothesis 07 — Embeddings separate families defined by a learnable many-pair coupling rule

## Status: PENDING

## Background

Iteration 06 ([`ANALYSIS_06.md`](../analysis/ANALYSIS_06.md)) produced a clean null:
two families differing by a **single** pairwise coupling (`seq[j]=seq[i]`) had both
controls at chance (the design was confound-free — H_06B PASS), but the **trained**
nano-MLM also stayed at chance and never learned the coupling. A single coupled
pair among 50 columns barely affects the masked-LM loss, so there is no gradient
signal to learn it (logged as [`KNOWN_PATTERNS.md`](../prompts/KNOWN_PATTERNS.md)
§2.4).

This iteration strengthens the planted signal so that **learning the rule
materially reduces the loss**, while preserving the airtight property from
iteration 06: every single-column marginal stays uniform, so neither composition
nor position nor any single-position statistic can separate the families.

## Hypothesis Statement

**Prediction**: Define K=10 disjoint column pairs `(a_k, b_k)` covering 20 of the 50
positions, and a fixed permutation `π` of the 20-residue alphabet.

- **Family A (coupled)**: for every pair, `seq[b_k] = π(seq[a_k])`.
- **Family B (independent)**: all columns independent uniform.

Because `π` is a bijection and `seq[a_k]` is uniform, `seq[b_k]` is also uniform —
so **every column's marginal is uniform in both families**, and per-sequence
composition has the same distribution. The families differ only in the **joint**
structure across the K pairs. Learning the rule now lets the model predict each
masked `b_k` from `a_k` (and vice versa), reducing loss on ~20/50 of all positions
— a strong, trainable signal.

A trained nano-MLM will learn the coupling; its mean-pooled embeddings will
**separate the families** (probe AUC high). An **untrained** model and a
**composition** baseline will both be at **chance**, isolating *learning* as the
cause.

**Success criteria**: see sub-hypotheses.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_07_bijection_coupling.py`
- **Phase**: synthetic
- **Data**: L=50, uniform background. K=10 disjoint pairs from a fixed seeded
  layout; fixed permutation `π` (a derangement of the alphabet). Family A applies
  `seq[b_k]=π(seq[a_k])`; Family B independent. N=1000/family (2000). Labels held
  out from training.
- **Model/training**: identical to script_03–06 (d_model=64, 4 heads, 2 layers,
  ff=128, 30 epochs, lr=1e-3, batch 128, 80/20 split, masked objective).
- **Embedding**: mean-pooled encoder output (64-d).
- **Probes/metrics**: logistic-regression probe AUC (held-out), PCA.
- **Controls**: untrained random-init embeddings and raw composition vectors —
  both must be at chance.
- **Mechanistic check**: masked accuracy at the `b_k` columns (with `a_k` visible),
  Family A vs Family B, averaged over the K pairs.

## Sub-Hypotheses

### H_07A: Trained embeddings separate the families
- **Success criteria**: probe AUC on held-out embeddings ≥ 0.90.

### H_07B: Both controls at chance (separation is *learned*)
- **Success criteria**: untrained-model AUC ≤ 0.60 **and** composition AUC ≤ 0.60.

### H_07C: The learned signal is the coupling rule
- **Success criteria**: mean masked accuracy at the `b_k` columns (with `a_k`
  visible) ≥ 0.80 for Family A and ≤ 0.15 for Family B (gap ≥ 0.50).

## Dependencies

- torch (CPU 2.12.1), numpy, matplotlib
- Reuses design from
  [`script_06_covariation_families.py`](../experiments/01_synthetic/script_06_covariation_families.py)
- Directly addresses [`ANALYSIS_06.md`](../analysis/ANALYSIS_06.md) fix and
  [`KNOWN_PATTERNS.md`](../prompts/KNOWN_PATTERNS.md) §2.4

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Seed | 1024 |
| Sequence length | 50 |
| Coupled pairs K | 10 (20 columns) |
| Permutation π | fixed derangement of the 20-letter alphabet |
| Family A | `seq[b_k]=π(seq[a_k])` for all k |
| Family B | all columns independent uniform |
| Marginals | uniform at every column in BOTH families |
| Corpus | N=1000/family (2000 total) |
| Model | d_model=64, nhead=4, layers=2, ff=128 |
| Epochs / lr / batch / val | 30 / 1e-3 / 128 / 0.2 |
| Metrics | probe AUC, PCA, mean coupled-col masked acc |

## Results

*(Filled in after experiment runs — see [`analysis/ANALYSIS_07.md`](../analysis/ANALYSIS_07.md))*

## Notes

- This is the airtight AND learnable version of the embedding claim: uniform
  marginals keep both controls at chance (fixing iter 05), and K=10 pairs make the
  rule materially loss-reducing (fixing iter 06).
- H_07C is the mechanistic smoking gun: the model separates families *because* it
  learned `π` linking the coupled columns.
