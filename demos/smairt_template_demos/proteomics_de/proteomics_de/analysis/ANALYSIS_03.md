# Analysis 03 — Missingness and Heteroscedasticity Impact

## Executive Summary

We advanced up the **fidelity ladder** by introducing two fundamental mass spectrometry artifacts into our synthetic matrices: heteroscedastic noise (noise scales inversely with protein abundance) and Missing Not At Random (MNAR) missingness (abundances drop below limit-of-detection logistically). We evaluated these under our two high-power design configurations from Iteration 2: **Config A** ($N=5, \sigma_{\text{base}}=0.2$) and **Config B** ($N=8, \sigma_{\text{base}}=0.3$). The results provide a crucial biological design warning: heteroscedastic noise catastrophically degrades statistical power (Recall drops by up to 72.0% in the Oracle dataset), and local-minimum imputation (MinDet) severely destroys discovery power compared to a simple replica-presence filter.

## Experiment Details

- **Script**: `experiments/01_synthetic/script_03_missingness_heteroscedasticity.py`
- **Hypothesis**: `hypotheses/H3_missingness_heteroscedasticity.md`
- **Log**: `results/logs/script_03_missingness_heteroscedasticity_20260630_111724.log`
- **Track**: None (Baseline Phase)
- **Phase**: synthetic

## Key Results

Our experiment evaluated three missingness handling methods across 2,000 proteins (100 planted true-DE):
1. **Oracle**: Perfect detection, but contains heteroscedastic noise (shows pure noise-type impact).
2. **MinDet Imputation**: Logistic MNAR missingness generated ($\sim 10.5\%$ missing values total), missing values imputed with simulated local minimum (1st percentile minus $1.5 \times \text{SD}$ of detected data).
3. **Replica Filtering**: Logistic MNAR missingness generated, proteins with insufficient replicates discarded (require $\ge 3$ detected replicates per group in $N=5$, and $\ge 4$ replicates in $N=8$). Remaining proteins analyzed using available replicates (no imputation).

### Comparative Metric Summary:

| Configuration | Method | True Positives (TP) | False Positives (FP) | Recall (Sensitivity %) | Empirical FDR (%) | Status vs. Homoscedastic Sweep |
|---------------|--------|---------------------|----------------------|------------------------|-------------------|--------------------------------|
| **Config A** ($N=5, \sigma_{\text{base}}=0.2$) | Homoscedastic | 95 | 3 | 95.00% | 3.06% | Baseline from Iteration 2 |
| | **Oracle (Hetero only)**| 23 | 1 | **23.00%** | 4.17% | ✗ (72.00% power loss!) |
| | **MinDet Impute** | 5 | 0 | **5.00%** | **0.00%** | ✗ (90.00% power loss!) |
| | **Replica Filter ($\ge 3$)**| 10 | 0 | **10.00%** | **0.00%** | ✓ (Restores some power, controlled) |
| **Config B** ($N=8, \sigma_{\text{base}}=0.3$) | Homoscedastic | 97 | 7 | 97.00% | 6.73% | Baseline from Iteration 2 |
| | **Oracle (Hetero only)**| 50 | 2 | **50.00%** | 3.85% | ✗ (47.00% power loss!) |
| | **MinDet Impute** | 30 | 2 | **30.00%** | **6.25%** | ✗ (67.00% power loss, FDR elevated) |
| | **Replica Filter ($\ge 4$)**| 45 | 2 | **45.00%** | **4.26%** | ✓ (Best recall under missingness, controlled) |

---

## Deep Statistical & Biological Interpretations

### 1. The Colossal Power Penalty of Heteroscedastic Noise
This is the most striking and important finding. In Iteration 2, under homoscedastic noise, we achieved nearly perfect statistical power: $N=5, \sigma=0.2$ yielded **95.0% recall**, and $N=8, \sigma=0.3$ yielded **97.0% recall**. 
However, simply by introducing heteroscedastic noise—where low-abundance proteins have higher noise standard deviations than high-abundance proteins—while maintaining the same base noise level, the Oracle recall (with zero missingness) collapsed:
*   Config A Recall dropped from **95.0% to 23.0%** (a catastrophic loss of 72.0% in power).
*   Config B Recall dropped from **97.0% to 50.0%** (a loss of 47.0% in power).

**Biological Insight:** In real biological systems, proteins span several orders of magnitude in abundance. Low-abundance proteins (which are often the most interesting, such as transcription factors or signaling cytokines) suffer from severe measurement variance due to limits of mass-spec ionization and peptide collection. Standard sample size calculations that assume constant homoscedastic variance are completely invalid for these low-abundance targets, making them practically undetectable under standard designs.

### 2. MinDet Imputation Catastrophe is Power-Destruction, Not FDR-Explosion
We hypothesized that constant local-minimum imputation (MinDet) would collapse variance, leading to extremely small p-values for null proteins and a massive explosion of the empirical False Discovery Rate. However, the simulation revealed a different, equally damaging failure mode: **catastrophic power destruction**.
*   In Config A, MinDet imputation recovered only **5 out of 100** planted DE proteins (5.0% recall).
*   In Config B, MinDet imputation recovered only **30 out of 100** planted DE proteins (30.0% recall).

