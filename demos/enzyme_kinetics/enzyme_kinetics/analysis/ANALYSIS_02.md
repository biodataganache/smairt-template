# ANALYSIS_02.md

## Script

`experiments/01_synthetic/script_02_noise_lineweaver_comparison.py`

## Hypothesis

`hypotheses/HYPOTHESIS_02.md`

As synthetic measurement noise increases, direct nonlinear least-squares fitting of the original velocity-versus-substrate data should recover planted Vmax and Km more accurately than Lineweaver-Burk fitting. Lineweaver-Burk was expected to break the 10% relative-error credibility threshold earlier than nonlinear fitting because reciprocal linearization overweights low-substrate noisy points.

## Methods summary

- Planted Vmax: 100.0 rate units
- Planted Km: 5.0 concentration units
- Substrate range: 0.5 to 50.0 concentration units
- Number of substrate points: 12
- Noise levels: 0%, 3%, 10%, 20%, and 40% of clean velocity
- Replicates per noise level: 50
- Base random seed: 2048
- Nonlinear initial guess: [90.0, 4.0] for [Vmax, Km]
- Methods compared:
  - Direct nonlinear least-squares fit on v versus [S]
  - Lineweaver-Burk linear regression on 1/v versus 1/[S]
- Primary metric: recovery error against planted Km and Vmax, not R^2 alone
- Credibility criterion: median Vmax and Km relative errors both <= 10%

## Output artifacts

- Log file: `results/logs/script_02_noise_lineweaver_comparison_20260713_135801.log`
- Detailed CSV: `results/script_02_noise_lineweaver_comparison_detailed_results.csv`
- Summary CSV: `results/script_02_noise_lineweaver_comparison_summary.csv`
- Median error figure: `results/figures/script_02_noise_lineweaver_comparison_median_errors.png`
- Representative fit figure: `results/figures/script_02_noise_lineweaver_comparison_representative_fit.png`
- Script with pasted-output block: `experiments/01_synthetic/script_02_noise_lineweaver_comparison.py`

## Key results

| Noise | Method | Valid / total | Invalid % | Median Vmax error | Median Km error | Median R^2 | Credible |
|-------|--------|---------------|-----------|-------------------|-----------------|------------|----------|
| 0% | Nonlinear | 50 / 50 | 0.00% | 0.000% | 0.000% | 1.00000 | True |
| 0% | Lineweaver-Burk | 50 / 50 | 0.00% | 0.000% | 0.000% | 1.00000 | True |
| 3% | Nonlinear | 50 / 50 | 0.00% | 1.093% | 3.732% | 0.99776 | True |
| 3% | Lineweaver-Burk | 50 / 50 | 0.00% | 2.328% | 3.113% | 0.99662 | True |
| 10% | Nonlinear | 50 / 50 | 0.00% | 5.000% | 12.666% | 0.97462 | False |
| 10% | Lineweaver-Burk | 50 / 50 | 0.00% | 7.880% | 8.856% | 0.95395 | True |
| 20% | Nonlinear | 50 / 50 | 0.00% | 11.064% | 25.296% | 0.89899 | False |
| 20% | Lineweaver-Burk | 50 / 50 | 0.00% | 16.635% | 23.219% | 0.80635 | False |
| 40% | Nonlinear | 50 / 50 | 0.00% | 21.212% | 33.566% | 0.68147 | False |
| 40% | Lineweaver-Burk | 40 / 50 | 20.00% | 36.584% | 47.898% | 0.37478 | False |

## Interpretation

The experiment confirms that both methods recover the planted parameters exactly on noiseless synthetic data and remain credible at 3% relative noise. This reproduces the expected textbook behavior under clean or near-clean conditions.

The predeclared hypothesis that Lineweaver-Burk would break earlier than nonlinear fitting was not supported under this specific relative-noise design and 10% median-error criterion. At 10% noise, the nonlinear method failed the credibility threshold because median Km error reached 12.666%, while Lineweaver-Burk remained just within threshold with median Km error of 8.856% and median Vmax error of 7.880%. This is an important result: the expected Lineweaver-Burk bias does not automatically dominate under every noise model and every breakdown criterion.

At 20% noise, both methods failed the 10% threshold. The representative 20% replicate showed severe disagreement: nonlinear fit estimated Vmax = 82.538767 and Km = 2.693782, while Lineweaver-Burk estimated Vmax = 133.258717 and Km = 8.082860. Both were far from the planted truth, but Lineweaver-Burk overshot Vmax and Km more strongly in that representative replicate.

At 40% noise, Lineweaver-Burk was clearly worse than nonlinear fitting. It produced invalid/nonphysical fits in 20% of replicates, and among valid replicates its median Vmax and Km errors were 36.584% and 47.898%, respectively. Nonlinear fitting also failed at this noise level, but with lower median errors and no invalid fits.

## Where did Lineweaver-Burk break down?

Under the predeclared definition, there was no tested noise level where Lineweaver-Burk failed while nonlinear fitting remained credible. Therefore, the formal breakdown level is: none among tested levels.

Under a broader practical interpretation, Lineweaver-Burk showed clear breakdown at 40% noise because:

1. 20% of Lineweaver-Burk replicates produced invalid/nonphysical parameters.
2. Median Lineweaver-Burk Vmax error reached 36.584%.
3. Median Lineweaver-Burk Km error reached 47.898%.
4. Median R^2 on the original velocity scale fell to 0.37478.

The result suggests that Lineweaver-Burk bias and instability become visible at high noise in this simulation, but the exact breakdown point depends on noise model, sampling design, and threshold definition.

## Limitations observed

- The noise model used relative Gaussian noise proportional to clean velocity. The classic Lineweaver-Burk failure mode may be more obvious under additive constant-variance velocity noise, because low-velocity points then receive disproportionately large reciprocal-scale distortions.
- The tested substrate design used 12 geometrically spaced points from 0.5 to 50. Different sampling density near low [S] could change the comparison.
- The 10% threshold is intentionally strict; small changes in threshold would alter which method is labeled credible at 10% noise.
- Median errors hide the full distribution. The detailed CSV should be used for quantiles, outliers, and replicate-level failure analysis.
- This iteration did not yet test inhibition models.

## Next steps

1. In a follow-up noise comparison, test additive constant-variance noise in velocity units, because that may better demonstrate the reciprocal-transform bias emphasized in the background question.
2. Add error bars or distribution plots for recovery error across replicates, not only medians.
3. Consider a denser noise sweep around 5% to 20% to identify the transition region more precisely.
4. Create `HYPOTHESIS_03.md` and `script_03_inhibition_apparent_parameters.py` to generate competitive or noncompetitive inhibition data and confirm the expected apparent Km/Vmax shift.

## Conclusion

Iteration 02 partially supports the broader concern about Lineweaver-Burk instability but does not support the strict hypothesis that Lineweaver-Burk breaks earlier than nonlinear fitting under the selected relative-noise model. Both methods are accurate at 0% and 3% noise. Nonlinear fitting fails the 10% Km threshold at 10% noise, both methods fail at 20% noise, and Lineweaver-Burk becomes clearly unstable at 40% noise with invalid fits and much larger median errors.
