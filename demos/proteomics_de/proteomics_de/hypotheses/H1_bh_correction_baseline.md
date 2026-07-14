# Hypothesis 1 — Benjamini-Hochberg Correction Baseline

## Status: PENDING

## Background

In high-throughput proteomics, we measure thousands of proteins simultaneously. When analyzing differential abundance, testing each protein independently results in a massive multiple-testing problem. Under a standard raw p-value threshold (e.g., $p < 0.05$), we expect false positives to scale with the number of null hypotheses tested. 

This experiment establishes a baseline under a simplified, clean synthetic data environment (no missing values, constant Gaussian noise) to verify that a standard differential abundance workflow (Welch's t-test + BH correction) behaves exactly as theoretically predicted.

## Hypothesis Statement

**Prediction**: 
A per-protein two-sample Welch's t-test on $\log_2$-transformed abundance values, followed by Benjamini-Hochberg (BH) false-discovery-rate correction at an FDR threshold of $0.05$, will:
1. Recover a high proportion (recall $\ge 70.0\%$) of the $100$ planted true-positive DE proteins (effect size of $\pm 1.0 \log_2$ fold change, noise $\text{SD} = 0.3$).
2. Keep the observed false-discovery rate (empirical FDR) strictly controlled at or below the nominal target threshold of $0.05$.
3. In contrast, using a raw uncorrected p-value threshold of $p < 0.05$ will result in a high observed false-discovery rate (empirical $\text{FDR} \gg 0.05$), demonstrating the multiple-testing problem.

**Rationale**: 
Welch's t-test is well-suited for two-sample comparisons of normally distributed $\log_2$ values. The Benjamini-Hochberg procedure controls the expected proportion of false discoveries when test statistics are independent or positively dependent. In our synthetic setup, the simulated noise is independent and Gaussian, satisfying the test assumptions perfectly.

**Success criteria**:
- Empirical FDR for BH-corrected results is $\le 0.05$ (or within statistical error across runs).
- Recall for BH-corrected results is $\ge 70.0\%$.
- Uncorrected empirical FDR is $> 40.0\%$, proving the necessity of multiple-testing correction.

## Experimental Design

- **Script**: `experiments/01_synthetic/script_01_bh_correction.py`
- **Phase**: synthetic
- **Track**: None (Baseline Phase)
- **Data**: Synthetic matrix of $2,000$ proteins $\times$ $10$ samples ($5$ control, $5$ treated).
- **Controls**: Uncorrected two-sample t-test results.
- **Key metrics**:
  - Number of true positives called (TP)
  - Number of false positives called (FP)
  - Empirical FDR: $\frac{FP}{TP + FP}$
  - Recall: $\frac{TP}{\text{Total Planted True DE}}$
  - Volcano Plot visualization

## Dependencies

- No external data files (pure synthetic).
- Shared library functions for logging: `scripts.shared.TeeLogger`, `scripts.setup_logging`.
- Python libraries: `numpy`, `pandas`, `scipy`, `statsmodels`, `matplotlib`.

## Results

*(To be filled in after script_01_bh_correction.py runs)*

## Notes

This forms the first tier of the data progression ladder. Future tiers will introduce log-normal noise, heteroscedasticity, and missing values.
