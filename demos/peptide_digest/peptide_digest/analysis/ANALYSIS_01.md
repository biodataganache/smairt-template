# Analysis 01: Canonical Trypsin Digestion Verification

## 1. Background

Our first experimental step focused on implementing and validating a deterministic, pure-Python *in-silico* tryptic digest algorithm. Because trypsin follows precise cleavage rules, we wanted to ensure that N- and C-terminal sequences, canonical cleavage points (cleave C-terminal to `K` or `R`), and proline-blocking exceptions (do not cleave `K` or `R` when followed immediately by `P`) are modeled exactly.

Research Question: `What tryptic peptides does a protein sequence produce, and which of those are MS-observable?`

## 2. Hypothesis Evaluation

Our hypothesis was:
> **Implementing the canonical trypsin rule—cleaving after Lysine (K) or Arginine (R), but not when followed immediately by Proline (P)—will perfectly reconstruct the expected peptide lists for hand-curated test sequences.**

### Findings
The experiment completely **supported** our hypothesis:
* **Exact-match validation rate:** 100% (5 out of 5 hand-curated test cases passed).
* **Proline-block exception violation rate:** 0% (explicit verification confirmed no peptides were cleaved immediately before a proline residue).

### Results Analysis

The test case details and output:
1. `AKPR` -> `["AKPR"]`: Successfully confirmed that proline blocks cleavage at the `K-P` junction.
2. `MKWVTFISLLR` -> `["MK", "WVTFISLLR"]`: Confirmed simple cleavage after `K` and proper terminal peptide emission.
3. `GPKPLR` -> `["GPKPLR"]`: Verified proline blocks cleavage in a longer sequence context.
4. `KPR` -> `["KPR"]`: Confirmed exception handling in short peptide lengths.
5. `RGPK` -> `["R", "GPK"]`: Confirmed correct cleavage near the N-terminus.

These results verify that our core logical loop correctly keeps track of sequence positions, respects the exception rule, and emits terminal fragments accurately.

## 3. Limits & Boundaries

* **No missed cleavages:** The current implementation assumes perfect cleavage efficiency. Real-world trypsin digests contain "missed cleavages" where trypsin fails to cut at valid cleavage sites, producing longer peptides.
* **No mass or length filters:** We have not yet modeled the physical limits of mass spectrometers (length 6-40, mass 500-5000 Da), so very short peptides (such as `"R"` and `"MK"`) are currently emitted.
* **Deterministic only:** Standard amino-acid residue masses and standard chemical groups (adding one water molecular mass) are not yet integrated into the calculator.

## 4. Future Directions

Based on this successful validation, we can now progress to the next rungs of the fidelity ladder:
1. **Missed Cleavages (Iteration 2):** Generalize the digestion algorithm to support `0`, `1`, or `2` missed cleavages, modeling realistic imperfect digestion. We predict that allowing missed cleavages will increase the overall count of unique peptide candidates and shift the peptide length distribution higher.
2. **Peptide Mass & MS Filters (Iteration 3):** Incorporate a monoisotopic amino acid residue mass table, calculate the monoisotopic mass of each peptide (residue sum + $H_2O$ mass), and filter peptides to the MS-observable window (mass 500-5000 Da, length 6-40 residues).

---
*Created on: 2026-06-29*
*Experiment Script:* [`smairt_template_demos/peptide_digest/peptide_digest/experiments/01_synthetic/script_01_tryptic_digestion_smoke_test.py`](smairt_template_demos/peptide_digest/peptide_digest/experiments/01_synthetic/script_01_tryptic_digestion_smoke_test.py)
*Log File:* `results/logs/script_01_tryptic_digestion_smoke_test_20260629_084613.log`
