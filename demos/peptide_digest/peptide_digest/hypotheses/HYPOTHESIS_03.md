# Hypothesis 03: Peptide Mass Calculation and MS-Observable Filtration

## 1. Background

Mass spectrometers do not detect all generated peptides from a protein digest. Due to physical limitations in charge states, ionization, and standard instrument scanning settings, only peptides within a specific length and mass range can be resolved and identified. To bridge *in-silico* modeling with actual mass spectrometry, this iteration implements a monoisotopic mass calculator and filters peptides based on physical instrument limits.

Research Question: `What tryptic peptides does a protein sequence produce, and which of those are MS-observable?`

## 2. Hypothesis

Calculating peptide monoisotopic masses and filtering against physical mass spectrometry constraints (mass 500–5000 Da, length 6–40 residues) will filter out very short and very long peptides. The observable fraction of peptides will be maximized at standard experimental missed cleavage levels ($N=1, 2$) on real target proteins like Bovine Serum Albumin (BSA).

Specifically:
1. Short peptides (length $< 6$ residues, such as `"MK"` or `"R"`) will have calculated masses well below the 500 Da lower threshold and will be excluded.
2. Long peptides generated due to high missed-cleavage rates will be excluded if they exceed 40 residues or 5000 Da.
3. At $N=0$ missed cleavages, the physical constraint filters will drop a large percentage of total peptides due to short segments.
4. Allowing $N=1, 2$ missed cleavages will maximize the absolute yield of observable peptides because combining segments "rescues" short tryptic peptides into the visible mass window.

## 3. Experimental Design

We will implement a standard monoisotopic amino acid mass calculator and constraint filters inside `experiments/01_synthetic/script_03_peptide_filtration.py`. We will validate this code using standard monoisotopic masses and a real protein sequence.

### Monoisotopic Mass Vocabulary
* Residues: `A`: 71.03711, `C`: 103.00919, `D`: 115.02694, `E`: 129.04259, `F`: 147.06841, `G`: 57.02146, `H`: 137.05891, `I`: 113.08406, `K`: 128.09496, `L`: 113.08406, `M`: 131.04049, `N`: 114.04293, `P`: 97.05276, `Q`: 128.05858, `R`: 156.10111, `S`: 87.03203, `T`: 101.04768, `V`: 99.06841, `W`: 186.07931, `Y`: 163.06333
* Water terminal group: `18.0106` Da.

### Hand-Curated Verification Cases

#### Case A: `MK` (131.04049 + 128.09496 + 18.0106 Da = 277.14605 Da)
* **Expected monoisotopic mass:** $277.146$ Da ($\pm 0.001$ Da tolerance).
* **Expected filtration:** Excluded (fails length $< 6$ and mass $< 500$ Da criteria).

#### Case B: `WVTFISLLR` (186.07931 + 99.06841 + 101.04768 + 147.06841 + 113.08406 + 87.03203 + 113.08406 + 113.08406 + 156.10111 + 18.0106 Da = 1133.6597 Da - note water mass is 18.0106 Da and summation math: 186.07931 + 99.06841 + 101.04768 + 147.06841 + 113.08406 + 87.03203 + 113.08406 + 113.08406 + 156.10111 + 18.01056 Da = 1133.65969 Da!)
* **Expected monoisotopic mass:** $1133.660$ Da ($\pm 0.001$ Da tolerance).
* **Expected filtration:** Included/Observable (passes 6–40 residues, 500–5000 Da window).

### Test Target: Bovine Serum Albumin (BSA)
We will digest the canonical mature Bovine Serum Albumin sequence (minus its signal peptide, containing 583 residues) and report:
* Peptide count and length distributions across $N = 0, 1, 2$ missed cleavages.
* The absolute count and fraction of observable peptides under each condition.

### Success Criteria (Metrics)
* **Mass Accuracy:** Calculated masses match manual verification to within $\pm 0.001$ Da.
* **Filter Correctness:** No peptide of length $<6$ or $>40$, or mass $<500$ Da or $>5000$ Da, makes it past the filter.
* **Observable Maxima:** Verify if $N=1$ or $N=2$ yields more absolute observable peptides than $N=0$.

## 4. References & Context
* Background Document: [`smairt_template_demos/peptide_digest/background/01_initial_question.md`](smairt_template_demos/peptide_digest/background/01_initial_question.md)
* Second Iteration Analysis: [`smairt_template_demos/peptide_digest/peptide_digest/analysis/ANALYSIS_02.md`](smairt_template_demos/peptide_digest/peptide_digest/analysis/ANALYSIS_02.md)
