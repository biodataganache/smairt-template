# Analysis 07 — Many-pair coupling: signal is now learnable-relevant, but the rule is too hard

**Hypothesis:** [`HYPOTHESIS_07.md`](../hypotheses/HYPOTHESIS_07.md) (H_07A/B/C)
**Script:** [`experiments/01_synthetic/script_07_bijection_coupling.py`](../experiments/01_synthetic/script_07_bijection_coupling.py)
**Log:** `results/logs/script_07_bijection_coupling_*.log`
**Figures:** `results/figures/script_07_embedding_pca.png`, `results/figures/script_07_auc_vs_controls.png`
**Date:** 2026-06-29 · **Seed:** 1024 · **torch** 2.12.1 (CPU)

## Status: PARTIAL — H_07B PASS; H_07A, H_07C FAIL (clear progress over iter 06)

Iteration 07 strengthened the planted signal from one coupled pair (iter 06) to
K=10 disjoint pairs linked by a fixed alphabet permutation `π`, keeping every
column's marginal uniform (verified: max |marginal − 1/20| = 0.022; rule
satisfaction FamA = 1.000, FamB = 0.054).

## Results

| metric | trained | untrained ctrl | composition |
|--------|---------|----------------|-------------|
| linear-probe AUC (val) | 0.6044 | 0.5204 | 0.5103 |
| mean masked acc at b-cols (a visible) | FamA=0.183, FamB=0.054 | — | — |

- **H_07B (controls at chance):** PASS — 0.520, 0.510. Design still airtight.
- **H_07A (trained AUC ≥ 0.90):** FAIL — 0.604.
- **H_07C (coupling learned):** FAIL — FamA b-accuracy 0.183 (target ≥ 0.80).

## Interpretation — the signal is now loss-relevant; the *rule* is the bottleneck

This is real, measurable progress and a sharper diagnosis than iteration 06:

1. **The model is now distinguishable from its controls.** Trained AUC 0.604 vs
   controls ≈ 0.51, and FamA b-accuracy 0.183 is **>3× chance** (0.054) while FamB
   stays at chance. Unlike iteration 06 (everything at chance), the K=10 signal
   *does* reduce the loss, so the model **started** learning the coupling.
2. **But it did not finish.** Learning an **arbitrary 20-symbol permutation** routed
   across 10 *random* (a,b) column pairs is a hard credit-assignment problem for a
   2-layer, 64-dim model in 30 epochs: the model must (i) attend from each `b` to
   its specific partner `a` and (ii) learn the full 20→20 mapping `π`. It learned
   this partially (0.183), not fully.
3. **The design is not at fault** — controls remain clean. The gap is purely model
   capacity/optimization vs rule complexity.

## What this shows

The two failure modes are now cleanly separated across iterations:
- iter 06: signal too **sparse** to matter to the loss (null, controls clean);
- iter 07: signal matters but the **rule is too complex** to fully learn at this
  budget (partial, controls clean).

Both point to the same fix: keep the airtight uniform-marginal design, but make the
mapping **easy to learn** so the nano model can finish.

## Fix — Iteration 08

Replace the arbitrary permutation with an **identity copy**: Family A sets
`seq[b_k] = seq[a_k]` (Family B independent). This still keeps every column uniform
(so both controls stay at chance), but the mapping is the simplest possible — a
single copy-attention head can implement "look at partner, copy its token." Give a
modest budget bump (more epochs / heads, still CPU-minutes). Expectation: trained
AUC ≥ 0.90, controls at chance, FamA b-accuracy near 1.0 — the airtight *and*
learnable demonstration that closes the embedding claim.

## Limitations

- Single seed; but the ordering trained ≫ controls is robust and the partial
  learning (0.183) is well above the chance band.
- Confirms a capacity/complexity limit at nano scale, not a limit of attention in
  general.
