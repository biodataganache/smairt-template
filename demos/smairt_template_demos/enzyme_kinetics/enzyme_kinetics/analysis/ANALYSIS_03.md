# ANALYSIS_03.md

## Script

`experiments/02_downloaded/script_03_puromycin_real_fit.py`

## Hypothesis

`hypotheses/HYPOTHESIS_03.md`

Direct nonlinear least-squares fitting of the Michaelis-Menten equation to the public R `Puromycin` initial-rate dataset should produce positive, finite, biologically plausible Vmax and Km estimates for both treated and untreated conditions. The fitted curves should follow the observed saturation pattern, and the treated condition should show an interpretable difference in fitted kinetic parameters relative to the untreated condition.

## Dataset

- Source: R `datasets::Puromycin`
- Cached file: `data/downloaded/puromycin_rates.csv`
- Data type: public downloaded enzyme initial-rate data
- Conditions: treated and untreated
- Variables: substrate concentration (`conc`), reaction rate (`rate`), condition (`state`)

This is real/downloaded data, so there is no planted truth. Correctness is judged by validation checks, fit convergence, positive finite parameters, finite uncertainty estimates, residual diagnostics, and visual agreement with the observed saturation pattern.

## Output artifacts

- Log file: `results/logs/script_03_puromycin_real_fit_20260713_141424.log`
- Fit summary CSV: `results/script_03_puromycin_real_fit_fit_summary.csv`
- Fitted curve figure: `results/figures/script_03_puromycin_real_fit_fit_curves.png`
- Residual figure: `results/figures/script_03_puromycin_real_fit_residuals.png`
- Script with pasted-output block: `experiments/02_downloaded/script_03_puromycin_real_fit.py`

## Data validation results

| Check | Result |
|-------|--------|
| Required columns present (`conc`, `rate`, `state`) | Pass |
| Loaded rows | 23 |
| All substrate concentrations positive and finite | Pass |
| All reaction rates positive and finite | Pass |
| Expected states observed (`treated`, `untreated`) | Pass |
| Treated observation count | 12 |
| Treated unique concentrations | 6 |
| Untreated observation count | 11 |
| Untreated unique concentrations | 6 |
| Overall validation | Pass |

## Nonlinear fit results

| Condition | Vmax | Km | Vmax 95% CI | Km 95% CI | RSS | R^2 |
|-----------|------|----|-------------|-----------|-----|-----|
| Treated | 212.683859 | 0.064121 | [197.204618, 228.163100] | [0.045670, 0.082573] | 1195.448814 | 0.961261 |
| Untreated | 160.280124 | 0.047708 | [145.620777, 174.939470] | [0.030104, 0.065312] | 859.604294 | 0.935572 |

## Condition comparison

| Comparison | Value |
|------------|-------|
| Treated / untreated Vmax ratio | 1.326951 |
| Treated / untreated Km ratio | 1.344031 |
| Treated Vmax higher than untreated Vmax | True |

The treated condition has a higher fitted Vmax than the untreated condition. It also has a somewhat higher fitted Km. The Vmax confidence intervals do not overlap much and suggest a clear condition-level difference in maximum rate. The Km confidence intervals overlap, so the Km difference should be interpreted more cautiously.

## Lineweaver-Burk diagnostic comparison

| Condition | Nonlinear Vmax | LB Vmax | Vmax difference | Nonlinear Km | LB Km | Km difference | Material disagreement |
|-----------|----------------|---------|-----------------|--------------|-------|---------------|-----------------------|
| Treated | 212.683859 | 195.802709 | 7.937% | 0.064121 | 0.048407 | 24.508% | True |
| Untreated | 160.280124 | 143.428116 | 10.514% | 0.047708 | 0.030837 | 35.363% | True |

Lineweaver-Burk materially disagreed with the nonlinear fit for Km in both conditions. This supports treating Lineweaver-Burk as a diagnostic comparator rather than the trusted primary estimate on this real dataset.

## Output correctness checklist

| Check | Result |
|-------|--------|
| Data validation passed | True |
| All nonlinear fits converged | True |
| All nonlinear parameters positive and finite | True |
| All approximate uncertainty estimates finite | True |
| All conditions sample above fitted Km | True |
| Non-visual output correctness checks passed | True |
| Visual fitted-curve check | Pass |
| Visual residual check | Pass with moderate scatter |

## Interpretation

Hypothesis 03 passes. The public Puromycin dataset produced positive, finite Michaelis-Menten parameter estimates for both treated and untreated conditions. The fitted curves show the expected saturation pattern and track the data reasonably well. The residual plot shows scatter around zero with moderate deviations but no obvious monotone failure across the full substrate range.

The treated condition has a substantially higher fitted Vmax than the untreated condition, consistent with the visible higher reaction rates at high substrate concentrations. Treated Vmax is estimated at 212.683859, while untreated Vmax is estimated at 160.280124. This gives a treated/untreated Vmax ratio of 1.326951.

The treated condition also has a higher fitted Km, 0.064121 versus 0.047708, but this difference is less definitive because the confidence intervals overlap. Therefore, the strongest condition-level conclusion is that the treated condition has a higher apparent maximum rate.

Lineweaver-Burk estimates materially disagree with nonlinear estimates, especially for Km. On treated data, Lineweaver-Burk Km is 24.508% lower than nonlinear Km. On untreated data, Lineweaver-Burk Km is 35.363% lower than nonlinear Km. This real-data result aligns with the broader concern that reciprocal linearization can materially change parameter estimates.

## Limitations observed

- This public dataset is small: 23 total observations across two conditions.
- Replicate structure is simple and not modeled hierarchically.
- Confidence intervals are approximate and derived from the nonlinear least-squares covariance matrix.
- Units are inherited from the source dataset and are not independently checked here.
- R^2 is reported only as secondary context; it is not sufficient by itself to validate kinetic parameter estimates.
- There is no planted truth in this real/downloaded dataset, so correctness is based on validation and diagnostics rather than true recovery error.

## Next steps

1. Add a bootstrap confidence interval script for Puromycin parameters to avoid relying only on covariance-based uncertainty.
2. Fit a shared-condition model that estimates condition effects more directly, such as separate Vmax but shared Km, or separate Vmax and Km with formal comparison.
3. Return to the mechanistic synthetic extension and create an inhibition dataset to verify expected apparent Km/Vmax shifts.
4. Compare with another public enzyme kinetics dataset to test whether the workflow generalizes beyond Puromycin.

## Conclusion

Iteration 03 successfully demonstrates the SMAIRT workflow on public real/downloaded enzyme kinetics data. The output is correct under the predeclared validation and diagnostic criteria: the data load cleanly, nonlinear fits converge, parameters and uncertainty estimates are finite, fitted curves match the observed saturation pattern, and condition-level differences are interpretable.
