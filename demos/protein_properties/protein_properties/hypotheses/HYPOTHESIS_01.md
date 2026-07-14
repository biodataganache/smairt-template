# Hypothesis 01 — Sequence-Property Calculator Accuracy and Validation

## Status: PENDING

## Background
The fundamental assumption of sequence-based protein analysis is that physical/chemical properties can be computed from raw amino acid letters using residue-level constants. If these simple mathematical models match standard database/tool properties, they form a robust baseline of features for downstream machine learning tasks (e.g., predicting cellular location or membrane-spanning status).

## Hypothesis Statement

**Prediction**: 
A pure-Python implementation of residue-level calculators for Molecular Weight (MW), Isoelectric Point (pI), and Grand Average of Hydropathy (GRAVY) will produce values that match standard reference values (specifically, ExPASy ProtParam / EMBOSS results) within tight numeric tolerances:
- **Molecular Weight**: $\le 0.1\%$ relative difference from reference when including terminal water ($H_2O$, approx. $18.015\text{ Da}$ for average isotopic masses).
- **Isoelectric Point (pI)**: $\le 0.05\text{ pH units}$ from reference when using standard EMBOSS pKa values for ionizable groups (N-terminus, C-terminus, D, E, C, Y, H, K, R) solved via a net-charge equation with bisection search.
- **GRAVY**: Perfect match (relative difference $= 0$) against the standard Kyte-Doolittle scale average.

**Rationale**: 
Residue masses and hydrophobicity scales are additive and invariant. Isoelectric point estimation is deterministic and can be computed via root-finding methods (e.g., bisection search on the pH range $[0, 14]$) to find the point where net charge equals zero. Correct handling of terminal water and terminus-specific charges will guarantee reference parity.

**Success criteria**:
- Relative error of computed MW for Human Ubiquitin is $< 0.1\%$ compared to the target reference of $\approx 8564.8\text{ Da}$ (calculated average MW is $8564.835\text{ Da}$).
- Calculated pI for Human Ubiquitin matches the target reference of $\approx 7.54$ within $\pm 0.05\text{ pH units}$ under the standard uncorrected EMBOSS pKa scale (note: ExPASy's reference of $6.56$ uses the Bjellqvist scale with terminal/residue-neighbor corrections).
- Calculated GRAVY for Human Ubiquitin matches the exact Kyte-Doolittle average of $-0.489$.
- Correct exact calculations verified on hand-checkable short sequences (e.g., `AAA`, `MVR`).

## Experimental Design

- **Script**: `experiments/01_synthetic/script_01_validate_calculators.py`
- **Phase**: synthetic (Phase 1)
- **Track**: Track A (Initial baseline property calculation)
- **Data**: 
  - Tiny test peptides (`AAA`, `MVR`) for formula correctness.
  - Human Ubiquitin sequence (`MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG`) as reference protein.
- **Controls**: Hand-computed MW and GRAVY scores; published/ExPASy validation values.
- **Key metrics**: 
  - Absolute/relative difference in MW (Da).
  - Absolute difference in pI (pH units).
  - Absolute difference in GRAVY.

## Dependencies

- EMBOSS pKa set:
  - N-term: 8.6
  - C-term: 3.6
  - Lys (K): 10.8
  - Arg (R): 12.5
  - His (H): 6.5
  - Asp (D): 3.9
  - Glu (E): 4.1
  - Cys (C): 8.5
  - Tyr (Y): 10.1
- Average isotopic masses of amino acid residues (with $H_2O$ subtracted for peptide bond):
  - A: 71.08, R: 156.19, N: 114.10, D: 115.09, C: 103.14, Q: 128.13, E: 129.12, G: 57.05, H: 137.14, I: 113.16, L: 113.16, K: 128.17, M: 131.20, F: 147.18, P: 97.12, S: 87.08, T: 101.10, W: 186.21, Y: 163.18, V: 99.13, Water ($H_2O$): 18.015

## Results

*(Filled in after experiment runs — see analysis/ANALYSIS_01.md for full interpretation)*

## Notes
- Human Ubiquitin reference values:
  - Sequence: `MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG`
  - Expected MW: ~8564.8 Da
  - Expected pI: ~7.54 (under EMBOSS pKa values; 6.56 is the ExPASy/Bjellqvist corrected value)
  - Expected GRAVY: -0.489 (exact Kyte-Doolittle average)
