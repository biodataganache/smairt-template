# Analysis 01 — Benjamini-Hochberg Correction Baseline

## Executive Summary

We evaluated the performance of a standard differential protein abundance workflow (per-protein Welch's t-test + Benjamini-Hochberg multiple-testing correction) on a synthetic matrix of 2,000 proteins across 10 samples (5 controls vs. 5 treated). While the BH procedure successfully controlled the empirical FDR at 2.70% (well below the 5.0% target), it achieved a much lower recall (36.00%) than the predicted 70% threshold. This represents a partial support of Hypothesis 1 and highlights a crucial trade-off: multiple-testing correction controls false positives at the cost of statistical power (sensitivity) under standard measurement noise.

## Experiment Details

- **Script**: `experiments/01_synthetic/script_01_bh_correction.py`
- **Hypothesis**: `hypotheses/H1_bh_correction_baseline.md`
- **Log**: `results/logs/script_01_bh_correction_20260630_110058.log`
- **Track**: None (Baseline Phase)
- **Phase**: synthetic

## Key Results

The standard Welch's t-test comparing the 5 controls and 5 treated samples was applied to each of the 2,000 proteins. Out of these, 100 proteins were planted with true-DE effects (50 up-regulated with +1.0 log2 FC, and 50 down-regulated with -1.0 log2 FC). The noise level was set to standard deviation $\sigma = 0.3$. 

| Metric | Expected (Hypothesis) | Observed (Uncorrected) | Observed (BH-Corrected) | Status (BH vs. Hyp) |
|--------|----------------------|-----------------------|-------------------------|---------------------|
| Called Significant | - | 186 | 37 | - |
| True Positives (TP) | - | 98 | 36 | - |
| False Positives (FP) | - | 88 | 1 | - |
| False Negatives (FN) | - | 2 | 64 | - |
| Recall (Sensitivity) | $\ge 70.0\%$ | 98.00% | 36.00% | ✗ (Lower than expected) |
| Empirical FDR | $\le 5.0\%$ | 47.31% | 2.70% | ✓ (FDR controlled) |

### Key Observations:
1. **The Multiple-Testing Problem is Real**: Without correction, a raw p-value threshold of $p < 0.05$ yields 88 false positives out of 1,900 null proteins (empirical $\text{FDR} = 47.31\%$), which is nearly equal to the number of true positives (98) detected.
2. **BH Controls FDR Successfully**: Applying Benjamini-Hochberg correction at a target FDR of $0.05$ reduces the number of false positives from 88 to exactly 1. The resulting empirical FDR is 2.70%, which is safely below the nominal 5.0% threshold.
3. **Severe Power/Recall Drop**: Controlling the false discovery rate drastically reduces statistical power. Only 36 out of 100 planted proteins were recovered under BH correction (recall of 36%), compared to 98 recovered using the uncorrected threshold.

## Hypothesis Assessment

### PARTIALLY SUPPORTED

- **FDR Control**: **SUPPORTED**. The BH procedure successfully controlled the empirical false discovery rate at 2.70%, which is well below the target 5.0% threshold. The uncorrected FDR of 47.31% confirmed the predicted catastrophic failure of raw p-values under multiple-testing pressures.
- **Recall Target**: **REFUTED**. We predicted a recall of $\ge 70\%$ for the BH-corrected results. However, we observed only 36.00% recall. Under the standard measurement noise ($\sigma = 0.3$ on log2 scale) and 5 replicates, an effect size of $\pm 1.0$ is not sufficiently distinguished from background noise to pass the stringent BH-adjusted p-value threshold for a large portion of the planted set.

### Where It Works (Boundaries)
- **FDR Control**: Succeeds perfectly on synthetic Gaussian data. The empirical FDR is safely within the target threshold ($\le 5.0\%$).
- **True DE Detection**: Highly sensitive when no multiple-testing correction is applied (98.0% recall), but this comes at the cost of unacceptable false positive rates (FDR = 47.31%).

### Where It Breaks Down
- **Statistical Power**: Under a standard design with 5 replicates per group, noise standard deviation of 0.3, and effect size of 1.0 (a 2-fold change), the BH correction is too conservative, resulting in a 64% False Negative Rate (64 missed true-positives).

## Comparison to Prior Work

This is the baseline experiment (Iteration 1), so no prior work exists for comparison.

## Implications

For quantitative proteomics experiments, relying solely on BH-corrected p-values at a strict FDR of $0.05$ with $N=5$ replicates per group will result in a highly clean but extremely incomplete list of differentially abundant proteins. Most of the truly changed proteins (in this case, 64%) will be missed. 

To improve recall, researchers must either:
1. Increase sample size (number of replicates $N$).
2. Have larger effect sizes (stronger biological response).
3. Reduce measurement noise (improved sample prep or instrumentation).
4. Relax the FDR threshold if an exploratory list is desired, or use combined filters (e.g., Volcano fold-change filters + raw p-values) though FDR control is then lost.

## Next Steps

1. **Investigate the effect of sample size (replicates $N$) and noise level ($\sigma$) on Recall and FDR**: Run a parameter sweep in Iteration 2 to map out the exact boundaries where a recall of $\ge 70\%$ can be achieved under BH control.
2. **Transition to Data Tier 2 (Synthetic, Harder)**: Introduce log-normal noise, heteroscedasticity, and missing values to see how they impact the FDR control and recall.
3. **Explore other multiple-testing corrections**: Compare BH with other methods such as Storey's q-value or Bonferroni.

## Files Generated

- `results/logs/script_01_bh_correction_20260630_110058.log` — Raw output
- `results/figures/script_01_bh_correction_volcano.png` — Volcano plot
- `results/script_01_bh_correction_results.csv` — Full differential abundance results matrix with metadata
- `data/synthetic/synthetic_abundance.csv` — Synthetic abundance matrix
- `data/synthetic/synthetic_metadata.csv` — Synthetic ground-truth metadata

## Intellectual Contribution Notes

The initial simulation parameters ($N = 2,000$ proteins, $5+5$ replicates, $100$ planted proteins, $\text{SD} = 0.3$, $\text{FC} = \pm 1.0$) and workflow proposal were provided by the user.
