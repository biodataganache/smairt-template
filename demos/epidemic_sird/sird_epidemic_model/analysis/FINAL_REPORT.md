# Final Report — SIRD Epidemic Modeling with Synthetic Validation and COVID-19 Fitting

| Field | Details |
|---|---|
| Research Project | SIRD Epidemic Model |
| Study Scope | Build, validate, interpret, and fit a SIRD compartmental model for outbreak dynamics, first on synthetic scenarios and then on downloaded COVID-19 time-series data. |
| Methodological Approach | Hypothesis-driven computational study using the SMAIRT workflow: hypothesis, numbered script, logged output, analysis, and synthesis. |
| Generated | 2026-07-13 |
| Last Updated | 2026-07-13 |
| Report Status | FINAL |
| Primary Sources | [background/01_initial_question.md](../background/01_initial_question.md); [ANALYSIS_01.md](ANALYSIS_01.md); [ANALYSIS_02.md](ANALYSIS_02.md); [ANALYSIS_03.md](ANALYSIS_03.md); [ANALYSIS_04.md](ANALYSIS_04.md) |

---

## 1. Executive Summary

This project answered the initial question in [background/01_initial_question.md](../background/01_initial_question.md): given infection, recovery, and death rates, how does a SIRD outbreak evolve over time, what peak infected burden occurs, what final recovered-versus-deceased split results, and does outbreak growth follow the basic reproduction-number threshold? The project used a staged SMAIRT workflow: first validating the SIRD equations on synthetic data, then sweeping parameters to test theory, then fitting effective parameters to downloaded COVID-19 data.

The synthetic results strongly supported the SIRD implementation. The baseline synthetic scenario used population 1000, one infected seed, infection rate 0.3 per day, recovery rate 0.1 per day, and death rate 0.01 per day. The computed reproduction number was 2.727273, the infected population peaked at 265.618355 on day 39.00 in the first run, and the population-conservation error was only 7.958078640513e-13. Subsequent sweeps confirmed that the outbreak faded below the reproduction-number threshold and grew above it, with peak infected burden increasing and shifting earlier as transmission increased.

The final-size and flatten-the-curve experiments clarified the interpretation of model parameters. Increasing the death rate shifted the final removed population toward deceased outcomes, and the final deceased-to-recovered ratio matched the theoretical death-rate-to-recovery-rate ratio in every tested scenario. Lowering transmission flattened the curve: in the comparison at death rate 0.01 per day, infection rate 0.12 peaked at 4.4900 infected on day 249.50, while infection rate 0.30 peaked at 265.8146 infected on day 39.50.

The downloaded-data iteration fit the SIRD model to Italy’s early COVID-19 reported active, recovered, and deceased time series from the Johns Hopkins University CSSE repository. This produced a point estimate of infection rate 0.23081955 per day, recovery rate 0.05206253 per day, death rate 0.03663978 per day, and reproduction number 2.60218185. Bootstrap uncertainty was substantial, with a reproduction-number interval from 1.74888496 to 2.28267311 and median 2.00616651. The real-data hypothesis was therefore only partially supported: the fitting machinery worked and estimated a reproduction number above one, but the fit error and uncertainty exposed serious model mismatch and reporting-data limitations.

---

## 2. Project Question and Study Scope

### Central Question

Given infection, recovery, and death rates, how does an outbreak described by the SIRD model evolve over time; what is the peak number simultaneously infected; when does it occur; what fraction of the population ultimately recovers versus dies; and does the epidemic grow or fade as predicted by the basic reproduction number?

### Study Scope

The study covers a closed-population SIRD model with susceptible, infected, recovered, and deceased compartments. It begins with deterministic synthetic simulations using known parameters, then moves to a downloaded public COVID-19 time series for an illustrative real-data parameter fit.

### Model, Data, or Experimental Context

The SIRD equations used throughout the project were:

- dS/dt equals negative transmission flow.
- dI/dt equals transmission flow minus recovery and death flows.
- dR/dt equals recovery flow.
- dD/dt equals death flow.

