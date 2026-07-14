# Analysis 02: Missed Tryptic Cleavages Verification

## 1. Background

Standard tryptic digestion is rarely 100% efficient under experimental conditions. To construct realistic search libraries for bottom-up proteomics, *in-silico* digesters must allow trypsin to skip a specified maximum of valid cleavage sites ($N$), combining adjacent segments. In this iteration, we expanded our digester algorithm to support missed cleavages ($N = 0, 1, 2$) and verified its mathematical behavior and correctness against hand-curated test cases.

Research Question: `What tryptic peptides does a protein sequence produce, and which of those are MS-observable?`

## 2. Hypothesis Evaluation

Our hypothesis was:
> **Allowing a maximum of $N$ missed cleavages will systematically expand the pool of candidate peptides by combining up to $N+1$ adjacent, fully-cleaved peptides. This will increase the total peptide yield and the average peptide length in a predictable, mathematically bounded manner.**

### Findings
The results completely **supported** our hypothesis:
1. **$N = 0$ equivalence:** Setting `max_missed_cleavages = 0` yielded identical peptide sequences to our canonical Iteration 1 outputs across all test cases.
2. **Deterministic hand-curated validation:** The updated digester achieved a **100% exact-match validation rate** (8 out of 8 validation conditions passed).
3. **Yield bounding:** For a sequence with $M$ fully-cleaved segments, the number of generated peptides exactly matched our prediction. For example:
   * Sequence `AKRGPK` ($M=3$ segments: `["AK", "R", "GPK"]`)
     * $N=0$ generated exactly $3$ peptides: $M-1+1 = 3$.
     * $N=1$ generated exactly $5$ peptides: $(M-1+1) + (M-2+1) = 3 + 2 = 5$.
     * $N=2$ generated exactly $6$ peptides: $3 + 2 + 1 = 6$.
4. **Monotonic trend validation:** On a longer mock template protein sequence (`MKWVTFISLLRLVAKRGPKPLRLVAKR`, $M = 7$ segments):
   * $N = 0$ produced **7** peptides with an average length of **3.86** residues.
   * $N = 1$ produced **13** peptides with an average length of **6.00** residues.
   * $N = 2$ produced **18** peptides with an average length of **7.78** residues.
   
   This explicitly confirms that both unique peptide counts and average peptide lengths increase monotonically as we allow greater missed-cleavage rates.

## 3. Limits & Boundaries

* **No mass or length filters:** While we successfully simulated missed cleavages, we are still emitting very short peptides (e.g. `"R"`) and very long peptides (e.g. the 18-residue `MKWVTFISLLRLVAK`), which might lie outside of a mass spectrometer's actual observation capabilities.
* **No chemical mass calculation:** The segments are still treated strictly as string variables without physical mass validation.

## 4. Future Directions

With the cleavage rules and missed-cleavage mechanics completely validated, we are ready to proceed to the third rung of our fidelity ladder:
1. **Peptide Monoisotopic Masses:** Introduce a standard monoisotopic amino acid residue mass table and compute peptide monoisotopic masses (residue sum + $18.0106$ Da $H_2O$ terminal groups mass).
2. **MS-Observable Window Filters:** Implement length filters (6–40 residues) and mass filters (500–5000 Da) to report the exact observable fraction on realistic target proteins.

---
*Created on: 2026-06-29*
*Experiment Script:* [`smairt_template_demos/peptide_digest/peptide_digest/experiments/01_synthetic/script_02_missed_cleavages_validation.py`](smairt_template_demos/peptide_digest/peptide_digest/experiments/01_synthetic/script_02_missed_cleavages_validation.py)
*Log File:* `results/logs/script_02_missed_cleavages_validation_20260629_085242.log`
