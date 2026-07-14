# Final Report — Michaelis-Menten Parameter Recovery Across Synthetic and Public Enzyme Kinetics Data

| Field | Details |
|---|---|
| Research Project | Enzyme kinetics parameter estimation |
| Study Scope | Estimation of Michaelis-Menten Km and Vmax from velocity-versus-substrate data across controlled synthetic data and a public enzyme kinetics dataset. |
| Methodological Approach | Hypothesis-driven computational study using synthetic positive controls, noise stress tests, method comparison, and public-data validation. |
| Generated | 2026-07-13 |
| Last Updated | 2026-07-13 |
| Report Status | FINAL |
| Primary Sources | [background/01_initial_question.md](../background/01_initial_question.md); [ANALYSIS_01.md](ANALYSIS_01.md); [ANALYSIS_02.md](ANALYSIS_02.md); [ANALYSIS_03.md](ANALYSIS_03.md) |

---

## 1. Executive Summary

This study evaluated how accurately Michaelis-Menten parameters can be estimated from reaction velocity measurements at different substrate concentrations. The central question was whether Km and Vmax can be recovered reliably from velocity-versus-substrate data, especially when measurement noise is present, and whether direct nonlinear least-squares fitting is preferable to the Lineweaver-Burk double-reciprocal transformation.

The first synthetic experiment established a positive control: direct nonlinear least-squares fitting recovered planted parameters from low-noise data within the predeclared 10% relative-error criterion. The fitted Vmax was 97.373584 versus true Vmax = 100, and the fitted Km was 4.678811 versus true Km = 5, corresponding to 2.626% Vmax error and 6.424% Km error.

The second synthetic experiment increased noise and compared nonlinear fitting with Lineweaver-Burk fitting. Both methods performed correctly on noiseless and 3% relative-noise data. Under the selected relative-noise model, the strict hypothesis that Lineweaver-Burk would fail earlier than nonlinear fitting was not supported: nonlinear Km median error exceeded 10% at 10% noise while Lineweaver-Burk remained within threshold at that level. At 40% noise, however, Lineweaver-Burk became clearly unstable, with 20% invalid fits and larger median Vmax and Km errors than nonlinear fitting.

The third experiment moved from synthetic data to the public R Puromycin enzyme kinetics dataset. Nonlinear Michaelis-Menten fits converged for both treated and untreated conditions, all non-visual correctness checks passed, and the fitted curves showed plausible saturation behavior. The treated condition had a higher fitted Vmax than the untreated condition, and Lineweaver-Burk estimates materially disagreed with nonlinear Km estimates, reinforcing that reciprocal linearization should be treated cautiously.

---

## 2. Project Question and Study Scope

### Central Question

Given measurements of reaction velocity at several substrate concentrations, what are an enzyme's Km and Vmax, and how accurately can those parameters be recovered, especially in the presence of measurement noise?

### Study Scope

The study focused on Michaelis-Menten kinetics with one substrate and initial-rate measurements. It progressed through three evidence levels:

1. Low-noise synthetic data with known planted truth.
2. Synthetic data with increasing noise and method comparison.
3. Public enzyme kinetics data from the R Puromycin dataset.

### Model, Data, or Experimental Context

The fitted model was the Michaelis-Menten equation:

```text
v = Vmax * [S] / (Km + [S])
```

The principal fitting method was direct nonlinear least squares on the original velocity scale. Lineweaver-Burk fitting was evaluated as a comparison or diagnostic method using:

```text
1/v = (Km/Vmax)(1/[S]) + 1/Vmax
```

### What This Study Is Designed to Resolve

This study was designed to determine whether nonlinear least-squares fitting can recover Michaelis-Menten parameters under controlled conditions, how recovery degrades with noise, when Lineweaver-Burk fitting becomes unreliable, and whether the workflow transfers to public real enzyme kinetics data.

### What This Study Does Not Resolve

