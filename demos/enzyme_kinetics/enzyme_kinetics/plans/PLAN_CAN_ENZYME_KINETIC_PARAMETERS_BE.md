# Plan: Can enzyme kinetic parameters be recovered from measured reaction velocities?

## Status

COMPLETE

## Hypothesis

`hypotheses/HYPOTHESIS_01.md`, `hypotheses/HYPOTHESIS_02.md`, `hypotheses/HYPOTHESIS_03.md`

## Problem statement

Fitting the Michaelis-Menten equation is routine; knowing whether the fitted Vmax and Km can be
trusted is not. One iteration cannot answer this, because a single fit on real data gives no way
to measure recovery error. The question needs a setting where truth is known, a stress test, and
only then a real dataset.

## Approach

1. Establish a positive control on synthetic data with planted parameters at low noise. If
   recovery fails here, nothing on real data could be trusted. Expected to pass; its value is
   that failure would stop the track.
2. Compare direct nonlinear least squares against Lineweaver-Burk linearization across five noise
   levels with 50 replicates each. Expected to show Lineweaver-Burk failing earlier. The purpose
   is to earn the choice of primary method rather than inherit it.
3. Apply the chosen method to a public real dataset with two conditions, where the claim shifts
   from correctness to credibility.

## Success criteria

The track succeeds if the choice of fitting method for iteration 03 is justified by measurement
rather than convention, and if the real-data estimates come with enough uncertainty information
to say which reported differences are real.

## Dependencies

- [x] Data: `data/downloaded/puromycin_rates.csv`, provenance and checksum in
      `data/downloaded/README.md`
- [x] Code: numpy, scipy, matplotlib
- [x] Results: iterations 01 and 02 interpreted before iteration 03 runs

## Steps

1. [x] Iteration 01: nonlinear recovery at 3% noise
2. [x] Iteration 02: both methods across 0-40% noise, 50 replicates each
3. [x] Iteration 03: nonlinear fit on the Puromycin dataset, both conditions

## Expected outputs

- Three iterations, three analyses, one selected result
- Figures: fitted curve, median error against noise, real-data fits and residuals

## Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| A fit converges only because the initial guess was near truth | Medium | Offset the guess from truth in iteration 01 |
| A single replicate dominates the method comparison | High | 50 replicates per level, medians not means |
| A plausible real-data fit is mistaken for a correct one | Medium | Report intervals and residuals; claim credibility, not correctness |

## Iterations

| Iteration | What it tested | Outcome |
|---|---|---|
| 01 | Nonlinear recovery at 3% noise | Supported: Vmax 2.626%, Km 6.424% error |
| 02 | Nonlinear versus Lineweaver-Burk, five noise levels | **Not supported**: nonlinear failed first, at 10% |
| 03 | Nonlinear fit on real Puromycin data | Supported: credible parameters, treated Vmax higher |

## Notes

The track's most useful result is the refutation in iteration 02. The prediction that
Lineweaver-Burk would fail earlier rested on an assumption about the noise model that the
experiment did not satisfy, and the predeclared breakdown rule is what made that visible. The
choice of nonlinear fitting for iteration 03 still stands, but on the evidence actually gathered:
Lineweaver-Burk is unstable at high noise, not earlier-failing at moderate noise.
