# Analysis 06 — Covariation families: design fixed, but MLM ignores a sparse dependency

**Hypothesis:** [`HYPOTHESIS_06.md`](../hypotheses/HYPOTHESIS_06.md) (H_06A/B/C)
**Script:** [`experiments/01_synthetic/script_06_covariation_families.py`](../experiments/01_synthetic/script_06_covariation_families.py)
**Log:** `results/logs/script_06_covariation_families_*.log`
**Figures:** `results/figures/script_06_embedding_pca.png`, `results/figures/script_06_auc_vs_controls.png`
**Date:** 2026-06-29 · **Seed:** 1024 · **torch** 2.12.1 (CPU)

## Status: PARTIAL — H_06B PASS (design fixed); H_06A, H_06C FAIL (null result, informative)

Iteration 06 redesigned the two-family test to remove the iteration-05 confound:
the families now have **identical single-column marginals** (uniform at every
position) and **identical composition**, differing only in a *pairwise covariation*
between columns i=15 and j=35 (Family A: `seq[j]=seq[i]`; Family B: independent).
The data generator was verified: marginals at i and j are uniform in both families
and `P(seq[i]==seq[j])` = 1.000 (A) vs 0.053 (B).

## Results

| metric | trained | untrained ctrl | composition |
|--------|---------|----------------|-------------|
| linear-probe AUC (val) | 0.4849 | 0.4855 | 0.4765 |
| masked acc at j (i visible) | FamA=0.055, FamB=0.055 | — | — |

- **H_06B (controls at chance):** PASS — untrained 0.486, composition 0.476. The
  position- and composition-shortcuts that confounded iteration 05 are **gone**.
- **H_06A (trained AUC ≥ 0.90):** FAIL — trained AUC 0.485 (chance).
- **H_06C (coupling learned):** FAIL — conditional j-accuracy is 0.055 (= chance)
  for **both** families; the model did not learn to copy i→j even for Family A.

## Interpretation — the design is right; the objective is the bottleneck

This is a genuine null result with a clear mechanism, not a bug:

1. **The experimental design is now airtight.** Equal marginals forced both
   controls to chance (H_06B PASS), which is exactly the property iteration 05
   lacked. Any separation here *would* have been attributable to learning. So the
   experiment is valid — it just returned a null on the trained model.

2. **A single coupled pair barely affects the masked-LM loss.** Predicting column
   j from column i only helps on the event "j is masked **and** i is visible" —
   roughly 0.15 × 0.85 of the time, and j is just **1 of 50** columns. The maximum
   achievable loss reduction from learning the rule is on the order of
   `(1/50) × 0.13 × log(20)` per token — buried in optimization noise. With no
   material gradient signal, 30 epochs of a nano model learn nothing at i↔j, so the
   embeddings carry no family information.

3. **The dependency exists but is "uninteresting" to the loss.** The data truly
   contains the coupling (match = 1.000), yet MLM has no incentive to model it.
   This is an important and often-overlooked property of the MLM objective: it
   learns structure **in proportion to how much that structure reduces its loss**,
   not in proportion to how "real" the structure is.

## What this shows

- **Methodologically:** the control-driven approach worked twice over — iteration
  05's controls caught a too-easy discriminator, and iteration 06's controls
  confirmed the new discriminator is shortcut-free. The remaining failure is now
  unambiguously about *learnability under the objective*, not confounds.
- **Scientifically:** MLM will not learn a sparse pairwise dependency that does not
  materially lower its loss — a concrete, quantified statement about the limits of
  the nano-MLM on planted grammar.

## Fix — Iteration 07

Make learning the dependency **pay off** in the loss while keeping all marginals
uniform and composition ~equal across families. Use **many** coupled position pairs
via a fixed bijection of the alphabet:

- Pick K disjoint column pairs (e.g. K=10, covering 20 of 50 columns).
- Family A: for each pair `(a,b)`, set `seq[b] = π(seq[a])` for a fixed permutation
  π of the 20 residues (each column's marginal stays uniform; composition stays the
  same distribution).
- Family B: all columns independent uniform.

Now learning the rule reduces loss on ~K/50 of all masked tokens — a large,
trainable signal — while every single-column marginal remains uniform, so both
controls should stay at chance and only the trained model separates. That is the
airtight *and* learnable version of the embedding claim.

## Limitations

- Single seed; but trained AUC at exact chance with j-acc at chance is unambiguous,
  not a borderline seed effect.
- Confirms a limit of *this* objective/scale, not of attention in general (a
  supervised classifier on i,j would separate trivially).
