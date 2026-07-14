# ANALYSIS_01.md

## Script

`experiments/01_synthetic/script_01_synthetic_nonlinear_fit.py`

## Hypothesis

`hypotheses/HYPOTHESIS_01.md`

Low-noise synthetic Michaelis-Menten data should allow direct nonlinear least-squares recovery of planted Km and Vmax within 10% relative error.

## Background question

The project asks whether enzyme kinetic parameters Km and Vmax can be recovered from reaction velocity measurements at several substrate concentrations. This first iteration is a synthetic positive control: because the true parameters are known, recovery error can be measured directly.

## Methods summary

- Planted Vmax: 100.0 rate units
- Planted Km: 5.0 concentration units
- Substrate range: 0.5 to 50.0 concentration units
- Number of substrate points: 12
- Noise model: Gaussian noise with standard deviation equal to 3% of clean velocity
- Random seed: 1024
- Fitting method: direct nonlinear least squares with the Michaelis-Menten equation
- Credibility criterion: both Vmax and Km recovered within 10% relative error

## Output artifacts

- Log file: `results/logs/script_01_synthetic_nonlinear_fit_20260713_135205.log`
- Figure file: `results/figures/script_01_synthetic_nonlinear_fit_fit_curve.png`
- Script with pasted-output block: `experiments/01_synthetic/script_01_synthetic_nonlinear_fit.py`

## Key results

| Metric | Value |
|--------|-------|
| Fitted Vmax | 97.373584 |
| Fitted Km | 4.678811 |
| Vmax absolute error | 2.626416 |
| Km absolute error | 0.321189 |
| Vmax relative error | 2.626% |
| Km relative error | 6.424% |
| Residual sum of squares | 14.675522 |
| R^2 on noisy observations | 0.998404 |
| Passed <=10% criterion | True |

## Interpretation

The first synthetic positive control supports the hypothesis. With low 3% relative measurement noise, direct nonlinear least-squares fitting recovered both planted parameters within the predeclared 10% relative-error threshold. Vmax was recovered especially closely at 2.626% relative error, and Km was recovered at 6.424% relative error.

The plotted fitted curve tracks the noisy synthetic observations and follows the same saturating shape as the planted truth curve. The fitted curve is slightly below the planted truth at high substrate concentrations because several high-substrate noisy observations fell below the clean curve. This is expected behavior for a least-squares fit to noisy observations rather than evidence of model failure.

The high R^2 value of 0.998404 confirms that the Michaelis-Menten curve explains nearly all observed variance in this low-noise synthetic dataset. Because the fitted parameters are positive and physically meaningful, the method is a credible baseline for subsequent tests.

## Limitations observed

- This test uses only one fixed random seed and one low noise level.
- The result does not yet show robustness across repeated simulations or higher noise.
- The result does not yet compare nonlinear fitting against Lineweaver-Burk reciprocal linearization.
- Confidence intervals were not interpreted beyond printing the covariance matrix.
- The synthetic data exactly match the fitted model form, so this is a positive-control test rather than a realistic assay stress test.

## Next steps

1. Create `HYPOTHESIS_02.md` and `script_02_noise_sweep_nonlinear_fit.py` to repeat nonlinear recovery across multiple noise levels, such as 0%, 3%, 10%, and 20%, ideally with multiple seeds per noise level.
2. Create `HYPOTHESIS_03.md` and `script_03_lineweaver_burk_comparison.py` to compare nonlinear least squares against the Lineweaver-Burk double-reciprocal method under the same synthetic noise conditions.
3. Add confidence interval reporting for fitted Km and Vmax once the core recovery workflow is stable.
4. Consider adding inhibition simulations after establishing the nonlinear-vs-linearized comparison.

## Conclusion

Iteration 01 passes. Direct nonlinear least-squares fitting is validated as the baseline method for recovering Km and Vmax from low-noise synthetic Michaelis-Menten data with known truth.
