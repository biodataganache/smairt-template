# 01_initial_question.md

## Brief Background

In a quantitative proteomics experiment, you measure the abundance of thousands
of proteins across two conditions (for example **treated vs. control**). The
core question is almost always the same: **which proteins changed, and can we
trust that the change is real rather than noise?**

This SMAIRT project answers that question in a simplified but realistic way. We
**generate a synthetic protein-abundance matrix with a known, planted answer**:
we decide in advance which proteins are truly up- or down-regulated and by how
much, add realistic measurement noise, and then ask the analysis to *recover*
those planted proteins. Because we know the ground truth, we can measure whether
the method works before ever touching messy real data. This is the same
"validate on synthetic first" discipline used in the lunar demo, applied to a
biology workflow.

It is CPU-only, pure Python (numpy/pandas/scipy/statsmodels), and needs no
external data to get started.

## Question

Given a two-condition protein-abundance matrix, which proteins are
**differentially abundant**, and how well can a per-protein test plus
multiple-testing correction **recover the proteins we know are truly changed**
while controlling false positives?

## Hypothesis

A per-protein two-sample t-test on log-transformed abundances, followed by
Benjamini-Hochberg (BH) false-discovery-rate correction, will recover most of
the planted true-positive proteins at a chosen FDR threshold while keeping the
observed false-discovery rate near that threshold. Without correction, the raw
p-value cutoff will produce far too many false positives because we are testing
thousands of proteins at once.

## Evidence / metrics

- **Recall (sensitivity):** fraction of planted true-DE proteins called
  significant.
- **Observed FDR:** fraction of called-significant proteins that were *not*
  planted as truly changed (should track the chosen BH threshold, e.g. 0.05).
- **Volcano plot:** log2 fold-change (x) vs. -log10 p-value (y), with planted
  true positives highlighted, as the visual sanity check.
- **Calibration:** without BH correction, count how many of the "significant"
  proteins are actually null (illustrates the multiple-testing problem).

## Domain Context

### What the data looks like
- A matrix of `n_proteins` rows (e.g. 2,000) by `n_samples` columns (e.g. 5
  control + 5 treated replicates).
- Values are intensities; analysis is done on **log2** intensities, where
  fold-changes become differences and noise is roughly normal.
- A small, known subset of proteins (e.g. 100) is **planted** with a real
  effect (a fixed log2 fold-change). The rest are null (no true difference).

### Why multiple-testing correction matters
- Testing 2,000 proteins at p < 0.05 yields ~100 false positives **by chance
  alone**, even if nothing changed.
- BH-FDR controls the *expected proportion* of false positives among your hits,
  which is the standard in omics. Recovering the planted set at controlled FDR
  is the success condition.

### Fidelity ladder (SMAIRT data progression)
1. **Synthetic:** planted effects + Gaussian noise, no missing values. Confirm
   recall and FDR behave as expected. (Start here.)
2. **Synthetic, harder:** add log-normal noise, a few high-variance proteins,
   and **missing values** (proteins not detected in some samples). Decide how to
   handle them (filter vs. impute) and show the effect on recall/FDR.
3. **Real (optional, later):** swap in a small published `proteinGroups`-style
   intensity table (a handful of proteins x samples). The ground-truth set is no
   longer known, so you now reason about effect sizes and prior biology instead
   of exact recall. State that shift honestly.

### Caveats
- A t-test assumes roughly normal log-intensities and equal-ish variance;
  real proteomics violates this (heteroscedasticity, missingness not at random).
  Part of the SMAIRT method is naming these limits next to the result.
- "Significant" is not "biologically important." Fold-change direction and
  magnitude matter alongside the p-value, which is why the volcano plot pairs
  them.

## Known parameters (suggested starting values)

| Quantity | Value |
|----------|-------|
| proteins | 2,000 |
| samples | 5 control + 5 treated |
| planted true-DE proteins | 100 |
| planted log2 fold-change | ~1.0 (2x) |
| measurement noise (log2 SD) | ~0.3 |
| BH-FDR threshold | 0.05 |
| random seed | fixed (reproducibility) |
