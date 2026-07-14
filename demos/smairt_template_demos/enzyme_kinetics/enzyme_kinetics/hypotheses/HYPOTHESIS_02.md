# HYPOTHESIS_02.md

## Title

Increasing measurement noise reveals Lineweaver-Burk bias relative to direct nonlinear Michaelis-Menten fitting.

## Background

Iteration 01 established that direct nonlinear least-squares fitting can recover planted Michaelis-Menten parameters from low-noise synthetic data. The next question is whether this baseline remains more accurate than the classic Lineweaver-Burk double-reciprocal linearization as measurement noise increases.

Lineweaver-Burk fitting transforms the Michaelis-Menten equation into:

`1/v = (Km/Vmax)(1/[S]) + 1/Vmax`

This makes the problem linear, but the reciprocal transform amplifies error in low-substrate and low-velocity measurements. Therefore, noise that is modest on the original velocity scale can become disproportionately influential on the reciprocal scale.

## Hypothesis

As synthetic measurement noise increases, direct nonlinear least-squares fitting of the original velocity-versus-substrate data will recover planted Vmax and Km more accurately than Lineweaver-Burk fitting. Lineweaver-Burk recovery should break the 10% relative-error credibility threshold earlier than nonlinear fitting, especially for Km.

## Planted true parameters

| Quantity | Value |
|----------|-------|
| True Vmax | 100.0 rate units |
| True Km | 5.0 concentration units |
| Substrate range | 0.5 to 50.0 concentration units |
| Number of substrate points | 12 |
| Noise levels | 0%, 3%, 10%, 20%, 40% |
| Replicates per noise level | 50 |
| Base random seed | 2048 |

## Credibility criterion

A method is considered credible at a given noise level if median relative error is less than or equal to 10% for both Vmax and Km across replicates.

Lineweaver-Burk is considered to have broken down at the first tested noise level where either median Vmax error or median Km error exceeds 10% while the nonlinear fit remains within that threshold, or at the first tested noise level where Lineweaver-Burk produces invalid parameters in a substantial fraction of replicates.

## Experiment design

1. Generate synthetic Michaelis-Menten velocity data from Vmax = 100.0 and Km = 5.0.
2. Sweep relative Gaussian noise levels: 0%, 3%, 10%, 20%, and 40% of clean velocity.
3. Use 50 replicate datasets per noise level with a fixed base seed for reproducibility.
4. Fit each dataset using direct nonlinear least squares on the original velocity scale.
5. Fit each dataset using Lineweaver-Burk linear regression on 1/v versus 1/[S].
6. Convert Lineweaver-Burk slope and intercept into Vmax and Km.
7. Compare both methods against planted truth using absolute and relative recovery errors for Vmax and Km.
8. Summarize median, mean, and worst-case relative errors by method and noise level.
9. Save figures showing error versus noise level and representative fits.
10. Write output to both console and results/logs using TeeLogger.

## Expected result

The nonlinear fit should remain accurate at low and moderate noise levels, while Lineweaver-Burk should show larger Km and/or Vmax errors as noise increases. Because the reciprocal transform overweights low-substrate noisy points, Lineweaver-Burk is expected to cross the 10% median-error threshold earlier than nonlinear least squares.

## Later iterations

- HYPOTHESIS_03 should generate data under an inhibition model and verify the expected apparent parameter shift.
- A competitive inhibitor should increase apparent Km while leaving Vmax approximately unchanged.
- A noncompetitive inhibitor should reduce apparent Vmax while leaving Km approximately unchanged.
