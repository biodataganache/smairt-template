# Hypothesis 01: Canonical Trypsin Digestion Verification

## 1. Background

In bottom-up shotgun proteomics, trypsin is used to cut proteins into peptides at specific sites. To identify proteins from MS data, we must model this cleavage process *in-silico*. Our study models the deterministic canonical trypsin cleavage rules as a primary foundation, before introducing biological noise or mass-spectrometry detection windows.

Research Question: `What tryptic peptides does a protein sequence produce, and which of those are MS-observable?`

## 2. Hypothesis

Implementing the canonical trypsin rule—cleaving after Lysine (K) or Arginine (R), but **not** when followed immediately by Proline (P)—will perfectly reconstruct the expected peptide lists for hand-curated test sequences. 

Specifically:
1. Any sequence lacking internal `K` or `R` (excluding those followed by `P`) will yield exactly 1 peptide containing the entire sequence.
2. The presence of `K` or `R` followed immediately by `P` will correctly suppress cleavage, producing a single combined peptide across that junction.
3. Clean cleavage boundaries at the protein N- and C-termini will be maintained without producing empty or off-by-one peptide sequences.

## 3. Experimental Design

We will implement a pure-Python tryptic digestion function in `experiments/01_synthetic/script_01_tryptic_digestion_smoke_test.py` and run a deterministic test suite containing the following test sequences:

| Test Sequence | Cleavage Points | Expected Peptides | Rationale |
|---|---|---|---|
| `AKPR` | No cuts (`K` is followed by `P`; C-terminal `R` is end) | `["AKPR"]` | Tests `K-P` blocking exception |
| `MKWVTFISLLR` | Cleave after `K` | `["MK", "WVTFISLLR"]` | Tests simple cleavage and N-/C-terminal emissions |
| `GPKPLR` | No cuts (`K` is followed by `P`; C-terminal `R` is end) | `["GPKPLR"]` | Tests `K-P` blocking exception with non-standard prefix |
| `KPR` | No cuts (`K` is followed by `P`) | `["KPR"]` | Tests extremely short sequence with block |
| `RGPK` | Cleave after `R` | `["R", "GPK"]` | Tests cleavage near N-terminus |

### Success Criteria (Metrics)
* **Exact-match validation rate:** 100% of test sequences must match their hand-written expected peptide lists exactly.
* **Proline block exception violation rate:** 0% of output peptides may terminate in `K` or `R` when the next character in the original sequence was `P`.

## 4. References & Context
* Background Document: [`smairt_template_demos/peptide_digest/background/01_initial_question.md`](smairt_template_demos/peptide_digest/background/01_initial_question.md)
* Code Conventions: [`smairt_template_demos/peptide_digest/peptide_digest/prompts/CODE_CONVENTIONS.md`](smairt_template_demos/peptide_digest/peptide_digest/prompts/CODE_CONVENTIONS.md)
