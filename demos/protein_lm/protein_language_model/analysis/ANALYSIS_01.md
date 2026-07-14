# Analysis 01 — Synthetic generator validation (pre-training)

**Hypothesis:** [`HYPOTHESIS_01.md`](../hypotheses/HYPOTHESIS_01.md) (H_01A, H_01B)
**Script:** [`experiments/01_synthetic/script_01_validate_generator.py`](../experiments/01_synthetic/script_01_validate_generator.py)
**Log:** `results/logs/script_01_validate_generator_*.log`
**Figures:** `results/figures/script_01_glycine_by_column.png`,
`results/figures/script_01_column_residue_heatmap.png`
**Date:** 2026-06-29 · **Seed:** 1024

## Status: H_01A SUPPORTED · H_01B SUPPORTED (generator trustworthy)

No model was trained this iteration — by design. The sole goal was to make the
planted ground truth trustworthy before any training, per SMAIRT discipline.

## What was tested

A synthetic corpus of N=2000 sequences, length 50, was drawn from a uniform
background over 20 amino acids, with the P-loop motif `G-x-G-x-x-G` planted at
columns 22–27. The invariant `G` columns are `{22, 24, 27}`; the variable `x`
columns are `{23, 25, 26}`.

## Results

| Check | Result | Evidence |
|-------|--------|----------|
| Invariant cols 100% glycine (H_01A) | **PASS** | glycine freq = 1.0000 at cols 22, 24, 27 |
| Non-invariant cols ~ uniform background (H_01A) | **PASS** | chi-square GOF vs uniform, df=19; max χ²=33.06 < crit 43.82 (α=0.001); 0 rejections across 47 cols |
| No stray glycine-dominated cols | **PASS** | none with glycine > 2×(1/20) outside motif |
| 15% masking rate (H_01B) | **PASS** | observed 0.1496 vs target 0.15 |
| No label leakage (H_01B) | **PASS** | all masked positions hidden; targets recover pre-mask residues exactly |
| Reproducibility | **PASS** | regeneration with seed 1024 byte-identical |

**Unigram-frequency baseline = 0.1076.** The globally most common residue is
glycine (freq 0.1076), matching the analytic prediction of 0.1070
(`(3 + 47/20)/50`). This is the **exact bar the nano-MLM in `script_02` must
beat**.

The figures confirm the structure visually: the glycine-by-column bar chart is
flat at ~0.05 everywhere except sharp spikes to 1.0 at columns 22/24/27, and the
column×residue heatmap shows a single bright cell at the G row in exactly those
three columns.

## Interpretation

The generator plants the grammar precisely where intended and nowhere else. The
variable `x` motif columns (23, 25, 26) behave like ordinary background columns,
which is correct: only the three `G` columns carry signal. This gives a clean,
falsifiable target for the model:

- A model that has learned the grammar should reach **~1.0 accuracy on masked
  `G`-columns** (22/24/27) and only **~0.05–0.11 on variable/background columns**.
- Overall masked accuracy must exceed **0.1076** to claim any learning beyond the
  trivial "always guess glycine" predictor.

## Methodological note (caught and fixed this iteration)

The first run **failed** a check: two background columns (15, 18) tripped a
per-frequency 3σ band (deviation 0.0150 vs tol 0.0146). This was a flaw in the
*check*, not the data — testing 47×20 = 940 individual frequencies against a
per-estimate 3σ threshold expects ~2.5 chance exceedances (a multiple-comparisons
error). Replaced with a per-column chi-square goodness-of-fit test against
uniform (df=19, α=0.001), which correctly treats each column's full distribution
as one test. All columns then passed. Worth recording in `KNOWN_PATTERNS.md` as
an anti-pattern: *don't apply per-element σ-bands across many estimates without a
multiple-comparisons correction.*

## Limitations

- Uniform background is the simplest possible truth; real proteins have biased
  residue frequencies. A biased background is deferred to a later rung.
- The motif is perfectly invariant and at a fixed position — trivially learnable.
  The interesting science (how accuracy tracks conservation level, and motif
  jitter) comes in later iterations.
- This validates mechanism/plumbing only, not biological insight.

## Next experiment

**`script_02_train_nano_mlm.py`** (still Phase 1 / synthetic): train a tiny
1–2 layer transformer (~embed 64) with 15% masked-residue prediction on this
exact corpus. Report held-out masked accuracy vs the **0.1076** baseline,
per-column accuracy (expecting ~1.0 at cols 22/24/27), and the train/val loss
curve. This tests H_01C (the main training hypothesis).