The model assumes a fixed population, homogeneous mixing, fixed rates, no births, no reinfection, no latent period, and no time-varying interventions. Synthetic experiments used CPU-only Python with NumPy, SciPy, and Matplotlib. The downloaded-data experiment used JHU CSSE COVID-19 global time-series CSV files cached under [covid19_jhu](../data/downloaded/covid19_jhu).

### What This Study Is Designed to Resolve

This study was designed to determine whether the SIRD implementation is numerically credible, whether it reproduces the reproduction-number threshold, how transmission and death rates shape peak burden and final outcomes, and whether the validated machinery can be applied to a small published outbreak time series while reporting uncertainty and limitations honestly.

### What This Study Does Not Resolve

This study does not provide a definitive epidemiological estimate for COVID-19 in Italy. The downloaded-data fit is an effective baseline fit, not a causal or policy-grade inference. It does not resolve underreporting, reporting delays, changing interventions, heterogeneous mixing, latent infection, age structure, hospitalization burden, or time-varying parameters.

---

## 3. Research Audit Trail

| Iteration | Hypothesis | Script or Method | Log or Evidence | Analysis | Status |
|---|---|---|---|---|---|
| 01 | [HYPOTHESIS_01.md](../hypotheses/HYPOTHESIS_01.md) | [script_01_single_scenario.py](../experiments/01_synthetic/script_01_single_scenario.py) | [script_01_single_scenario_20260713_121406.log](../results/logs/script_01_single_scenario_20260713_121406.log) | [ANALYSIS_01.md](ANALYSIS_01.md) | SUPPORTED |
| 02 | [HYPOTHESIS_02.md](../hypotheses/HYPOTHESIS_02.md) | [script_02_beta_sweep.py](../experiments/01_synthetic/script_02_beta_sweep.py) | [script_02_beta_sweep_20260713_121625.log](../results/logs/script_02_beta_sweep_20260713_121625.log) | [ANALYSIS_02.md](ANALYSIS_02.md) | SUPPORTED |
| 03 | [HYPOTHESIS_03.md](../hypotheses/HYPOTHESIS_03.md) | [script_03_mu_final_size_flatten_curve.py](../experiments/01_synthetic/script_03_mu_final_size_flatten_curve.py) | [script_03_mu_final_size_flatten_curve_20260713_121957.log](../results/logs/script_03_mu_final_size_flatten_curve_20260713_121957.log) | [ANALYSIS_03.md](ANALYSIS_03.md) | SUPPORTED |
| 04 | [HYPOTHESIS_04.md](../hypotheses/HYPOTHESIS_04.md) | [script_04_fit_published_outbreak.py](../experiments/02_downloaded/script_04_fit_published_outbreak.py) | [script_04_fit_published_outbreak_20260713_125931.log](../results/logs/script_04_fit_published_outbreak_20260713_125931.log) | [ANALYSIS_04.md](ANALYSIS_04.md) | PARTIALLY SUPPORTED |

---

## 4. Final Results Matrix

| Result Area | Best or Representative Case | Main Quantitative Outcome | Interpretation |
|---|---:|---:|---|
| Solver conservation | Baseline synthetic scenario | Max conservation error 7.958078640513e-13 | Numerical implementation preserved total population. |
| Baseline outbreak peak | Infection rate 0.3, recovery rate 0.1, death rate 0.01 | Peak infected 265.618355 on day 39.00 | Reproduction number above one produced initial growth and later decline. |
| Threshold behavior | Beta sweep across threshold | Below 0.11 faded; 0.12 and above grew | Reproduction-number threshold was confirmed, with finite-seed correction. |
| Peak burden trend | Beta sweep | Peak increased from 4.1754 at reproduction number 1.0909 to 505.8340 at 5.4545 | Higher transmission produced larger, earlier peaks. |
| Final recovered/deceased split | Mu sweep | Death fraction rose from 0.0000 percent at death rate 0.000 to 30.0649 percent at 0.080 | Death rate controlled final mortality split. |
| Flatten-the-curve interpretation | Beta comparison at death rate 0.01 | Beta 0.12 peak 4.4900 on day 249.50; beta 0.30 peak 265.8146 on day 39.50 | Lower transmission reduced and delayed peak burden. |
| Downloaded COVID-19 fit | Italy 2020-02-23 to 2020-04-22 | Point estimate reproduction number 2.60218185; bootstrap interval 1.74888496 to 2.28267311 | Fitting pipeline worked, but uncertainty and model mismatch were substantial. |

