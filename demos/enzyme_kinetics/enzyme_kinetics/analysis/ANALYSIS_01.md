# ANALYSIS_01 - Synthetic nonlinear recovery at 3% noise

Hypothesis: `hypotheses/HYPOTHESIS_01.md`
Iteration: 01
Log: recorded in `analysis/RUN_HISTORY.md`

## What was measured

| Quantity | Planted | Fitted | Relative error |
|---|---|---|---|
| Vmax | 100.0 | 97.373584 | 2.626% |
| Km | 5.0 | 4.678811 | 6.424% |

Residual sum of squares 14.675522, R^2 0.998404 on the noisy observations. Standard errors 1.032
for Vmax and 0.162 for Km.

## Against the predeclared criteria

1. Vmax relative error <= 10%: **met** at 2.626%.
2. Km relative error <= 10%: **met** at 6.424%.
3. Fitted curve follows observations and saturates near planted Vmax: **met**, see
   `results/figures/script_01_synthetic_nonlinear_fit_fit_curve.png`.
4. Parameters physically meaningful: **met**, both positive.

## Interpretation

The positive control passes. Direct nonlinear least squares recovers both planted parameters from
12 points at 3% relative noise, from an initial guess deliberately offset from truth, so
convergence rather than the starting point produced the answer.

Km is recovered less precisely than Vmax, at 6.424% against 2.626%. That asymmetry is expected
and worth noting: Vmax is constrained by the high-concentration plateau where many points sit,
while Km is constrained by the curvature near the transition, which fewer points cover. It
anticipates the finding in iteration 02, where Km is the parameter that fails first for both
methods.

## What this does not establish

Only that the method works where noise is low and truth is known. Whether it degrades gracefully,
and whether it beats the classical alternative, is iteration 02.
