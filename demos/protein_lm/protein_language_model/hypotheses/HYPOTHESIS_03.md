# Hypothesis 03 — Discriminating motif makes the baseline comparison meaningful

## Status: PENDING

## Background

Iteration 02 ([`ANALYSIS_02.md`](../analysis/ANALYSIS_02.md)) found that the
nano-MLM learned the all-glycine motif **perfectly** (motif columns 1.000,
background 0.048 = chance, healthy loss curve), but overall masked accuracy
(0.1072) **tied** the unigram-frequency baseline (0.1076). Root cause: the
planted motif residue (glycine) was exactly the baseline's single guess, and 47
of 50 columns are unlearnable uniform noise that dominates the average. The
metric, not the model, was at fault.

This iteration fixes the experiment so the baseline comparison becomes a real
test of learning.

## Hypothesis Statement

**Prediction**: With a **multi-residue conserved motif** `GKTYRG` (six distinct
fixed residues, not all the global mode), the nano-MLM will (a) achieve overall
masked accuracy **clearly above the global-unigram baseline**, (b) reconstruct
all six motif columns at ~1.0 accuracy while background columns stay at chance
(~1/20), (c) **match the per-column-optimal accuracy ceiling**, and (d) show a
healthy decreasing loss curve.

**Rationale**: A single-residue global-unigram baseline can match at most the one
motif column whose residue equals the global mode; it gets the other five motif
columns wrong. The model, having learned the positional grammar, gets all six
right, so its overall accuracy must exceed the global baseline. The per-column
baseline (guess each column's own mode) is the information-theoretic ceiling; a
fully-trained model should reach it.

**Success criteria**: see sub-hypotheses.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_03_discriminating_motif.py`
- **Phase**: synthetic
- **Data**: same generator/params, motif swapped to `GKTYRG` at cols 22–27
- **Model/training**: identical to script_02 (d_model=64, 2 layers, 30 epochs)
- **Controls**: TWO baselines — global-unigram (non-discriminating before) and
  per-column-optimal (the ceiling)
- **Key metrics**: overall masked acc, per-column acc, both baselines, loss curve

## Sub-Hypotheses

### H_03A: Beat the global-unigram baseline
- **Success criteria**: overall val acc > global baseline + 0.02.

### H_03B: Reconstruct the conserved motif
- **Success criteria**: mean motif-column acc ≥ 0.95; background mean ≤ 0.15.

### H_03C: Reach the per-column ceiling
- **Success criteria**: |overall acc − per-column-optimal acc| ≤ 0.03.

### H_03D: Healthy learning curve
- **Success criteria**: final val loss < initial val loss.

## Dependencies

- torch (CPU, 2.12.1), numpy, matplotlib
- Reuses model/training design from
  [`script_02_train_nano_mlm.py`](../experiments/01_synthetic/script_02_train_nano_mlm.py)
- Motivated by [`ANALYSIS_02.md`](../analysis/ANALYSIS_02.md)

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Seed | 1024 |
| Motif | `GKTYRG` (6 distinct conserved residues) at cols 22–27 |
| Corpus | N=2000, L=50, uniform background |
| Model | d_model=64, nhead=4, layers=2, ff=128 |
| Epochs / lr / batch | 30 / 1e-3 / 128 |

## Results

*(Filled in after experiment runs — see [`analysis/ANALYSIS_03.md`](../analysis/ANALYSIS_03.md))*

## Notes

- Expected baselines (uniform background, 6-residue motif): global-unigram ≈
  (1 + 44/20)/50 ≈ 0.064 if the motif's modal residue is unique to one column;
  per-column-optimal ≈ (6 + 44/20)/50 ≈ 0.164. The model should land near 0.164.