---

## 5. Iteration-Level Findings

### Iteration 01 — Single-Scenario SIRD Validation

#### Goal

Validate the SIRD solver on one checkable synthetic scenario before doing parameter sweeps or real-data fitting.

#### Method

[script_01_single_scenario.py](../experiments/01_synthetic/script_01_single_scenario.py) integrated the SIRD equations using a numerical ODE solver, logged output to [results/logs](../results/logs), saved the four-curve figure, and asserted population conservation and non-negativity.

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Reproduction number | Greater than one | 2.727273 | Supported |
| Conservation error | Less than 1e-6 | 7.958078640513e-13 | Supported |
| Peak infected | Above one-person seed | 265.618355 on day 39.00 | Supported |
| Final deceased-to-recovered ratio | 0.100000 | 0.100000 | Supported |

#### Interpretation

The baseline SIRD implementation was credible. The solver preserved total population, produced plausible above-threshold epidemic dynamics, and matched the expected recovered/deceased ratio.

---

### Iteration 02 — Beta Sweep and Reproduction-Number Threshold

#### Goal

Test whether varying infection rate changes outbreak growth as predicted by the reproduction-number threshold.

#### Method

[script_02_beta_sweep.py](../experiments/01_synthetic/script_02_beta_sweep.py) swept infection-rate values from 0.03 to 0.60 while holding recovery rate 0.1 and death rate 0.01 fixed. Each scenario was validated for conservation and non-negativity.

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Ideal threshold | Reproduction number one at beta 0.11 | Reported beta 0.110000 | Supported |
| Finite-seed threshold | Slightly above one | Reported 1.001001 | Supported |
| Below-threshold behavior | Fade immediately | Beta 0.03 through 0.11 did not grow above seed | Supported |
| Above-threshold behavior | Grow and peak | Beta 0.12 through 0.60 grew above seed | Supported |
| Peak size trend | Increase with transmission | 4.1754 to 505.8340 | Supported |
| Peak timing trend | Earlier with higher transmission | Day 200.00 to day 17.50 | Supported |

#### Interpretation

The beta sweep demonstrated that the implementation reproduces the main threshold theorem of the SIRD model. Lowering transmission reduces peak burden and delays the peak, providing the first synthetic flatten-the-curve evidence.

---

### Iteration 03 — Death-Rate Sweep, Final Size, and Flattening the Curve

#### Goal

Quantify how death rate changes final recovered-versus-deceased outcomes and interpret lowering transmission as flattening the curve.

#### Method

[script_03_mu_final_size_flatten_curve.py](../experiments/01_synthetic/script_03_mu_final_size_flatten_curve.py) swept death-rate values at fixed infection and recovery rates, then compared multiple infection rates at fixed death and recovery rates.

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Conservation | Error below tolerance | 3.411e-13 to 1.364e-12 | Supported |
| Final deceased fraction | Increase with death rate | 0.0000 percent to 30.0649 percent | Supported |
| Final deceased-to-recovered ratio | Match death-rate-to-recovery-rate ratio | Matched for every tested death rate | Supported |
| Flattening by lowering transmission | Lower and later infected peak | Beta 0.12 peak 4.4900 on day 249.50; beta 0.30 peak 265.8146 on day 39.50 | Supported |

#### Interpretation

The final-size results confirmed the theoretical relationship between recovery and death rates. The flattening results supported the public-health interpretation that lowering transmission is the most direct lever for reducing simultaneous infections and hospital burden.

---

### Iteration 04 — Downloaded COVID-19 SIRD Fit

#### Goal

Fit infection, recovery, and death rates to a small downloaded public COVID-19 outbreak time series and report reproduction-number uncertainty and limitations.

#### Method

