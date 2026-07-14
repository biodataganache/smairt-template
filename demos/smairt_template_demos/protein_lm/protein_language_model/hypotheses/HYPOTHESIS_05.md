# Hypothesis 05 — Mean-pooled embeddings separate two planted families by motif position

## Status: PENDING

## Background

Iterations 01–04 established the single-family results: a validated generator
([`ANALYSIS_01.md`](../analysis/ANALYSIS_01.md)), a nano-MLM that beats a
discriminating baseline and reaches the per-column ceiling
([`ANALYSIS_03.md`](../analysis/ANALYSIS_03.md)), and motif accuracy that tracks
the Bayes-optimal conservation curve ([`ANALYSIS_04.md`](../analysis/ANALYSIS_04.md)).

The one remaining claim in the project hypothesis
([`01_initial_question.md`](../background/01_initial_question.md)) is the **Rung 2
headline**: *"Learned per-sequence embeddings will separate two planted families."*
This iteration tests it.

We deliberately design the two families so that **family identity is encoded
purely by motif position, not by residue composition**: both families plant the
identical motif `GKTYRG`, but Family A places it at columns 22–27 and Family B at
columns 10–15, on an identical uniform background. Because both families inject the
same six motif residues (and draw everything else uniformly), their **per-sequence
amino-acid composition is statistically identical**. Any family separation a model
achieves must therefore come from learned **positional grammar**, not from a
bag-of-residues shortcut. This forecloses the non-discriminating-baseline
anti-pattern logged in [`KNOWN_PATTERNS.md`](../prompts/KNOWN_PATTERNS.md) §2.2.

## Hypothesis Statement

**Prediction**: A single nano-MLM trained (masked-residue objective, family labels
**never** shown to the model) on a mixed corpus of the two families will learn
mean-pooled per-sequence embeddings whose geometry **separates the two families**.
A simple linear probe on the trained embeddings will classify family near
perfectly, while the same probe on (a) an **untrained** random-init model and
(b) **raw residue composition** stays at chance.

**Rationale**: To predict masked residues well, the model must learn *where* the
conserved motif sits. That positional information is context that propagates into
every residue's contextual embedding; mean-pooling surfaces it at the
sequence level. Composition cannot distinguish the families by construction, so a
composition probe must be at chance — isolating "learned positional grammar" as the
only explanation for separation.

**Success criteria**: see sub-hypotheses.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_05_two_family_embeddings.py`
- **Phase**: synthetic
- **Data**: motif `GKTYRG` (100% conserved); Family A at cols 22–27, Family B at
  cols 10–15; N=1000 sequences per family (2000 total), L=50, uniform background.
  Family labels are held out from training and used **only** for evaluation.
- **Model/training**: identical to script_03/04 (d_model=64, 4 heads, 2 layers,
  ff=128, 30 epochs, lr=1e-3, batch 128, 80/20 train/val split, masked-residue
  objective only — no family supervision).
- **Embedding**: encoder output mean-pooled over sequence positions → 64-d vector
  per sequence.
- **Probes / metrics** (numpy/torch only — no new dependency):
  - linear logistic-regression probe trained on train-split embeddings, AUC on the
    held-out val split (5-fold-free: single held-out split, fixed seed);
  - silhouette score of val embeddings against family labels;
  - 2D PCA for visualization.
- **Controls**: same probes/metrics on (1) untrained random-init model embeddings
  and (2) raw one-hot-composition vectors (20-d residue counts per sequence).

## Sub-Hypotheses

### H_05A: Trained embeddings linearly separate families
- **Success criteria**: logistic-regression probe AUC on held-out embeddings
  ≥ 0.95 (vs 0.5 chance).

### H_05B: Trained embeddings cluster by family
- **Success criteria**: silhouette score of held-out trained embeddings ≥ 0.30.

### H_05C: Controls stay at chance (separation is *learned*, not architectural/compositional)
- **Success criteria**: untrained-model probe AUC ≤ 0.65 **and** composition probe
  AUC ≤ 0.65; both silhouettes ≤ 0.10. (Composition AUC is expected ≈ 0.5 by
  construction; the untrained control checks the architecture alone does not
  separate.)

### H_05D: The shared model still does the MLM job for both families
- **Success criteria**: masked motif-column accuracy ≥ 0.90 for **both** families
  (each family's motif is 100% conserved → Bayes-optimal ≈ 1.0), while background
  accuracy stays ≤ 0.15.

## Dependencies

- torch (CPU 2.12.1), numpy, matplotlib
- Reuses model/training/eval design from
  [`script_04_conservation_sweep.py`](../experiments/01_synthetic/script_04_conservation_sweep.py)
- Motivated by [`ANALYSIS_04.md`](../analysis/ANALYSIS_04.md) "next experiments" #2

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Seed | 1024 |
| Motif | `GKTYRG` (100% conserved) |
| Family A motif columns | 22–27 |
| Family B motif columns | 10–15 |
| Background | uniform, identical both families |
| Corpus | N=1000/family (2000 total), L=50 |
| Model | d_model=64, nhead=4, layers=2, ff=128 |
| Epochs / lr / batch / val | 30 / 1e-3 / 128 / 0.2 |
| Embedding | mean-pooled encoder output (64-d) |
| Probe | logistic regression (gradient descent, numpy/torch) |
| Metrics | AUC, silhouette, 2D PCA |

## Results

*(Filled in after experiment runs — see [`analysis/ANALYSIS_05.md`](../analysis/ANALYSIS_05.md))*

## Notes

- The model is **never** given family labels; separation, if it appears, is an
  emergent by-product of the masked-prediction objective.
- By design the composition probe is the strongest possible composition baseline
  and should sit at chance — this is the control that makes the "learned positional
  grammar" claim airtight (per KNOWN_PATTERNS §2.2).
- Both families use a fully conserved motif, so H_05D is essentially the
  two-family generalization of the script_03 motif-reconstruction result.
