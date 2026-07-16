# Hypothesis 02 — Separation of Membrane-Like and Soluble-Like Sequences using GRAVY

## Status: PENDING

## Background
Transmembrane proteins sit inside lipid bilayers, which are highly hydrophobic environments. Consequently, their transmembrane domains are enriched in highly hydrophobic residue types (such as I, L, V, F). On the other hand, cytosolic soluble proteins sit in aqueous cellular compartments, meaning they are enriched in polar/charged residues (such as E, D, K, R, N, Q) and generally depleted of massive hydrophobic segments. This fundamental biological difference should be strongly reflected in sequence-average hydropathy (GRAVY).

## Hypothesis Statement

**Prediction**:
1. Synthetic peptide sequences generated with amino acid frequencies biased toward hydrophobic residues ("membrane-like" pool) will have systematically and significantly higher GRAVY scores compared to synthetic sequences biased toward charged and polar residues ("soluble-like" pool).
2. A single-feature classifier or threshold model trained on the GRAVY score will separate these two pools with high classification accuracy (AUROC $\ge 0.90$), whereas negative controls (MW or pI alone) will achieve near-random accuracy ($\approx 50\%$).
3. Evaluating feature importance across a multi-feature classifier (containing MW, pI, and GRAVY) will show that GRAVY carries the overwhelming majority of predictive power.

**Rationale**:
By definition, Kyte-Doolittle GRAVY measures average sequence hydropathy, where positive values denote hydrophobic sequences and negative values denote hydrophilic ones. Since the membrane-like and soluble-like pools are explicitly constructed with differing proportions of hydrophobic residues, their average GRAVY distributions will be heavily shifted. MW and pI do not have systematic evolutionary pressures tied directly to membrane occupancy in this simplistic simulation, meaning they will serve as negative controls.

**Success criteria**:
- The mean GRAVY of the membrane-like pool is positive, while the mean GRAVY of the soluble-like pool is negative.
- The AUROC of a simple Logistic Regression or Decision Tree classifier using GRAVY alone as a feature is $\ge 0.90$ on a test split.
- The classification accuracy using pI or MW alone is close to random chance ($50\% \pm 10\%$).
- Multi-feature random forest or logistic regression model confirms GRAVY feature importance/coefficient is dramatically larger than MW or pI.
- A visualization (histogram) clearly shows two distinct, minimally overlapping distributions of GRAVY for the two pools.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_02_synthetic_classification.py`
- **Phase**: synthetic (Phase 1)
- **Track**: Track A (Initial baseline property calculation & downstream classification)
- **Data**:
  - Synthetic membrane-like pool: 500 sequences (length 100-150 residues) generated with a higher probability for hydrophobic amino acids: `I`, `L`, `V`, `F`, `A`, `M` (e.g., total 60% probability) and lower for charged/polar residues.
  - Synthetic soluble-like pool: 500 sequences (length 100-150 residues) generated with a higher probability for charged/polar amino acids: `K`, `R`, `H`, `D`, `E`, `N`, `Q` (e.g., total 60% probability) and lower for hydrophobic ones.
  - Total $1,000$ labeled samples ($50\%$ membrane-like as class 1, $50\%$ soluble-like as class 0).
- **Controls**:
  - Negative control feature 1: Molecular Weight (MW).
  - Negative control feature 2: Isoelectric Point (pI).
- **Key metrics**:
  - Mean properties (MW, pI, GRAVY) for both pools.
  - Classification accuracy, precision, recall, F1-score, and AUROC for:
    - GRAVY-only model
    - pI-only model
    - MW-only model
    - Combined multi-feature model
  - Permutation feature importance or model coefficient weights.

## Dependencies
- NumPy for sequence generation with custom probability distributions.
- Pandas for structural tabular organization.
- Scikit-learn for splitting, classifier training, evaluation, and feature importance.
- Matplotlib/Seaborn for histogram plotting.
- Property calculators implemented and validated in `script_01_validate_calculators.py`.

## Results

*(To be filled in after the classification experiment script runs — see analysis/ANALYSIS_02.md)*

## Notes
- Random seed must be strictly fixed (`1024` as per `prompts/CODE_CONVENTIONS.md` standards table) to ensure that the synthetic data pools are fully reproducible.
- Sequence lengths should be randomly chosen (e.g., uniform in $[100, 150]$) to confirm that the classifiers do not learn a trivial sequence-length bias.