This study does not establish universal performance across all enzymes, assay designs, inhibitors, or noise structures. It does not model hierarchical replicate structure, substrate depletion, product inhibition, enzyme instability, or full experimental uncertainty. The public-data analysis uses a single benchmark dataset and approximate covariance-based confidence intervals.

---

## 3. Research Audit Trail

| Iteration | Hypothesis | Script or Method | Log or Evidence | Analysis | Status |
|---|---|---|---|---|---|
| 01 | [HYPOTHESIS_01.md](../hypotheses/HYPOTHESIS_01.md) | [script_01_synthetic_nonlinear_fit.py](../experiments/01_synthetic/script_01_synthetic_nonlinear_fit.py) | [script_01_synthetic_nonlinear_fit_20260713_135205.log](../results/logs/script_01_synthetic_nonlinear_fit_20260713_135205.log) | [ANALYSIS_01.md](ANALYSIS_01.md) | SUPPORTED |
| 02 | [HYPOTHESIS_02.md](../hypotheses/HYPOTHESIS_02.md) | [script_02_noise_lineweaver_comparison.py](../experiments/01_synthetic/script_02_noise_lineweaver_comparison.py) | [script_02_noise_lineweaver_comparison_20260713_135801.log](../results/logs/script_02_noise_lineweaver_comparison_20260713_135801.log) | [ANALYSIS_02.md](ANALYSIS_02.md) | PARTIALLY SUPPORTED |
| 03 | [HYPOTHESIS_03.md](../hypotheses/HYPOTHESIS_03.md) | [script_03_puromycin_real_fit.py](../experiments/02_downloaded/script_03_puromycin_real_fit.py) | [script_03_puromycin_real_fit_20260713_141424.log](../results/logs/script_03_puromycin_real_fit_20260713_141424.log) | [ANALYSIS_03.md](ANALYSIS_03.md) | SUPPORTED |

---

## 4. Final Results Matrix

| Result Area | Best or Representative Case | Main Quantitative Outcome | Interpretation |
|---|---:|---:|---|
| Low-noise nonlinear recovery | Synthetic data, 3% relative noise | Vmax error = 2.626%; Km error = 6.424% | Nonlinear fitting recovered planted truth within the 10% credibility threshold. |
| Noise robustness | Synthetic data, 3% relative noise across 50 replicates | Nonlinear median Vmax error = 1.093%; nonlinear median Km error = 3.732% | Nonlinear fitting remained credible under low relative noise. |
| Lineweaver-Burk at low noise | Synthetic data, 3% relative noise across 50 replicates | LB median Vmax error = 2.328%; LB median Km error = 3.113% | Lineweaver-Burk was also credible under low noise. |
| Lineweaver-Burk high-noise instability | Synthetic data, 40% relative noise across 50 replicates | 20% invalid LB fits; LB median Vmax error = 36.584%; LB median Km error = 47.898% | Reciprocal linearization became unstable at high noise. |
| Public-data nonlinear fit | Puromycin treated condition | Vmax = 212.683859; Km = 0.064121; R² = 0.961261 | The treated condition fit was positive, finite, and visually consistent with saturation. |
| Public-data nonlinear fit | Puromycin untreated condition | Vmax = 160.280124; Km = 0.047708; R² = 0.935572 | The untreated condition fit was positive, finite, and visually consistent with saturation. |
| Public-data condition effect | Puromycin treated versus untreated | Treated/untreated Vmax ratio = 1.326951 | The treated condition showed a higher apparent maximum rate. |
| Public-data LB diagnostic | Puromycin data | LB Km differed from nonlinear Km by 24.508% treated and 35.363% untreated | Lineweaver-Burk materially changed Km estimates and should not be treated as the primary estimate. |

---

## 5. Iteration-Level Findings

### Iteration 01 — Low-Noise Synthetic Positive Control

#### Goal

