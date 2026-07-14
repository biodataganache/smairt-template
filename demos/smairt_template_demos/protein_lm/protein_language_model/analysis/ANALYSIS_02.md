# Analysis 02 — Nano-MLM training: model learned the grammar, baseline metric was flawed

**Hypothesis:** [`HYPOTHESIS_02.md`](../hypotheses/HYPOTHESIS_02.md) (H_02A, H_02B, H_02C)
**Script:** [`experiments/01_synthetic/script_02_train_nano_mlm.py`](../experiments/01_synthetic/script_02_train_nano_mlm.py)
**Log:** `results/logs/script_02_train_nano_mlm_*.log`
**Figures:** `results/figures/script_02_loss_curve.png`,
`results/figures/script_02_per_column_accuracy.png`
**Date:** 2026-06-29 · **Seed:** 1024 · **torch** 2.12.1 (CPU)

## Status: H_02B SUPPORTED · H_02C SUPPORTED · H_02A INCONCLUSIVE (metric flaw, not model failure)

## Results

A 72,982-parameter nano transformer (d_model=64, 4 heads, 2 layers) trained for
30 epochs on 1600 train / 400 val sequences.

| Metric | Value | Target | Verdict |
|--------|-------|--------|---------|
| Motif G-column accuracy (cols 22/24/27) | **1.000, 1.000, 1.000** | ≥ 0.95 | H_02B PASS |
| Background-column mean accuracy | **0.0483** (≈ 1/20) | ≤ 0.15 | H_02B PASS |
| Val loss trajectory | 2.962 → 2.819 (steady ↓) | decreasing | H_02C PASS |
| Overall masked accuracy | **0.1072** | > 0.1076 baseline | H_02A FAIL (tie) |

## Interpretation — the model is actually Bayes-optimal

The model did exactly what a correct model should do:

- It learned the **conserved motif perfectly** — 100% accuracy on all three
  invariant `G` columns, demonstrating it discovered the positional grammar.
- It scored background columns at **0.048 ≈ 1/20 = chance**, which is *correct*:
  the background is drawn uniformly at random and carries **no learnable signal**,
  so no model (however large) can exceed chance there.

These two facts mean the model reached the **information-theoretic ceiling**.
H_02A nonetheless "failed" — and that exposes a flaw in my experimental design,
not in the model.

## Root cause: the baseline metric was non-discriminating

The unigram-frequency baseline always guesses the single most-common residue,
which is **glycine** — and glycine is the most common residue *only because the
planted motif is made of glycine*. So the baseline gets the 3 motif columns
"for free" (they are all G) plus background-G at 1/20:

```
baseline overall = (3 + 47 × 1/20) / 50 = 0.107
model    overall = (3 × 1.0 + 47 × 1/20) / 50 = 0.107   (identical)
```

Both the trivial baseline and the perfect model land on the same overall number.
**Overall masked accuracy cannot distinguish them** because (a) 47 of 50 positions
are unlearnable noise that dominates the average, and (b) the motif residue
coincides with the baseline's single guess. The model decisively wins where it
*matters* — the conserved positions — but that signal is diluted to invisibility
in the overall average.

This is a genuine, instructive SMAIRT finding: **validate-on-synthetic surfaced a
metric design error before it could mislead us on real data.**

## Fix (next iteration)

Two complementary changes make H_02A meaningful:

1. **Per-position comparison (primary):** compare the model's motif-column
   accuracy against a *per-column* most-common-residue baseline. On background
   columns both tie at ~1/20; on motif columns the model hits 1.0 while a
   position-blind unigram baseline cannot. This isolates the learnable signal.
2. **Non-modal / multi-residue motif (corpus change):** replace the all-glycine
   motif with a motif of **distinct conserved residues** that are *not* the global
   mode (e.g. a Walker-A-like `G-K-T` with several fixed non-G residues). Then a
   single-residue unigram baseline can capture at most one motif position, and the
   model's overall accuracy will clearly exceed the baseline because it nails
   several conserved positions the baseline cannot.

Planned as **`script_03_discriminating_motif.py`**: keep the validated generator,
swap to a multi-residue conserved motif, and report both the per-column baseline
and overall accuracy so H_02A becomes a real test.

## Limitations

- The current corpus's background is pure noise; real proteins have correlated,
  biased residues, so background accuracy above chance is expected later.
- A perfectly invariant motif is trivially learnable; the interesting science
  (accuracy vs conservation level, motif jitter, two-family separation) is still
  ahead on the fidelity ladder.

## Candidate KNOWN_PATTERNS entry

> **Anti-pattern: averaging a metric over mostly-unlearnable positions.** When most
> positions carry no signal, overall accuracy is dominated by the noise floor and
> can tie a trivial baseline even for a perfect model. Always report per-position
> (or per-stratum) metrics, and design baselines that are *discriminating* on the
> positions of interest. (Also: don't let the planted signal coincide with the
> baseline's guess.)
