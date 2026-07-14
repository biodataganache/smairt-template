# HYPOTHESIS_01.md

## Title

Low-noise synthetic Michaelis-Menten data are sufficient to validate direct nonlinear parameter recovery.

## Background

The initial project question asks whether enzyme kinetic parameters can be recovered from measured reaction velocities at several substrate concentrations. Because synthetic data can be generated from known parameters, the first experiment should establish a simple positive control before adding higher noise, alternate fitting methods, or real assay complications.

## Hypothesis

If velocity-versus-substrate data are generated from the Michaelis-Menten equation with known parameters and low relative measurement noise, then a direct nonlinear least-squares fit of the Michaelis-Menten equation will recover both planted parameters within 10% relative error.

## Planted true parameters

| Quantity | Value |
|----------|-------|
| True Vmax | 100.0 rate units |
| True Km | 5.0 concentration units |
| Substrate range | 0.5 to 50.0 concentration units |
| Number of substrate points | 12 |
| Relative measurement noise | 3% of clean velocity |
| Random seed | 1024 |

## Credibility criterion

The nonlinear least-squares method will be considered credible for this first low-noise synthetic positive control if:

1. Relative Vmax recovery error is less than or equal to 10%.
2. Relative Km recovery error is less than or equal to 10%.
3. The plotted fitted curve visually follows the noisy observations and saturates near the planted Vmax.
4. The fitted parameters are physically meaningful: Vmax > 0 and Km > 0.

## Experiment design

1. Generate substrate concentrations spanning below and above Km, from 0.5 to 50.0.
2. Compute clean Michaelis-Menten velocities using Vmax = 100.0 and Km = 5.0.
3. Add Gaussian noise with standard deviation equal to 3% of each clean velocity.
4. Fit the noisy data using scipy.optimize.curve_fit with the Michaelis-Menten equation directly, not a reciprocal transform.
5. Report fitted Vmax, fitted Km, absolute errors, relative errors, residual sum of squares, and R^2.
6. Save a figure overlaying the noisy data, clean truth curve, and nonlinear fitted curve.
7. Write output to both console and results/logs using TeeLogger.

## Expected result

The nonlinear fit should recover Vmax and Km within 10% relative error. Because the data are low-noise and cover substrate concentrations below, near, and above Km, the saturation curve should be identifiable from the generated observations.

## Later iterations

- HYPOTHESIS_02 should raise noise across multiple levels, such as 0%, 3%, 10%, and 20%, to map when nonlinear parameter recovery starts to degrade.
- HYPOTHESIS_03 should add a Lineweaver-Burk double-reciprocal fit and compare recovery errors against nonlinear least squares, with the expectation that reciprocal linearization becomes biased as noise increases.
- Optional later hypotheses can add inhibition models or small real datasets once the synthetic workflow is validated.