Test whether direct nonlinear least-squares fitting can recover known Michaelis-Menten parameters from low-noise synthetic velocity-versus-substrate data.

#### Method

Synthetic data were generated from Vmax = 100 and Km = 5 over substrate concentrations from 0.5 to 50 with 3% relative Gaussian noise and fixed random seed 1024. The Michaelis-Menten equation was fit directly by nonlinear least squares.

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Vmax relative error | ≤ 10% | 2.626% | Pass |
| Km relative error | ≤ 10% | 6.424% | Pass |
| R² on noisy observations | High | 0.998404 | Consistent with good fit |
| Parameter physical validity | Vmax > 0 and Km > 0 | Both positive | Pass |

#### Interpretation

The first iteration supported nonlinear least-squares fitting as a valid baseline method under low-noise synthetic conditions. Because truth was known, the decisive metric was recovery error against the planted Vmax and Km, not R² alone.

---

### Iteration 02 — Noise Sweep and Lineweaver-Burk Comparison

#### Goal

Determine how increasing measurement noise affects Km and Vmax recovery for nonlinear fitting versus Lineweaver-Burk fitting.

#### Method

Synthetic datasets were generated from Vmax = 100 and Km = 5 at noise levels of 0%, 3%, 10%, 20%, and 40%, with 50 replicates per noise level and fixed base seed 2048. Each dataset was fit with direct nonlinear least squares and with Lineweaver-Burk linear regression. Median recovery errors were computed against the planted truth.

#### Key Findings

| Noise | Method | Median Vmax Error | Median Km Error | Invalid Fits | Credible |
|---:|---|---:|---:|---:|---|
| 0% | Nonlinear | 0.000% | 0.000% | 0% | Yes |
| 0% | Lineweaver-Burk | 0.000% | 0.000% | 0% | Yes |
| 3% | Nonlinear | 1.093% | 3.732% | 0% | Yes |
| 3% | Lineweaver-Burk | 2.328% | 3.113% | 0% | Yes |
| 10% | Nonlinear | 5.000% | 12.666% | 0% | No |
| 10% | Lineweaver-Burk | 7.880% | 8.856% | 0% | Yes |
| 20% | Nonlinear | 11.064% | 25.296% | 0% | No |
| 20% | Lineweaver-Burk | 16.635% | 23.219% | 0% | No |
| 40% | Nonlinear | 21.212% | 33.566% | 0% | No |
| 40% | Lineweaver-Burk | 36.584% | 47.898% | 20% | No |

#### Interpretation

Iteration 02 partially supported the broader concern about Lineweaver-Burk instability but did not support the strict hypothesis that Lineweaver-Burk would fail earlier than nonlinear fitting under the selected relative-noise model. Both methods were credible at 0% and 3% noise. At 10% noise, nonlinear Km median error exceeded the 10% threshold while Lineweaver-Burk remained within threshold. At 40% noise, Lineweaver-Burk became clearly unstable, producing invalid fits and larger parameter errors than nonlinear fitting.

---

### Iteration 03 — Public Puromycin Dataset Fit

#### Goal

Test whether the parameter-estimation workflow transfers from synthetic data to a public enzyme kinetics dataset and produces correct, interpretable outputs without assuming planted truth.

#### Method

The R Puromycin dataset was cached as [puromycin_rates.csv](../data/downloaded/puromycin_rates.csv). Data were validated for schema, positivity, condition labels, and sample counts. Nonlinear Michaelis-Menten curves were fit separately for treated and untreated conditions. Approximate standard errors and confidence intervals were computed from the covariance matrix. Lineweaver-Burk fits were computed as diagnostic comparators.

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Data validation | Pass | Pass | Pass |
| Treated nonlinear fit | Positive finite Vmax and Km | Vmax = 212.683859; Km = 0.064121 | Pass |
| Untreated nonlinear fit | Positive finite Vmax and Km | Vmax = 160.280124; Km = 0.047708 | Pass |
| Treated Vmax 95% CI | Finite | [197.204618, 228.163100] | Pass |
| Untreated Vmax 95% CI | Finite | [145.620777, 174.939470] | Pass |
| Treated / untreated Vmax ratio | Interpretable condition difference | 1.326951 | Pass |
| LB versus nonlinear Km agreement | Diagnostic only | LB differed by 24.508% treated and 35.363% untreated | Material disagreement |

