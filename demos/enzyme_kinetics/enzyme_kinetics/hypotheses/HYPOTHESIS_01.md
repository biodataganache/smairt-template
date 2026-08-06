# HYPOTHESIS_01 - Low-noise synthetic data are sufficient to validate direct nonlinear parameter recovery

## Status

SUPPORTED

## Background

The project question asks whether enzyme kinetic parameters can be recovered from measured
reaction velocities at several substrate concentrations. Synthetic data can be generated from
known parameters, so the first iteration establishes a positive control before adding higher
noise, alternate fitting methods, or real assay complications. If recovery fails here, nothing
measured on real data could be trusted.

## Hypothesis Statement

**Prediction**: If velocity-versus-substrate data are generated from the Michaelis-Menten
equation with known parameters and low relative measurement noise, a direct nonlinear
least-squares fit will recover both planted parameters within 10% relative error.

**Rationale**: The substrate range spans below, near, and above Km, so the saturation curve is
identifiable from the observations. At 3% noise the signal dominates.

**Alternative explanations**: A fit could appear accurate because the initial guess was already
close to truth rather than because the data constrain the parameters. The guess is deliberately
offset from truth (90.0, 4.0 against 100.0, 5.0) so convergence is doing the work.

**Success criteria**:

1. Relative Vmax recovery error <= 10%.
2. Relative Km recovery error <= 10%.
3. The fitted curve follows the noisy observations and saturates near the planted Vmax.
4. Fitted parameters are physically meaningful: Vmax > 0 and Km > 0.

**Rejection criteria**: Either relative error above 10%, a non-converging fit, or a negative
fitted parameter would refute the claim that this method is a usable baseline.

## Experimental Design

- **Phase**: synthetic
- **Data**: Generated in-script from planted parameters. No external input.
- **Controls**: The clean noiseless curve is plotted against the fit as the reference.
- **Key metrics**: Fitted Vmax and Km, absolute and relative error, residual sum of squares, R^2.
- **Randomness**: Seed 1024, fixed in the script's CONFIG and recorded by `write_provenance`.

## Planted true parameters

| Quantity | Value |
|---|---|
| True Vmax | 100.0 rate units |
| True Km | 5.0 concentration units |
| Substrate range | 0.5 to 50.0 concentration units |
| Substrate points | 12 |
| Relative measurement noise | 3% of clean velocity |
| Random seed | 1024 |

## Dependencies

- `background/01_initial_question.md`

## Iterations

| Iteration | What it tested | Outcome |
|---|---|---|
| 01 | Nonlinear recovery at 3% noise | Both parameters recovered within 10% |

## Results

See `analysis/ANALYSIS_01.md` and the log recorded in `analysis/RUN_HISTORY.md`.

## Notes

The initial guess is offset from truth on purpose, so this tests convergence rather than
restating the answer.
