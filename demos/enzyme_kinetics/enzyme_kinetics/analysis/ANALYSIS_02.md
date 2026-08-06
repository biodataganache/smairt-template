# ANALYSIS_02 - Nonlinear versus Lineweaver-Burk across five noise levels

Hypothesis: `hypotheses/HYPOTHESIS_02.md`
Iteration: 02
Log: recorded in `analysis/RUN_HISTORY.md`

## What was measured

50 replicates at each of five relative-noise levels, both methods, against planted Vmax 100.0 and
Km 5.0. Medians reported because a single near-singular reciprocal fit dominates a mean.

| Noise | Method | Valid | Median Vmax err | Median Km err | Median R^2 | Credible |
|---|---|---|---|---|---|---|
| 0% | nonlinear | 50/50 | 0.000% | 0.000% | 1.00000 | yes |
| 0% | Lineweaver-Burk | 50/50 | 0.000% | 0.000% | 1.00000 | yes |
| 3% | nonlinear | 50/50 | 1.635% | 3.858% | 0.99740 | yes |
| 3% | Lineweaver-Burk | 50/50 | 2.357% | 3.744% | 0.99578 | yes |
| 10% | nonlinear | 50/50 | 5.057% | 10.654% | 0.97604 | **no** |
| 10% | Lineweaver-Burk | 50/50 | 6.531% | 12.849% | 0.95921 | **no** |
| 20% | nonlinear | 50/50 | 9.584% | 21.217% | 0.90583 | no |
| 20% | Lineweaver-Burk | 50/50 | 22.518% | 26.245% | 0.77844 | no |
| 40% | nonlinear | 50/50 | 23.360% | 47.135% | 0.68605 | no |
| 40% | Lineweaver-Burk | **43/50** | 35.969% | 49.971% | 0.36982 | no |

## Against the predeclared criteria

The breakdown rule was: the first noise level where Lineweaver-Burk fails while nonlinear remains
credible. **No tested level triggered it.** The prediction is **not supported**.

Both methods fail at the same level, 10%, and both fail on Km rather than Vmax. The 0% control
behaved correctly, with both methods recovering truth exactly, which is what makes the rest of
the table trustworthy.

## Interpretation

This is the most instructive iteration in the demo, precisely because the prediction was wrong.

The reasoning behind the prediction was that the double-reciprocal transform overweights noisy
low-velocity points. That reasoning assumes noise of roughly constant absolute size. Under the
*relative* noise model used here, a low velocity carries a proportionally small error, so the
reciprocal transform is not handed the disproportionately noisy points the argument depends on.
The noise model, not the transform, decided the outcome.

What does survive: Lineweaver-Burk is meaningfully worse at high noise. At 20% its median Vmax
error is 22.518% against nonlinear's 9.584%, and at 40% it produces nonphysical parameters in 7
of 50 replicates while nonlinear produces none. Its median R^2 collapses to 0.370 against 0.686.
So the general preference for nonlinear fitting is justified; the specific claim that it fails
*later* is not.

Because the criteria and the breakdown rule were committed before the run, this reads as a
finding about the noise model. Had they been written afterwards, the same numbers could have been
presented as support for a vaguer claim about Lineweaver-Burk being worse, which the data do also
show. The ordering is what makes the difference visible.

## Consequence for the next iteration

Iteration 03 uses nonlinear fitting as the primary method on real data and reports
Lineweaver-Burk only as a diagnostic. This iteration is why that is a defended choice rather than
an inherited convention.
