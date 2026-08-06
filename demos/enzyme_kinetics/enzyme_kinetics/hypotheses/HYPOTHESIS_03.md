# HYPOTHESIS_03 - The validated method produces plausible parameters on a public real dataset

## Status

SUPPORTED

## Background

Iterations 01 and 02 established nonlinear least squares as the trustworthy method on synthetic
data where truth was known. Real assay data has no planted truth, so the question changes: not
"is the estimate correct" but "is the estimate credible, and does the model fit the observed
saturation". The Puromycin initial-rate dataset is public, small, and has two conditions, so it
tests the method where the answer cannot be checked against a planted value.

## Hypothesis Statement

**Prediction**: Direct nonlinear fitting of the Michaelis-Menten equation to the public
Puromycin dataset will produce positive, finite, biologically plausible Vmax and Km for both
treated and untreated conditions, the fitted curves will follow the observed saturation, and the
treated condition will show an interpretable difference in kinetic parameters.

**Rationale**: The dataset covers concentrations spanning the saturation transition for both
conditions, which is what makes Km identifiable.

**Alternative explanations**: A plausible-looking fit does not prove the Michaelis-Menten model
is right for this enzyme. Residuals are inspected for systematic structure for that reason, and
this iteration claims credibility rather than correctness.

**Success criteria**:

1. The data file loads and has columns `conc`, `rate`, `state`.
2. All concentrations and rates are positive.
3. Each condition has >= 5 observations and >= 4 unique concentrations.
4. Fits converge for both conditions.
5. Fitted Vmax and Km are positive and finite for both.
6. Standard errors and approximate 95% confidence intervals are finite.
7. Fitted curves follow the observed saturation pattern.
8. Residuals show no obvious systematic failure of the model.

**Rejection criteria**: A non-converging fit, a negative or infinite parameter, or clearly
structured residuals would mean the method does not transfer to this real dataset.

## Experimental Design

- **Phase**: downloaded
- **Data**: `data/downloaded/puromycin_rates.csv`, provenance recorded in
  `data/downloaded/README.md`. 23 observations, treated and untreated.
- **Controls**: The untreated condition is the comparison for the treated condition.
- **Key metrics**: Fitted Vmax and Km with standard errors and 95% intervals, RSS, R^2,
  residual summaries. Lineweaver-Burk is reported only as a diagnostic comparator.
- **Randomness**: None. The fit is deterministic given the cached data.

## Dependencies

- Iterations 01 and 02, which established the method
- The cached dataset and its provenance record

## Iterations

| Iteration | What it tested | Outcome |
|---|---|---|
| 03 | Nonlinear fit on real Puromycin data, both conditions | Plausible finite parameters, treated Vmax higher |

## Results

See `analysis/ANALYSIS_03.md`.

## Notes

Lineweaver-Burk is retained here as a diagnostic only. Iteration 02 is the reason it is not the
primary fit.