#### Interpretation

Iteration 03 supported the workflow on public downloaded data. Both nonlinear fits converged, all fitted parameters and uncertainty estimates were finite, and the saved curve plot showed plausible saturation-shaped fits. The treated condition had a higher fitted Vmax than the untreated condition. Lineweaver-Burk materially disagreed with nonlinear Km estimates, especially for the untreated condition, supporting its use as a diagnostic method rather than the primary parameter estimate.

---

## 6. Cross-Iteration Comparison

| Metric or Decision Point | Iteration 01 | Iteration 02 | Iteration 03 | Current Interpretation |
|---|---:|---:|---:|---|
| Data type | Synthetic, low-noise | Synthetic, noise sweep | Public downloaded enzyme kinetics data | Evidence progressed from controlled truth recovery to public-data validation. |
| Truth available | Yes | Yes | No | Synthetic iterations used recovery error; public-data iteration used validation and diagnostics. |
| Primary method | Nonlinear least squares | Nonlinear least squares and Lineweaver-Burk | Nonlinear least squares with LB diagnostic | Nonlinear fitting remains the preferred primary method. |
| Best nonlinear Vmax error | 2.626% | 0.000% at 0% noise; 1.093% median at 3% noise | Not applicable | Synthetic truth recovery supports nonlinear fitting under low noise. |
| Best nonlinear Km error | 6.424% | 0.000% at 0% noise; 3.732% median at 3% noise | Not applicable | Km recovery is credible under low noise but more sensitive to noise. |
| Lineweaver-Burk behavior | Not tested | Credible at low noise; unstable at 40% noise | Material Km disagreement with nonlinear fit | LB is acceptable in clean cases but can materially distort estimates. |
| Fit validation standard | Recovery error against truth | Median recovery error against truth | Data validation, finite parameters, confidence intervals, plots, residuals | Validation criteria correctly shifted with data type. |

---

## 7. Key Scientific Conclusions

1. Direct nonlinear least-squares fitting is a credible baseline for Michaelis-Menten parameter estimation when substrate coverage is adequate and noise is low.
2. Km is more noise-sensitive than Vmax in the tested synthetic setup; nonlinear Km median error crossed the 10% threshold at 10% relative noise.
3. Lineweaver-Burk fitting is not uniformly poor under all conditions, but it becomes unstable at high noise and can materially disagree with nonlinear fitting on public real data.
4. Public enzyme kinetics data can be fit with the same nonlinear workflow when correctness is assessed through validation, finite parameter estimates, uncertainty estimates, residual diagnostics, and fitted-curve inspection rather than planted-truth recovery.
5. The strongest public-data finding is that the Puromycin treated condition has a higher apparent Vmax than the untreated condition.

---

## 8. Human Intellectual Contributions

| Iteration or Decision Point | Human Contribution | Why It Mattered |
|---|---|---|
| Initial project framing | Defined the central enzyme kinetics question and requested the SMAIRT workflow. | Established the scientific question, audit-trail structure, and evidence progression. |
| Iteration 01 design | Required fixed random seed, known planted truth, and recovery error against Km and Vmax rather than relying on R². | Ensured the synthetic positive control tested the actual parameter-recovery question. |
| Iteration 02 direction | Requested the second iteration to raise noise and compare nonlinear fitting with Lineweaver-Burk recovery. | Moved the project from baseline validation to method comparison under stress. |
| Iteration 03 pivot | Selected public Puromycin data for real/downloaded-data validation. | Advanced the workflow from synthetic data to public enzyme kinetics measurements. |
| Final synthesis requirement | Requested a project-level final analysis using the analysis template. | Converted per-iteration findings into an ordered research synthesis. |