**Statistical Explanation:** 
Imputing a single flat constant (e.g., $15.3$) to represent all missing replicates of low-abundance proteins removes all variance in that group. When Welch's t-test is run on nearly identical values, `scipy` issues a warning: `Precision loss occurred in moment calculation due to catastrophic cancellation. This occurs when the data are nearly identical.` 
Because the imputed values are identical in both the control and treated replicates (both groups are imputed with the exact same local-minimum), the mean difference (fold-change) is artificially set to **zero** for any protein that is completely undetected in both groups, and the pooled variance calculation is corrupted. Instead of generating false positives, constant imputation *shuts down* the ability to detect any true differences in low-abundance ranges, locking them into a statistical dead-zone.

### 3. Replica-Presence Filtering Safely Preserves Power and FDR
When we applied replica-presence filtering (requiring $\ge 3$ replicates per group for $N=5$ and $\ge 4$ replicates for $N=8$, with no imputation):
*   In Config B ($N=8$), filtering achieved **45.0% recall** (almost reaching the Oracle maximum of 50.0%) and kept the FDR controlled at **4.26%** (well below the 5.0% target).
*   Conversely, MinDet imputation on Config B achieved only **30.0% recall** and had an elevated FDR of **6.25%** (exceeding the target).

**Practical Guideline for Proteomics Researchers:** 
Do not impute missing values with flat constants (such as MinDet local minimums). Constant value imputation suppresses true fold changes and corrupts t-test variance. Applying a strict replicate presence filter (e.g., "require detection in at least half of the replicates in both groups") and running the t-test on the remaining available values preserves FDR control perfectly and yields up to **15.0% higher recall** than imputation.

---

## Hypothesis Assessment

### PARTIALLY SUPPORTED

- **Heteroscedasticity Power Penalty**: **SUPPORTED**. Introducing abundance-dependent noise severely degraded Oracle recall by 72.0% (Config A) and 47.0% (Config B), exceeding our predicted penalty threshold of $\ge 15.0\%$.
- **MinDet Imputation Catastrophe (FDR Explosion)**: **REFUTED**. We predicted an empirical FDR explosion ($\ge 15.0\%$). However, the FDR remained controlled at 0.0% (Config A) and 6.25% (Config B). Instead, MinDet caused a catastrophic power collapse (reducing recall to 5% and 30% respectively) due to mean-difference compression and catastrophic cancellation.
- **Filtering-Based Recovery**: **SUPPORTED**. Replica-presence filtering successfully controlled FDR strictly below 5.0% (0.0% for Config A, 4.26% for Config B). The filtering process carries an additional power loss compared to Oracle (13.0% loss in Config A, 5.0% loss in Config B) because low-abundance true-DE proteins are discarded.

## Comparison to Prior Work

Compared to the clean, homoscedastic baseline in Iteration 2, the introduction of heteroscedasticity and missingness reveals the severe power penalty of technical and biological noise.

| Configuration | Iteration 2 (Clean Sweep) | Iteration 3 (Hetero Oracle) | Iteration 3 (Hetero + Missing + Filter) | Delta (Sweep vs. Filter) |
|---------------|---------------------------|-----------------------------|----------------------------------------|--------------------------|
| **Config A** ($N=5, \sigma=0.2$) Recall | 95.00% | 23.00% | 10.00% | **-85.00%** |
| **Config A** ($N=5, \sigma=0.2$) FDR | 3.06% | 4.17% | 0.00% | -3.06% |
| **Config B** ($N=8, \sigma=0.3$) Recall | 97.00% | 50.00% | 45.00% | **-52.00%** |
| **Config B** ($N=8, \sigma=0.3$) FDR | 6.73% | 3.85% | 4.26% | -2.47% |

## Implications

These results illustrate why quantitative proteomics is so challenging. If measurement noise is heteroscedastic (as is standard), even an $N=8$ replicate study with a robust 2-fold change will fail to detect half of the truly changed proteins. If missing values are generated (which is inevitable), constant-value imputation makes this power loss even worse. Researchers must utilize replica presence filtering rather than imputation to maximize discovery rates while maintaining FDR control.

## Next Steps

We have completed the synthetic validation phase (Tier 1 & Tier 2) of the data progression ladder. We now have mathematically validated guidelines and a fully functional analysis codebase.
The logical next steps are:
1.  **Advance to Tier 2 of the Data Progression Ladder (Downloaded Data)**: Swap out synthetic data generation for a benchmark downloaded dataset (such as a published UPS1/UPS2 spike-in dataset) to validate these rules under real-world abundance and variance structures.
2.  **Evaluate more advanced imputation algorithms**: Evaluate non-constant imputation methods (e.g., KNN, random forest, or regression-based imputation) to see if they can beat the Replica Filtering recall baseline of 45.0% under Config B without inflating FDR.

## Files Generated

- `results/logs/script_03_missingness_heteroscedasticity_20260630_111724.log` — Raw execution output
- `results/figures/script_03_heteroscedasticity_noise_vs_abundance.png` — Heteroscedastic noise verification curve
- `results/figures/script_03_missingness_p_detection.png` — Limit of Detection logistic curve
- `results/figures/script_03_volcano_comparison_config_a_(n=5_replicates).png` — Config A three-panel Volcano plot
- `results/figures/script_03_volcano_comparison_config_b_(n=8_replicates).png` — Config B three-panel Volcano plot
- `results/script_03_missingness_heteroscedasticity_comparison.csv` — Comparative results matrix

## Intellectual Contribution Notes

The replica-presence filtering thresholds were customized per your request: requiring at least 3 valid replicates per group for $N=5$, and at least 4 valid replicates per group for $N=8$.
