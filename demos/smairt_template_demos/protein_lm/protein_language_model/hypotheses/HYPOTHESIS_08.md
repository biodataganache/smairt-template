# Hypothesis 08 — Embeddings separate families defined by an easy-to-learn copy rule

## Status: PENDING

## Background

The two-family embedding claim has been narrowed across three iterations:

- **iter 05** ([`ANALYSIS_05.md`](../analysis/ANALYSIS_05.md)): families differed by
  motif *position* → untrained control also separated (position is free). Confound.
- **iter 06** ([`ANALYSIS_06.md`](../analysis/ANALYSIS_06.md)): single coupled pair,
  uniform marginals → controls clean, but signal too sparse to affect the loss;
  trained model at chance. ([`KNOWN_PATTERNS.md`](../prompts/KNOWN_PATTERNS.md) §2.4)
- **iter 07** ([`ANALYSIS_07.md`](../analysis/ANALYSIS_07.md)): K=10 pairs linked by
  an arbitrary permutation → controls clean, signal loss-relevant, trained model
  rose above controls (AUC 0.604, coupled-col acc 0.183) but the permutation was
  too hard to fully learn at nano budget. (§2.5)

The design is now airtight (uniform marginals keep both controls at chance); the
only remaining obstacle is the **complexity of the mapping**. This iteration uses
the simplest learnable mapping.

## Hypothesis Statement

**Prediction**: Define K=10 disjoint column pairs `(a_k, b_k)`. 

- **Family A (copy)**: `seq[b_k] = seq[a_k]` for every pair.
- **Family B (independent)**: all columns independent uniform.

Since `seq[a_k]` is uniform, `seq[b_k]` is uniform too → every column's marginal is
uniform in both families and composition is matched, so **both controls stay at
chance**. But the mapping is now the trivial identity ("copy your partner"), which a
single self-attention head can implement. With a modest budget bump (40 epochs),
the trained nano-MLM will **learn the copy rule** and its mean-pooled embeddings
will **separate the families** at high AUC, while controls remain at chance.

**Success criteria**: see sub-hypotheses.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_08_identity_coupling.py`
- **Phase**: synthetic
- **Data**: L=50, uniform background. K=10 disjoint pairs (fixed seeded layout).
  Family A: `seq[b_k]=seq[a_k]`; Family B independent. N=1000/family (2000). Labels
  held out from training.
- **Model/training**: same architecture (d_model=64, 4 heads, 2 layers, ff=128),
  **EPOCHS=40** (modest bump from 30), lr=1e-3, batch 128, 80/20 split, masked
  objective only.
- **Embedding**: mean-pooled encoder output (64-d).
- **Probes/metrics**: logistic-regression probe AUC (held-out), PCA.
- **Controls**: untrained random-init embeddings and raw composition — both must be
  at chance.
- **Mechanistic check**: mean masked accuracy at `b_k` columns (with `a_k` visible),
  Family A vs Family B.

## Sub-Hypotheses

### H_08A: Trained embeddings separate the families
- **Success criteria**: probe AUC on held-out embeddings ≥ 0.90.

### H_08B: Both controls at chance (separation is *learned*)
- **Success criteria**: untrained-model AUC ≤ 0.60 **and** composition AUC ≤ 0.60.

### H_08C: The learned signal is the copy rule
- **Success criteria**: mean masked accuracy at the `b_k` columns (with `a_k`
  visible) ≥ 0.80 for Family A and ≤ 0.15 for Family B (gap ≥ 0.50).

## Dependencies

- torch (CPU 2.12.1), numpy, matplotlib
- Reuses design from
  [`script_07_bijection_coupling.py`](../experiments/01_synthetic/script_07_bijection_coupling.py)
- Directly addresses [`ANALYSIS_07.md`](../analysis/ANALYSIS_07.md) fix and §2.5

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Seed | 1024 |
| Sequence length | 50 |
| Coupled pairs K | 10 (20 columns) |
| Rule | Family A: `seq[b]=seq[a]` (identity copy); Family B independent |
| Marginals | uniform at every column in BOTH families |
| Corpus | N=1000/family (2000 total) |
| Model | d_model=64, nhead=4, layers=2, ff=128 |
| Epochs / lr / batch / val | 40 / 1e-3 / 128 / 0.2 |
| Metrics | probe AUC, PCA, mean coupled-col masked acc |

## Results

*(Filled in after experiment runs — see [`analysis/ANALYSIS_08.md`](../analysis/ANALYSIS_08.md))*

## Notes

- This is the airtight AND learnable demonstration: uniform marginals keep controls
  at chance (fixes iter 05), K=10 makes the signal loss-relevant (fixes iter 06),
  and identity-copy makes the rule learnable at nano scale (fixes iter 07).
- A PASS here closes the project's embedding claim on the synthetic rung and is the
  natural launch point for Rung 3 (real sequences via pretrained ESM-2).
