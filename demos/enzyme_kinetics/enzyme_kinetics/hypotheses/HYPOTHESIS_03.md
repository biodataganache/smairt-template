# HYPOTHESIS_03.md

## Title

A public real enzyme initial-rate dataset should yield positive, finite Michaelis-Menten parameter estimates with interpretable condition differences.

## Background

Iterations 01 and 02 used synthetic data where the planted Km and Vmax were known. Hypothesis 03 moves to a public real enzyme kinetics dataset: the R `Puromycin` dataset, a classic initial-rate dataset measuring reaction velocity at different substrate concentrations for treated and untreated cells.

Because this is not synthetic data, there is no planted truth. Output correctness must therefore be judged by data validation, parameter plausibility, uncertainty estimates, residual diagnostics, visual agreement with the observed saturation pattern, and reproducibility of the logged results.

## Hypothesis

Direct nonlinear least-squares fitting of the Michaelis-Menten equation to the public Puromycin initial-rate dataset will produce positive, finite, biologically plausible Vmax and Km estimates for both treated and untreated conditions. The fitted curves should follow the observed saturation pattern, and the treated condition should show an interpretable difference in fitted kinetic parameters relative to the untreated condition.

## Dataset

| Field | Description |
|-------|-------------|
| Source | R `datasets::Puromycin` |
| Data type | Public enzyme initial-rate data |
| Variables | substrate concentration, reaction rate, treatment condition |
| Conditions | treated, untreated |
| Cached file | `data/downloaded/puromycin_rates.csv` |

## Correctness criteria

The output will be considered trustworthy if:

1. The data file loads successfully and has the required columns: `conc`, `rate`, and `state`.
2. All substrate concentrations and reaction rates are positive.
3. Each condition has at least five observations and at least four unique substrate concentrations.
4. Nonlinear fits converge for both treated and untreated conditions.
5. Fitted Vmax and Km are positive and finite for both conditions.
6. Parameter standard errors and approximate 95% confidence intervals are finite.
7. The fitted curve visually follows the observed saturation pattern.
8. Residuals do not show an obvious systematic failure of the Michaelis-Menten model.
9. Lineweaver-Burk estimates, if reported, are treated as diagnostics rather than the trusted primary fit.

## Experiment design

1. Cache the public Puromycin dataset in `data/downloaded/puromycin_rates.csv`.
2. Load the cached CSV and validate schema, positivity, condition labels, and sample counts.
3. Fit the Michaelis-Menten equation separately for treated and untreated conditions using direct nonlinear least squares.
4. Estimate standard errors and approximate 95% confidence intervals from the covariance matrix.
5. Compute residual sum of squares, R^2, and residual summaries for each condition.
6. Fit Lineweaver-Burk as a diagnostic comparator and report whether it materially disagrees with nonlinear fitting.
7. Save a fitted-curve plot overlaying data and nonlinear fits by condition.
8. Save a residual plot by condition.
9. Write console output and a timestamped log using TeeLogger.
10. Add the run output to the pasted-output block at the end of the script.
11. Write `analysis/ANALYSIS_03.md` interpreting whether the real-data output passes the correctness criteria.

## Expected result

Both conditions should produce positive, finite nonlinear parameter estimates and saturation-shaped curves. The treated condition is expected to have a higher apparent maximum rate than the untreated condition because the observed treated rates reach higher values at high substrate concentration.

## Next steps

If Hypothesis 03 passes, later work can either:

- compare more public real datasets, or
- return to mechanistic synthetic extensions such as competitive and noncompetitive inhibition.
