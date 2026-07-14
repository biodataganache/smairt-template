# Hypothesis 04 — Motif-recovery accuracy tracks the planted conservation level

## Status: PENDING

## Background

Iterations 01–03 established (a) a validated synthetic generator
([`ANALYSIS_01.md`](../analysis/ANALYSIS_01.md)) and (b) that the nano-MLM learns a
**fully** conserved motif perfectly, beating a discriminating baseline and reaching
the per-column information-theoretic ceiling ([`ANALYSIS_03.md`](../analysis/ANALYSIS_03.md)).
Both prior training runs used a 100%-invariant motif, which is trivially learnable.

The background document
([`01_initial_question.md`](../background/01_initial_question.md)) names the
genuinely interesting science: *"the interesting science is how accuracy tracks the
conservation level you set."* This iteration tests exactly that by planting the
motif at several conservation probabilities and measuring how motif-column accuracy
responds.

## Hypothesis Statement

**Prediction**: If each motif column is conserved with probability `p` (with prob
`1-p` it is drawn from the uniform background instead of its fixed residue), then
the model's recovered motif-column accuracy will be a **monotonically increasing
function of `p`**, approximately tracking the Bayes-optimal accuracy
`p + (1-p)/20` (guess the conserved residue; correct whenever it was conserved,
plus chance when it was not). Background-column accuracy stays at chance (~1/20)
for all `p`.

**Rationale**: At conservation `p`, the most likely residue at a motif column is
its conserved identity (for any `p > 1/20`), so a model that learns the column's
distribution should predict that residue and be right with probability
`p + (1-p)/20`. As `p` falls toward 1/20 the column becomes indistinguishable from
background and accuracy collapses to chance.

**Success criteria**: see sub-hypotheses.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_04_conservation_sweep.py`
- **Phase**: synthetic
- **Data**: motif `GKTYRG` at cols 22–27, each motif position conserved with
  probability `p ∈ {1.0, 0.9, 0.7, 0.5, 0.25}`; one corpus + model per `p`
- **Model/training**: identical to script_03 (d_model=64, 2 layers, 30 epochs)
- **Controls**: Bayes-optimal motif accuracy `p + (1-p)/20` per level; chance 1/20
- **Key metrics**: motif-column accuracy vs `p`, background accuracy vs `p`,
  agreement with the Bayes-optimal curve

## Sub-Hypotheses

### H_04A: Monotonic tracking
- **Success criteria**: mean motif-column accuracy is non-decreasing across
  increasing `p`, and strictly higher at p=1.0 than at p=0.25.

### H_04B: Near Bayes-optimal
- **Success criteria**: |measured motif accuracy − (p + (1-p)/20)| ≤ 0.10 at each
  level (with adequate signal; looser at the noisiest level).

### H_04C: Background stays at chance
- **Success criteria**: background-column mean accuracy ≤ 0.15 for every `p`.

## Dependencies

- torch (CPU 2.12.1), numpy, matplotlib
- Reuses model/training/eval design from
  [`script_03_discriminating_motif.py`](../experiments/01_synthetic/script_03_discriminating_motif.py)
- Motivated by [`ANALYSIS_03.md`](../analysis/ANALYSIS_03.md) "next experiments"

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Seed | 1024 |
| Motif | `GKTYRG` at cols 22–27 |
| Conservation levels `p` | 1.0, 0.9, 0.7, 0.5, 0.25 |
| Corpus | N=2000, L=50, uniform background |
| Model | d_model=64, nhead=4, layers=2, ff=128 |
| Epochs / lr / batch | 30 / 1e-3 / 128 |

## Results

*(Filled in after experiment runs — see [`analysis/ANALYSIS_04.md`](../analysis/ANALYSIS_04.md))*

## Notes

- Bayes-optimal reference per level: p=1.0→1.000, 0.9→0.905, 0.7→0.715, 0.5→0.525,
  0.25→0.2875. The key scientific output is the accuracy-vs-conservation curve,
  not a single pass/fail.
- Training five small models sequentially is still CPU-minutes.
