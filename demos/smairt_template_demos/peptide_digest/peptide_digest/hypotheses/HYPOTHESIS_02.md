# Hypothesis 02: Missed Tryptic Cleavages Verification

## 1. Background

Standard tryptic digestion is rarely 100% efficient. In practical mass spectrometry search engines, we allow trypsin to occasionally skip a valid cleavage site, which produces longer, heavier peptides that span multiple fully-cleaved segments. These are referred to as **missed cleavages**. This iteration implements and validates a missed cleavage generator to expand our model's capacity toward realistic proteomics search spaces.

Research Question: `What tryptic peptides does a protein sequence produce, and which of those are MS-observable?`

## 2. Hypothesis

Allowing a maximum of $N$ missed cleavages will systematically expand the pool of candidate peptides by combining up to $N+1$ adjacent, fully-cleaved peptides. This will increase the total peptide yield and the average peptide length in a predictable, mathematically bounded manner.

Specifically:
1. When $N = 0$, the output will be identical to our canonical, fully-cleaved digestion.
2. For any sequence containing $M$ fully-cleaved peptide segments, the maximum number of peptides produced when allowing up to $N$ missed cleavages is bounded by the formula:
   $$\text{Max Peptides} = \sum_{k=1}^{N+1} \max(0, M - k + 1)$$
3. The average length of peptides produced under $N > 0$ will increase monotonically because missed-cleavage peptides are formed by stitching together adjacent smaller segments.

## 3. Experimental Design

We will modify or extend the digestion algorithm to support `max_missed_cleavages` in `experiments/01_synthetic/script_02_missed_cleavages_validation.py`. We will validate this code using the following deterministic test cases:

### Hand-Curated Verification Cases

#### Case A: `MKWVTFISLLR` (Cleavable segments: `["MK", "WVTFISLLR"]`, $M = 2$ segments)
* **$N = 0$ expected:** `["MK", "WVTFISLLR"]`
* **$N = 1$ expected:** `["MK", "WVTFISLLR", "MKWVTFISLLR"]`
* **$N = 2$ expected:** `["MK", "WVTFISLLR", "MKWVTFISLLR"]` (cannot form larger since $M=2$)

#### Case B: `AKR` (Cleavable segments: `["AK", "R"]`, $M = 2$ segments)
* **$N = 0$ expected:** `["AK", "R"]`
* **$N = 1$ expected:** `["AK", "R", "AKR"]`

#### Case C: `AKRGPK` (Cleavable segments: `["AK", "R", "GPK"]`, $M = 3$ segments)
* **$N = 0$ expected:** `["AK", "R", "GPK"]`
* **$N = 1$ expected:** `["AK", "R", "GPK", "AKR", "RGPK"]`
* **$N = 2$ expected:** `["AK", "R", "GPK", "AKR", "RGPK", "AKRGPK"]`

### Success Criteria (Metrics)
* **Exact-match validation rate:** 100% agreement on all expected peptide outputs across $N = 0, 1, 2$ missed cleavages for the test cases.
* **Segment Yield Metric:** The number of unique peptides generated for any sequence of $M$ segments must perfectly match the subset sum bound.

## 4. References & Context
* Background Document: [`smairt_template_demos/peptide_digest/background/01_initial_question.md`](smairt_template_demos/peptide_digest/background/01_initial_question.md)
* First Iteration Analysis: [`smairt_template_demos/peptide_digest/peptide_digest/analysis/ANALYSIS_01.md`](smairt_template_demos/peptide_digest/peptide_digest/analysis/ANALYSIS_01.md)
