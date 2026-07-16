# Hypothesis 01 — Nano-MLM learns the planted protein grammar (validation-first)

## Status: PENDING

## Background

This is the first iteration of the protein language model SMAIRT project
(see [`background/01_initial_question.md`](../background/01_initial_question.md)).
A nano masked-language model (MLM) will be trained on a synthetic protein-like
corpus whose grammar we control: a uniform background residue distribution with
a conserved P-loop motif `G-x-G-x-x-G` planted at fixed positions. Because the
ground truth is planted, we can verify exactly what the model should learn.

Following SMAIRT discipline, **this iteration validates the synthetic data
generator before any model is trained**. If the generator does not plant the
grammar correctly, every downstream model result is meaningless. The training
hypothesis below is therefore stated in full, but the script for iteration 01
(`script_01_validate_generator.py`) tests only the generator and the
training-data plumbing — no model is fit yet.

## Hypothesis Statement

**Prediction**: A tiny transformer (1–2 layers, embedding dim ~64, a few hundred
thousand parameters) trained with ~15% masked-residue prediction on a
single-family synthetic corpus will (a) reach held-out masked-token accuracy
clearly above the unigram-frequency baseline, and (b) predict the conserved-motif
`G` positions with near-1.0 accuracy while scoring variable positions only near
the background rate. The masked cross-entropy loss drops steadily with a
reasonable train/val gap.

**Rationale**: The conserved `G` columns are perfectly predictable from context
(they are invariant by construction), so any model that learns position-aware
context should nail them. Background/variable positions carry no learnable signal
beyond the unigram distribution, so accuracy there should sit near chance. The
gap between these two is the signature that the model learned the planted grammar
rather than memorizing a marginal residue frequency.

**Success criteria**:
- Held-out masked-token accuracy > unigram-frequency baseline by a clear margin.
- Motif `G`-position masked accuracy ≈ 1.0 (well above variable-position accuracy).
- Masked cross-entropy loss decreases steadily; train/val gap stays modest.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_01_validate_generator.py`
- **Phase**: synthetic
- **Track**: (none — early sequential numbering)
- **Data**: synthetic protein-like corpus generated in-script (no external data)
- **Controls**: unigram-frequency masked-prediction baseline (computed here so the
  exact bar exists before any model is trained)
- **Key metrics (this iteration)**: per-column residue frequencies, motif-position
  residue identity, unigram baseline accuracy, masking-rate / label-integrity
  checks, reproducibility under fixed seed

## Sub-Hypotheses

### H_01A: Generator plants the conserved motif exactly (THIS ITERATION)
- **Prediction**: Invariant motif columns `{22, 24, 27}` are 100% glycine; all
  other columns follow the uniform background (~0.05 per residue) with no
  glycine-dominated column outside the invariant set.
- **Success criteria**: Glycine frequency `== 1.0` at invariant columns; every
  non-invariant column's residue frequencies within a binomial 3σ band of 1/20;
  assertions pass.

### H_01B: Training-data plumbing is correct (THIS ITERATION)
- **Prediction**: Applying 15% masking yields ≈15% masked positions and stored
  targets that exactly equal the pre-mask residues (no label leakage).
- **Success criteria**: |masked fraction − 0.15| within tolerance; targets match
  originals at all masked positions.

### H_01C: Nano-MLM beats baseline and reconstructs the motif (NEXT ITERATION)
- **Prediction**: See main hypothesis statement (deferred to `script_02`).
- **Success criteria**: Held-out accuracy > baseline; motif-position accuracy ≈ 1.0.

## Dependencies

- Shared logging: `scripts/shared/TeeLogger`, `setup_logging`
- numpy (corpus generation, frequency tables), matplotlib (figures)
- No prior scripts; this is iteration 01

## Design Parameters (fixed for reproducibility)

| Parameter | Value |
|-----------|-------|
| Random seed | 1024 |
| Sequence length L | 50 |
| Number of sequences N | 2000 |
| Alphabet | 20 standard AAs (ACDEFGHIKLMNPQRSTVWY) |
| Background distribution | uniform over 20 AAs |
| Conserved motif | G-x-G-x-x-G (P-loop / Walker-A) |
| Motif start column (0-based) | 22 (occupies columns 22–27) |
| Invariant (G) columns | {22, 24, 27} |
| Variable (x) columns | {23, 25, 26} |
| Mask rate | 0.15 |

## Results

*(Filled in after experiment runs — see [`analysis/ANALYSIS_01.md`](../analysis/ANALYSIS_01.md) for full interpretation)*

## Notes

- This iteration deliberately trains no model. Its sole job is to make the
  planted ground truth trustworthy and to fix the exact unigram baseline that
  `script_02` must beat.
- Uniform background is the simplest known truth; a biased (real-protein-like)
  background and motif-position jitter are deferred to later rungs of the
  fidelity ladder.
