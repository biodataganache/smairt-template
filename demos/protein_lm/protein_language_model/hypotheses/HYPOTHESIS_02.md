# Hypothesis 02 — Nano-MLM beats the unigram baseline and reconstructs the motif

## Status: PENDING

## Background

Iteration 01 ([`ANALYSIS_01.md`](../analysis/ANALYSIS_01.md)) validated the
synthetic data generator: the P-loop motif `G-x-G-x-x-G` is planted exactly at
invariant columns `{22, 24, 27}` (100% glycine), the other 47 columns follow the
uniform background, the 15% masking plumbing is correct, and the corpus is
reproducible under seed 1024. Critically, it fixed the **unigram-frequency
baseline = 0.1076** (always-guess-glycine) — the exact bar a trained model must
beat to demonstrate any learning.

This iteration trains the tiny masked-language model and tests the main project
hypothesis (carried over as H_01C in [`HYPOTHESIS_01.md`](HYPOTHESIS_01.md)).

## Hypothesis Statement

**Prediction**: A tiny transformer (1–2 layers, embedding dim ~64, a few hundred
thousand parameters) trained with 15% masked-residue prediction on the iteration-01
synthetic corpus will (a) reach held-out masked-token accuracy clearly above the
0.1076 unigram baseline, and (b) predict the conserved-motif `G` positions
(columns 22/24/27) with near-1.0 accuracy while scoring variable/background
positions only near the background rate (~0.05). Masked cross-entropy loss drops
steadily with a reasonable train/val gap.

**Rationale**: The invariant `G` columns are perfectly determined by position/
context, so a model with positional information should learn them to ~1.0. The
background and variable `x` columns carry no learnable signal beyond the marginal
distribution, so accuracy there should sit near chance (~1/20). The contrast
between the two is the signature of having learned the *planted grammar* rather
than a global residue frequency.

**Success criteria**:
- Held-out overall masked accuracy **> 0.1076** by a clear margin.
- Masked accuracy on motif `G`-columns **≈ 1.0** (≥ 0.95), well above
  variable/background-column accuracy (~0.05–0.10).
- Train/val masked cross-entropy both decrease; val does not diverge upward.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_02_train_nano_mlm.py`
- **Phase**: synthetic
- **Track**: (none — sequential)
- **Data**: same generator/params as script_01 (seed 1024, N=2000, L=50, motif at 22–27)
- **Model**: token embedding (vocab 22 = 20 AA + `[MASK]` + `[PAD]`) + learned
  positional embedding, 2 `TransformerEncoder` layers, d_model=64, nhead=4,
  feedforward=128, then a linear head to vocab. A few hundred K params.
- **Training**: 15% dynamic masking per batch, Adam, masked cross-entropy on the
  masked positions only, fixed seed, train/val split (e.g. 80/20), ~tens of epochs.
- **Controls**: the unigram-frequency baseline (0.1076) from iteration 01.
- **Key metrics**: held-out masked accuracy (overall), per-column masked accuracy
  (esp. motif vs background), masked cross-entropy train/val curves.

## Sub-Hypotheses

### H_02A: Beat the baseline
- **Prediction**: held-out masked accuracy > 0.1076 by a clear margin.
- **Success criteria**: val masked accuracy ≥ 0.15 (and clearly above 0.1076).

### H_02B: Reconstruct the conserved motif
- **Prediction**: masked accuracy at columns {22,24,27} ≈ 1.0; background columns ~0.05.
- **Success criteria**: mean motif-column accuracy ≥ 0.95; background-column mean ≤ ~0.10.

### H_02C: Healthy learning curve
- **Prediction**: loss decreases steadily; modest train/val gap.
- **Success criteria**: val loss trends down and does not blow up.

## Dependencies

- torch (CPU build) — installed: torch 2.12.1
- numpy, matplotlib
- Reuses the generation logic and design constants from
  [`script_01_validate_generator.py`](../experiments/01_synthetic/script_01_validate_generator.py)
- Baseline target (0.1076) from [`ANALYSIS_01.md`](../analysis/ANALYSIS_01.md)

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Seed | 1024 |
| Corpus | N=2000, L=50, uniform background, motif G-x-G-x-x-G at cols 22–27 |
| Vocab | 22 (20 AA + [MASK] + [PAD]) |
| d_model / nhead / layers / ff | 64 / 4 / 2 / 128 |
| Mask rate | 0.15 (dynamic per batch) |
| Optimizer / lr | Adam / 1e-3 |
| Train/val split | 80 / 20 |
| Baseline to beat | 0.1076 |

## Results

*(Filled in after experiment runs — see [`analysis/ANALYSIS_02.md`](../analysis/ANALYSIS_02.md))*

## Notes

- Uniform background + perfectly invariant motif make this an easy, almost
  guaranteed win; that is intentional. The point is to confirm the training loop
  works and the model recovers a *known* signal before raising difficulty
  (biased background, motif jitter, two families) in later iterations.