---

## 9. Reproducibility Manifest

| Artifact | Purpose | Path |
|---|---|---|
| Initial question | Research question and domain framing | [background/01_initial_question.md](../background/01_initial_question.md) |
| Code conventions | Script, logging, and audit-trail requirements | [prompts/CODE_CONVENTIONS.md](../prompts/CODE_CONVENTIONS.md) |
| Shared logging utility | Dual console and log-file output | [scripts/shared/logging.py](../scripts/shared/logging.py) |
| Iteration 01 hypothesis | Low-noise synthetic recovery hypothesis | [hypotheses/HYPOTHESIS_01.md](../hypotheses/HYPOTHESIS_01.md) |
| Iteration 01 script | Synthetic nonlinear positive control | [experiments/01_synthetic/script_01_synthetic_nonlinear_fit.py](../experiments/01_synthetic/script_01_synthetic_nonlinear_fit.py) |
| Iteration 01 log | Raw output for iteration 01 | [results/logs/script_01_synthetic_nonlinear_fit_20260713_135205.log](../results/logs/script_01_synthetic_nonlinear_fit_20260713_135205.log) |
| Iteration 01 figure | Fitted curve over low-noise synthetic data | [results/figures/script_01_synthetic_nonlinear_fit_fit_curve.png](../results/figures/script_01_synthetic_nonlinear_fit_fit_curve.png) |
| Iteration 01 analysis | Interpretation of low-noise recovery | [analysis/ANALYSIS_01.md](ANALYSIS_01.md) |
| Iteration 02 hypothesis | Noise and Lineweaver-Burk comparison hypothesis | [hypotheses/HYPOTHESIS_02.md](../hypotheses/HYPOTHESIS_02.md) |
| Iteration 02 script | Noise sweep and method comparison | [experiments/01_synthetic/script_02_noise_lineweaver_comparison.py](../experiments/01_synthetic/script_02_noise_lineweaver_comparison.py) |
| Iteration 02 log | Raw output for iteration 02 | [results/logs/script_02_noise_lineweaver_comparison_20260713_135801.log](../results/logs/script_02_noise_lineweaver_comparison_20260713_135801.log) |
| Iteration 02 summary data | Method comparison summary | [results/script_02_noise_lineweaver_comparison_summary.csv](../results/script_02_noise_lineweaver_comparison_summary.csv) |
| Iteration 02 detailed data | Replicate-level method comparison results | [results/script_02_noise_lineweaver_comparison_detailed_results.csv](../results/script_02_noise_lineweaver_comparison_detailed_results.csv) |
| Iteration 02 error figure | Median error versus noise plot | [results/figures/script_02_noise_lineweaver_comparison_median_errors.png](../results/figures/script_02_noise_lineweaver_comparison_median_errors.png) |
| Iteration 02 analysis | Interpretation of noise sweep | [analysis/ANALYSIS_02.md](ANALYSIS_02.md) |
| Iteration 03 hypothesis | Public Puromycin dataset hypothesis | [hypotheses/HYPOTHESIS_03.md](../hypotheses/HYPOTHESIS_03.md) |
| Puromycin cached data | Public downloaded enzyme kinetics dataset | [data/downloaded/puromycin_rates.csv](../data/downloaded/puromycin_rates.csv) |
| Iteration 03 script | Public-data nonlinear fitting and diagnostics | [experiments/02_downloaded/script_03_puromycin_real_fit.py](../experiments/02_downloaded/script_03_puromycin_real_fit.py) |
| Iteration 03 log | Raw output for iteration 03 | [results/logs/script_03_puromycin_real_fit_20260713_141424.log](../results/logs/script_03_puromycin_real_fit_20260713_141424.log) |
| Iteration 03 fit summary | Condition-level fit summary | [results/script_03_puromycin_real_fit_fit_summary.csv](../results/script_03_puromycin_real_fit_fit_summary.csv) |
| Iteration 03 fit figure | Public-data fitted curves | [results/figures/script_03_puromycin_real_fit_fit_curves.png](../results/figures/script_03_puromycin_real_fit_fit_curves.png) |
| Iteration 03 residual figure | Public-data residual diagnostics | [results/figures/script_03_puromycin_real_fit_residuals.png](../results/figures/script_03_puromycin_real_fit_residuals.png) |
| Iteration 03 analysis | Interpretation of public-data fitting | [analysis/ANALYSIS_03.md](ANALYSIS_03.md) |