[script_04_fit_published_outbreak.py](../experiments/02_downloaded/script_04_fit_published_outbreak.py) downloaded or read cached JHU CSSE COVID-19 confirmed, recovered, and deaths time series, selected Italy’s early outbreak window, fit SIRD parameters using bounded least squares on log-transformed active/recovered/deceased counts, and estimated uncertainty using residual bootstrap.

#### Key Findings

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| Fitted parameters | Non-negative | beta 0.23081955, gamma 0.05206253, mu 0.03663978 | Supported |
| Point reproduction number | Reported | 2.60218185 | Supported |
| Bootstrap reproduction-number interval | Reported | 1.74888496 to 2.28267311 | Supported with caveats |
| Conservation | Below tolerance | 5.960464477539e-08 | Supported |
| Fit quality | Acceptable only if mismatch limited | Log-scale RMSE 1.035406 | Mixed |
| Limitations | Explicitly stated | Reporting and model caveats documented | Supported |

#### Interpretation

The downloaded-data experiment showed that the SIRD machinery can fit public outbreak data, but the result should be interpreted as an effective illustrative fit. The model estimated reproduction number above one, consistent with early outbreak growth, but substantial fit error and unstable bootstrap behavior indicated meaningful mismatch.

---

## 6. Cross-Iteration Comparison

| Metric or Decision Point | Iteration 1 | Iteration 2 | Iteration 3 | Iteration 4 | Current Interpretation |
|---|---:|---:|---:|---:|---|
| Data fidelity | Synthetic single scenario | Synthetic beta sweep | Synthetic death-rate and beta comparison | Downloaded COVID-19 data | Fidelity increased from controlled validation to noisy public data. |
| Conservation | 7.958078640513e-13 | 2.274e-13 to 9.095e-13 | 3.411e-13 to 1.364e-12 | 5.960464477539e-08 | Conservation held across all stages. |
| Non-negativity | Passed after explicit assertion | Passed | Passed | Passed | Solver and fitted trajectories remained physically plausible. |
| Reproduction number role | One above-threshold case | Threshold tested directly | Used in parameter interpretation | Estimated from data | The reproduction number remained central across all analyses. |
| Peak infected burden | 265.618355 | Increased with beta | Reduced by lowering beta | Fit to observed active cases | Synthetic peak mechanics were clear; real-data fit is approximate. |
| Final recovered/deceased split | Matched death-rate-to-recovery-rate ratio | Reported by beta scenario | Death-rate effect tested directly | Fit to reported recovered/deaths | Theoretical split holds synthetically but real data are reporting-biased. |
| Main limitation | Single scenario only | Synthetic-only sweep | Simplified intervention interpretation | Strong model and reporting mismatch | Limitations grew as data realism increased. |

---

## 7. Key Scientific Conclusions

1. The SIRD implementation is numerically valid for the tested scenarios: total population is conserved and compartments remain non-negative to numerical tolerance.
2. The reproduction-number threshold is the correct organizing principle for early SIRD outbreak behavior: below threshold, infection fades; above threshold, infection grows and peaks.
3. Transmission rate controls peak burden and timing. Lowering transmission flattens the curve by reducing simultaneous infections and delaying peak timing.
4. Death rate controls the final recovered-versus-deceased split in the closed deterministic SIRD model, with the final deceased-to-recovered ratio matching the death-rate-to-recovery-rate ratio.
5. The model can be fit to downloaded COVID-19 data, but the resulting parameters should be interpreted as effective, window-specific estimates rather than definitive epidemiological constants.
6. The real-data fit exposes model limitations: reported cases are not true compartments, rates change over time, and COVID-19 dynamics violate fixed-rate homogeneous SIRD assumptions.

---

## 8. Human Intellectual Contributions

