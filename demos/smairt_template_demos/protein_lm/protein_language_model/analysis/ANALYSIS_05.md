# Analysis 05 — Two-family embeddings: separation is real, but the test could not isolate "learning"

**Hypothesis:** [`HYPOTHESIS_05.md`](../hypotheses/HYPOTHESIS_05.md) (H_05A/B/C/D)
**Script:** [`experiments/01_synthetic/script_05_two_family_embeddings.py`](../experiments/01_synthetic/script_05_two_family_embeddings.py)
**Log:** `results/logs/script_05_two_family_embeddings_*.log`
**Figures:** `results/figures/script_05_embedding_pca.png`, `results/figures/script_05_separability_metrics.png`
**Date:** 2026-06-29 · **Seed:** 1024 · **torch** 2.12.1 (CPU)

## Status: PARTIAL — H_05A, H_05D PASS; H_05B, H_05C FAIL (informative — design flaw surfaced)

This iteration tested the last open claim in the project hypothesis: that
mean-pooled embeddings **separate two planted families**. The two families share
the identical motif `GKTYRG` and differ **only by motif position** (Family A at
cols 22–27, Family B at cols 10–15) on a uniform background, so per-sequence
composition is identical by construction. The result is a clean, honest PARTIAL
that taught us something about experimental design.

## Results

| metric | trained model | untrained ctrl | composition |
|--------|---------------|----------------|-------------|
| linear-probe AUC (val) | **0.9998** | 0.9785 | **0.4864** |
| silhouette (val) | 0.0575 | 0.0040 | −0.0010 |
| motif MLM acc | FamA=1.000, FamB=1.000 | — | — |
| background MLM acc | 0.056 | — | — |

- **H_05A (trained AUC ≥ 0.95):** PASS — 0.9998. Embeddings are almost perfectly
  linearly separable by family.
- **H_05D (both-family MLM ≥ 0.90):** PASS — the single shared model reconstructs
  *both* families' motifs perfectly (1.000) with background pinned at chance
  (0.056). One model learned two positional motifs simultaneously.
- **H_05B (silhouette ≥ 0.30):** FAIL — 0.0575.
- **H_05C (controls at chance):** FAIL — composition is at chance (0.486, exactly
  as designed) but the **untrained** random-init model separates (0.978).

## Interpretation — two distinct lessons

### 1. The composition control worked perfectly (the part we got right)
Composition AUC = **0.486** ≈ chance. By making both families carry the identical
residue multiset, we proved the separation is **not** a bag-of-residues shortcut.
This directly answers the §2.2 anti-pattern from
[`KNOWN_PATTERNS.md`](../prompts/KNOWN_PATTERNS.md): a non-discriminating baseline
was deliberately constructed and confirmed at chance.

### 2. The discriminator was too easy — position is "free" (the part we got wrong)
The untrained model separates the families at AUC 0.978. The reason is mechanical:
the model adds **position embeddings** before the encoder, so even with random
weights, a sequence with its motif at cols 22–27 lands in a different region of
embedding space than one with the motif at cols 10–15. **Motif position is encoded
by the architecture, not by learning.** H_05C correctly flagged this: a
position-only family difference cannot demonstrate *learned* grammar, because the
position channel is present at initialization.

This is the same class of error as iteration 02's metric flaw — the *measurement
setup*, not the model, was the problem — and exactly why the control was included.
The control did its job.

### 3. Silhouette was the wrong metric (a secondary issue)
AUC = 0.9998 with silhouette = 0.0575 is the classic high-dimensional signature:
the classes are perfectly separable along a **single** direction, but Euclidean
silhouette averaged over 64 mostly-uninformative dimensions is dominated by noise
and understates the separation. AUC (or silhouette computed in the discriminant
subspace / after PCA) is the appropriate metric for a "separable?" claim.

## What this does and does not show

- **Does show:** a single nano-MLM can learn two positional motifs at once
  (H_05D), and its embeddings are trivially family-separable — but *triviality* is
  the point: a random network does it too.
- **Does not show:** that *training* is what creates separable family structure.
  To claim that, the family difference must be invisible both to composition (✓
  already) **and** to position embeddings (✗ — needs a new design).

## Fix — Iteration 06 design

Use a discriminator that only **attention over content** can capture: a **pairwise
covariation** rule. Both families have the motif at the *same* fixed columns, so
position is identical; both have identical marginal composition. They differ only
in a **correlation** between two residue positions:

- Family A: positions `i` and `j` are **coupled** (e.g. always the same residue,
  or one determines the other).
- Family B: positions `i` and `j` are **independent** (each drawn freely).

Marginals (composition) and positions are identical across families ⇒ both the
composition control **and** the untrained control should drop to **chance**. Only a
model that has *learned* the i–j dependency (via self-attention) can separate them.
That is the airtight test of "learned grammar drives family separation."

## Limitations

- Single seed; AUC is high enough that seed variation is unlikely to change H_05A,
  but the iteration-06 controls should be checked across ≥2 seeds.
- Silhouette retained as a reported metric but de-emphasized in favor of AUC; an
  in-subspace silhouette could be added.
