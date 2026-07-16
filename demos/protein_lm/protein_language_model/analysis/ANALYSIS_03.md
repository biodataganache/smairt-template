# Analysis 03 — Nano-MLM learns the planted grammar (corrected, discriminating metric)

**Hypothesis:** [`HYPOTHESIS_03.md`](../hypotheses/HYPOTHESIS_03.md) (H_03A/B/C/D)
**Script:** [`experiments/01_synthetic/script_03_discriminating_motif.py`](../experiments/01_synthetic/script_03_discriminating_motif.py)
**Log:** `results/logs/script_03_discriminating_motif_*.log`
**Figures:** `results/figures/script_03_loss_curve.png`,
`results/figures/script_03_per_column_accuracy.png`
**Date:** 2026-06-29 · **Seed:** 1024 · **torch** 2.12.1 (CPU)

## Status: ALL SUPPORTED — H_03A, H_03B, H_03C, H_03D PASS

This iteration applied the fix prescribed in [`ANALYSIS_02.md`](ANALYSIS_02.md):
a **multi-residue conserved motif** `GKTYRG` (six distinct fixed residues instead
of all glycine) and **two baselines** (global-unigram and per-column-optimal).

## Results

| Metric | Value | Target | Verdict |
|--------|-------|--------|---------|
| Overall masked accuracy | **0.1600** | > global baseline (0.0840) + 0.02 | H_03A PASS |
| Motif-column accuracy (cols 22–27) | **1.000 × 6** (mean 1.0000) | ≥ 0.95 | H_03B PASS |
| Background-column mean | **0.0514** (≈ 1/20) | ≤ 0.15 | H_03B PASS |
| vs per-column ceiling | 0.1600 vs **0.1640** | within 0.03 | H_03C PASS |
| Val loss | 2.899 → 2.661 (steady ↓) | decreasing | H_03D PASS |

## Interpretation — the original project hypothesis is now confirmed

With the discriminating design, the picture is unambiguous:

- **The model beats the global-unigram baseline by ~2×** (0.160 vs 0.084). The
  baseline can only ever get one motif column right (whichever residue happens to
  be the global mode — here a stray glycine), so it tops out near 0.084. The model
  gets **all six** motif columns, lifting overall accuracy to 0.160.
- **The model reaches the information-theoretic ceiling** (0.160 ≈ 0.164). The
  remaining gap to 1.0 is pure background noise that *no* model can predict — and
  the model correctly sits at chance (0.051) there, confirming it is not
  hallucinating structure in the noise.
- **Every conserved position is reconstructed perfectly** (1.000 across all six),
  which is the direct evidence that the nano transformer learned the *planted
  grammar* — the positional rule that columns 22–27 are fixed to G,K,T,Y,R,G.

This validates the project's core hypothesis from
[`background/01_initial_question.md`](../background/01_initial_question.md): a tiny
masked-language model trained on synthetic protein-like sequences recovers the
signal it was given, beating a frequency baseline and nailing the conserved motif.

## Why iteration 02 "failed" and this one passes (the lesson)

Nothing about the *model* changed — same architecture, same training. Only the
**experiment design** changed: the motif now contains residues the unigram
baseline cannot all guess, and we measure against a per-column ceiling. The
model's behavior was correct all along (ANALYSIS_02 showed motif=1.0, bg=chance);
iteration 02's overall-accuracy metric simply could not *see* that success. This
is the SMAIRT method working as intended: synthetic data with known truth exposed
a measurement flaw before it could mislead us on real data.

## Limitations

- The motif is perfectly invariant (100% conserved) and at a fixed position —
  trivially learnable. The scientifically interesting questions are still ahead:
  how accuracy tracks **conservation level** (a partially-conserved motif),
  robustness to **positional jitter**, and **two-family separation** via
  mean-pooled embeddings (Rung 2 of the fidelity ladder).
- Uniform background is unrealistic; real proteins have biased, correlated
  residues, so background accuracy above chance is expected on real data.

## Next experiments (Rung 2 — synthetic, harder)

1. **Conservation sweep:** make the motif conserved at p ∈ {1.0, 0.9, 0.7, 0.5}
   and show motif-column accuracy tracks the planted conservation level (the
   "interesting science" called out in the background).
2. **Positional jitter:** randomize the motif start ±k columns and confirm the
   model still localizes it.
3. **Two families:** plant two motifs/compositions and test whether mean-pooled
   per-sequence embeddings separate the families (silhouette / logistic-regression
   AUC), per the project's Rung-2 hypothesis.

## KNOWN_PATTERNS entry earned this iteration

> **Anti-pattern (confirmed & resolved): non-discriminating baseline + noise-diluted
> average.** A global most-common-residue baseline ties a perfect model when (a)
> the planted signal residue equals the baseline's guess and (b) most positions are
> unlearnable. Fix: use multi-residue signals and report per-position metrics plus a
> per-column optimal baseline (the ceiling). Recommend adding to
> [`prompts/KNOWN_PATTERNS.md`](../prompts/KNOWN_PATTERNS.md) §2.