| Iteration or Decision Point | Human Contribution | Why It Mattered |
|---|---|---|
| Initial framing | Provided the SIRD research question in [background/01_initial_question.md](../background/01_initial_question.md) | Established the model, metrics, and scientific target. |
| Iteration 1 | Required a single checkable scenario before broader work | Prevented premature parameter sweeps without solver validation. |
| Iteration 1 validation | Required conservation and non-negativity checks before trusting curves | Set a rigorous numerical credibility standard. |
| Iteration 2 | Required sweeping infection rate across the reproduction-number threshold | Turned one plausible curve into a threshold-validation experiment. |
| Iteration 3 | Required final-size death-rate analysis and flatten-the-curve interpretation | Connected model mechanics to public-health reasoning. |
| Intervention judgment | Prioritized lowering transmission because it directly reduces simultaneous burden | Made the work interpretive rather than merely computational. |
| Iteration 4 | Chose downloaded public COVID-19 data with caching/provenance | Moved the project into reproducible published-data fitting. |

---

## 9. Reproducibility Manifest

| Artifact | Purpose | Path |
|---|---|---|
| Background question | Initial scientific framing | [background/01_initial_question.md](../background/01_initial_question.md) |
| Code conventions | Script/logging/output conventions | [CODE_CONVENTIONS.md](../prompts/CODE_CONVENTIONS.md) |
| Shared logging utility | Dual console and log-file output | [logging.py](../scripts/shared/logging.py) |
| Iteration 1 hypothesis | Single-scenario validation prediction | [HYPOTHESIS_01.md](../hypotheses/HYPOTHESIS_01.md) |
| Iteration 1 script | Baseline SIRD solver and plot | [script_01_single_scenario.py](../experiments/01_synthetic/script_01_single_scenario.py) |
| Iteration 1 log | Baseline run output | [script_01_single_scenario_20260713_121406.log](../results/logs/script_01_single_scenario_20260713_121406.log) |
| Iteration 1 figure | Four SIRD curves | [script_01_single_scenario_sird_curves.png](../results/figures/script_01_single_scenario_sird_curves.png) |
| Iteration 1 analysis | Baseline interpretation | [ANALYSIS_01.md](ANALYSIS_01.md) |
| Iteration 2 hypothesis | Beta-threshold prediction | [HYPOTHESIS_02.md](../hypotheses/HYPOTHESIS_02.md) |
| Iteration 2 script | Infection-rate sweep | [script_02_beta_sweep.py](../experiments/01_synthetic/script_02_beta_sweep.py) |
| Iteration 2 log | Beta-sweep output | [script_02_beta_sweep_20260713_121625.log](../results/logs/script_02_beta_sweep_20260713_121625.log) |
| Iteration 2 figure | Infected curves across transmission rates | [script_02_beta_sweep_infected_curves.png](../results/figures/script_02_beta_sweep_infected_curves.png) |
| Iteration 2 figure | Peak metrics versus reproduction number | [script_02_beta_sweep_peak_metrics_vs_r0.png](../results/figures/script_02_beta_sweep_peak_metrics_vs_r0.png) |
| Iteration 2 analysis | Threshold interpretation | [ANALYSIS_02.md](ANALYSIS_02.md) |
| Iteration 3 hypothesis | Death-rate and flattening prediction | [HYPOTHESIS_03.md](../hypotheses/HYPOTHESIS_03.md) |
| Iteration 3 script | Death-rate sweep and beta comparison | [script_03_mu_final_size_flatten_curve.py](../experiments/01_synthetic/script_03_mu_final_size_flatten_curve.py) |
| Iteration 3 log | Mu-sweep and flattening output | [script_03_mu_final_size_flatten_curve_20260713_121957.log](../results/logs/script_03_mu_final_size_flatten_curve_20260713_121957.log) |
| Iteration 3 figure | Final size across death rates | [script_03_mu_final_size_flatten_curve_mu_final_size.png](../results/figures/script_03_mu_final_size_flatten_curve_mu_final_size.png) |
| Iteration 3 figure | Flatten-the-curve comparison | [script_03_mu_final_size_flatten_curve_flatten_curve_beta_comparison.png](../results/figures/script_03_mu_final_size_flatten_curve_flatten_curve_beta_comparison.png) |
| Iteration 3 analysis | Final-size and intervention interpretation | [ANALYSIS_03.md](ANALYSIS_03.md) |
| Iteration 4 hypothesis | Downloaded-data fitting prediction | [HYPOTHESIS_04.md](../hypotheses/HYPOTHESIS_04.md) |
| Iteration 4 script | COVID-19 data download/cache and SIRD fit | [script_04_fit_published_outbreak.py](../experiments/02_downloaded/script_04_fit_published_outbreak.py) |
| Iteration 4 data provenance | Dataset source and cache metadata | [italy_provenance.txt](../data/downloaded/covid19_jhu/italy_provenance.txt) |
| Iteration 4 log | Fitting and bootstrap output | [script_04_fit_published_outbreak_20260713_125931.log](../results/logs/script_04_fit_published_outbreak_20260713_125931.log) |
| Iteration 4 figure | Observed versus fitted curves | [script_04_fit_published_outbreak_fit.png](../results/figures/script_04_fit_published_outbreak_fit.png) |
| Iteration 4 figure | Residuals and uncertainty | [script_04_fit_published_outbreak_residuals_uncertainty.png](../results/figures/script_04_fit_published_outbreak_residuals_uncertainty.png) |
| Iteration 4 analysis | Real-data fit interpretation | [ANALYSIS_04.md](ANALYSIS_04.md) |
| Intellectual contribution log | Human decisions and scientific judgment | [intellectual_contribution.md](../prompts/intellectual_contribution.md) |

