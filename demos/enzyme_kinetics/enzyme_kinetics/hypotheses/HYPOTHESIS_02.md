# HYPOTHESIS_02 - Nonlinear least squares degrades more slowly than Lineweaver-Burk as noise rises

## Status

NOT SUPPORTED

## Background

Iteration 01 showed direct nonlinear fitting recovers planted parameters at 3% noise. The
Lineweaver-Burk double-reciprocal plot is the classical hand-calculation method and is still
taught. Because it fits 1/v against 1/[S], measurement noise on small velocities is amplified,
so the two methods should diverge as noise grows. That divergence is worth measuring rather than
asserting.

## Hypothesis Statement

**Prediction**: As synthetic measurement noise increases, direct nonlinear least-squares fitting
will recover planted Vmax and Km more accurately than Lineweaver-Burk fitting. Lineweaver-Burk
will break the 10% relative-error threshold at a lower noise level than nonlinear fitting,
especially for Km.

**Rationale**: The reciprocal transform overweights low-substrate, low-velocity points, which
carry the largest relative error. Nonlinear fitting on the original scale weights each
observation by its own magnitude.

**Alternative explanations**: A single unlucky replicate could produce the difference, so the
comparison uses 50 replicates per noise level and reports medians rather than one fit.

**Success criteria**: A method is credible at a noise level if median relative error <= 10% for
both Vmax and Km across replicates. Lineweaver-Burk has broken down at the first noise level
where either median error exceeds 10% while the nonlinear fit stays within it, or where it
produces invalid parameters in a substantial fraction of replicates.

**Rejection criteria**: If Lineweaver-Burk matched or beat nonlinear fitting at every tested
noise level, the prediction would be refuted and the reciprocal transform's reputation for noise
sensitivity would not apply at this scale.

## Experimental Design

- **Phase**: synthetic
- **Data**: Generated in-script from the same planted parameters as iteration 01.
- **Controls**: The 0% noise level is the control; both methods must agree there.
- **Key metrics**: Median, mean, and worst-case relative error for Vmax and Km, by method and
  noise level; count of invalid Lineweaver-Burk fits.
- **Randomness**: Base seed 2048, 50 replicates per noise level.

## Planted true parameters

| Quantity | Value |
|---|---|
| True Vmax | 100.0 rate units |
| True Km | 5.0 concentration units |
| Substrate range | 0.5 to 50.0 concentration units |
| Substrate points | 12 |
| Noise levels | 0%, 3%, 10%, 20%, 40% |
| Replicates per noise level | 50 |
| Base random seed | 2048 |

## Dependencies

- Iteration 01, interpreted in `analysis/ANALYSIS_01.md`

## Iterations

| Iteration | What it tested | Outcome |
|---|---|---|
| 02 | Both methods across five noise levels | Prediction refuted: nonlinear failed the Km criterion at 10% noise while Lineweaver-Burk held |

## Results

See `analysis/ANALYSIS_02.md`.

## Outcome

The prediction was refuted, and this is the most instructive iteration in the demo.

At 10% relative noise the *nonlinear* fit failed the criterion, with median Km error 12.666%,
while Lineweaver-Burk stayed inside it at 8.856%. The predeclared breakdown rule -- the first
level where Lineweaver-Burk fails while nonlinear holds -- was never triggered at any tested
level. Lineweaver-Burk's expected reciprocal bias does not dominate under a *relative* noise
model, because relative noise keeps the low-velocity points that the reciprocal transform
overweights from becoming disproportionately noisy.

Lineweaver-Burk does become clearly unstable at 40% noise, producing invalid parameters in 10 of
50 replicates against nonlinear's 0. So the broader concern about its stability survives; the
specific ordering claim does not.

The criteria were committed before the run, which is the only reason this reads as a finding
rather than as a mistake to be quietly corrected. Iteration 03 uses nonlinear fitting as the
primary method on real data, with Lineweaver-Burk kept as a diagnostic, and iteration 02 is why
that choice is defensible rather than conventional.

## Notes

Reporting medians matters here: a mean over replicates that include a near-singular reciprocal
fit is dominated by that one fit and would overstate the effect.

The noise model is the load-bearing assumption. Under *absolute* rather than relative noise the
result would plausibly reverse, and this iteration does not test that.