---

## 10. Limitations and Caveats

1. The synthetic noise model in iteration 02 used relative Gaussian noise proportional to clean velocity. A constant-variance additive noise model may produce different Lineweaver-Burk behavior.
2. The 10% credibility threshold is useful and explicit, but it is a study criterion rather than a universal biochemical standard.
3. The synthetic experiments use the same model form for data generation and fitting, so they test estimator behavior under controlled assumptions rather than assay realism.
4. The Puromycin dataset is small, with 23 total observations across two conditions.
5. The public-data confidence intervals are approximate and based on the nonlinear least-squares covariance matrix.
6. The public-data analysis does not model replicate-level random effects or formal condition-level hypothesis tests.
7. R² is reported as secondary context only; parameter recovery error, validation checks, confidence intervals, and residual diagnostics are more relevant to the study question.

---

## 11. Recommended Next Steps

1. Run an additive constant-variance noise experiment to test whether the expected Lineweaver-Burk reciprocal-transform bias appears more strongly under a noise model where low-velocity points are disproportionately affected after reciprocal transformation.
2. Add bootstrap confidence intervals for the Puromycin nonlinear fits to assess parameter uncertainty without relying only on covariance approximations.
3. Fit condition-comparison models for Puromycin, including shared-Km and separate-Km alternatives, to test whether the Vmax difference remains robust under constrained model structures.
4. Generate synthetic competitive and noncompetitive inhibition datasets to confirm expected apparent shifts in Km and Vmax.
5. Apply the workflow to additional public enzyme kinetics datasets to test generality beyond Puromycin.

---

## 12. Final Assessment

### Primary Findings

- Nonlinear Michaelis-Menten fitting recovered known Km and Vmax from low-noise synthetic data within the predeclared 10% recovery-error threshold.
- Both nonlinear and Lineweaver-Burk methods performed well under clean or low-noise synthetic conditions, but Lineweaver-Burk became unstable under high noise.
- The public Puromycin dataset produced positive, finite nonlinear parameter estimates for both treated and untreated conditions, with treated cells showing a higher apparent Vmax.
- Lineweaver-Burk materially changed Km estimates on the public dataset, supporting the decision to treat it as a diagnostic comparator rather than the primary fitting method.

### Research Significance

The study establishes a complete, reproducible parameter-estimation workflow for Michaelis-Menten kinetics. It begins with truth-known synthetic controls, stress-tests method behavior under increasing noise, and then transfers to public enzyme kinetics data with validation criteria appropriate for measurements without planted truth.

### Methodological Assessment

The workflow is scientifically coherent and auditable. Each iteration has a hypothesis, script, log, outputs, and analysis. The key methodological distinction is correctly maintained: synthetic data are evaluated by recovery error against planted truth, while public data are evaluated by validation, convergence, finite uncertainty, diagnostic plots, and biologically interpretable parameter estimates. Direct nonlinear least-squares fitting is supported as the primary method for this project; Lineweaver-Burk remains useful as a diagnostic but is not reliable enough to serve as the main estimator under noisy or real-data conditions.