---

## 10. Limitations and Caveats

1. SIRD assumes a closed, homogeneous, well-mixed population with fixed rates.
2. SIRD has no exposed or latent compartment, which is a serious limitation for COVID-19.
3. The synthetic experiments are deterministic and do not include observation noise or stochastic outbreak extinction.
4. Final recovered/deceased split is clean in synthetic SIRD but can be distorted in real data by reporting delays and inconsistent recovery definitions.
5. The downloaded COVID-19 active/recovered/deceased counts are not direct observations of true SIRD compartments.
6. Italy’s 60-day early outbreak window likely includes changing testing policy, behavioral response, medical practice, and interventions.
7. The residual-bootstrap uncertainty in Iteration 4 should be treated as a first-pass diagnostic, not a final inferential interval.
8. The real-data reproduction-number estimate is an effective parameter for a selected window and observation model, not a universal biological constant.

---

## 11. Recommended Next Steps

1. Repeat the downloaded-data fit using shorter early windows before major interventions to test sensitivity to time-varying transmission.
2. Use multiple optimizer starting points and profile likelihood to improve uncertainty quantification.
3. Fit confirmed/deaths only and compare against active/recovered/deceased fitting, because recovered counts are often unreliable in COVID-19 data.
4. Implement a piecewise-transmission SIRD model to represent interventions and behavior changes.
5. Compare Italy with another country or region to test robustness of the fitted effective parameters.
6. Consider an SEIRD extension with a latent compartment for COVID-19.
7. Add a concise paper-style narrative in [paper/outline.md](../paper/outline.md) or [paper_draft](../paper_draft) using this final report as the evidence base.

---

## 12. Final Assessment

### Primary Findings

- The SIRD solver was validated: conservation and non-negativity held across synthetic and fitted scenarios.
- The reproduction-number threshold was demonstrated directly through the beta sweep.
- Lowering transmission flattened the curve by reducing and delaying the infected peak.
- Changing death rate shifted final outcomes between recovered and deceased exactly as expected in synthetic SIRD.
- Fitting to downloaded COVID-19 data was possible but only partially supported due to substantial model mismatch and uncertainty.

### Research Significance

This project demonstrates the full SMAIRT workflow on a compact epidemiological modeling problem: start with a clear question, validate the model mechanistically, sweep parameters to test theory, interpret public-health implications, then confront a real published dataset while preserving provenance and limitations. The result is a reproducible breadcrumb trail from idealized model behavior to cautious real-data fitting.

### Methodological Assessment

The methodology was successful for model validation and educational interpretation. The synthetic experiments provide strong internal checks and clear conclusions. The downloaded-data fit is valuable as a transparent baseline but should not be overinterpreted. The main methodological lesson is that mechanistic models are most trustworthy when every stage includes explicit invariants, parameter-threshold checks, uncertainty quantification, and honest caveats about observation mismatch.
