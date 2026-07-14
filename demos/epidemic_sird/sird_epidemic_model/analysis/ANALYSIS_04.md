# Analysis 04 — Fit SIRD Parameters to Downloaded COVID-19 Time Series

## Executive Summary

This iteration fit the SIRD model to a downloaded public COVID-19 time series from the Johns Hopkins University CSSE repository. The script selected Italy's early outbreak window from `2020-02-23` through `2020-04-22` and fit active infected, recovered, and deceased trajectories using bounded least squares on log-transformed counts. The fitted point estimate was `beta = 0.23081955`, `gamma = 0.05206253`, `mu = 0.03663978`, giving `R0 = 2.60218185`; residual-bootstrap uncertainty was substantial, with a bootstrap `R0` interval from `1.74888496` to `2.28267311` and median `2.00616651`.

## Experiment Details

- **Script**: `sird_epidemic_model/experiments/02_downloaded/script_04_fit_published_outbreak.py`
- **Hypothesis**: `sird_epidemic_model/hypotheses/HYPOTHESIS_04.md`
- **Log**: `sird_epidemic_model/results/logs/script_04_fit_published_outbreak_20260713_125931.log`
- **Data provenance**: `sird_epidemic_model/data/downloaded/covid19_jhu/italy_provenance.txt`
- **Figures**:
  - `sird_epidemic_model/results/figures/script_04_fit_published_outbreak_fit.png`
  - `sird_epidemic_model/results/figures/script_04_fit_published_outbreak_residuals_uncertainty.png`
- **Track**: A — baseline SIRD fitting
- **Phase**: downloaded

## Data Source and Fitting Window

The script downloaded and cached these JHU CSSE global COVID-19 time series files:

- `sird_epidemic_model/data/downloaded/covid19_jhu/time_series_covid19_confirmed_global.csv`
- `sird_epidemic_model/data/downloaded/covid19_jhu/time_series_covid19_deaths_global.csv`
- `sird_epidemic_model/data/downloaded/covid19_jhu/time_series_covid19_recovered_global.csv`

Selected window:

| Field | Value |
|-------|-------|
| Country | `Italy` |
| Population used as closed SIRD `N` | `60,461,826` |
| Start date | `2020-02-23` |
| End date | `2020-04-22` |
| Window length | `60` days |
| Start confirmed | `155` |
| Start active | `150` |
| Start recovered | `2` |
| Start deaths | `3` |
| End confirmed | `187,327` |
| End active | `107,699` |
| End recovered | `54,543` |
| End deaths | `25,085` |

## Key Results

| Metric | Expected | Observed | Status |
|--------|----------|----------|--------|
| Data download/cache | JHU CSSE files available locally | Three CSVs downloaded and cached | ✓ |
| Non-negative fitted parameters | `beta`, `gamma`, `mu >= 0` | `0.23081955`, `0.05206253`, `0.03663978` | ✓ |
| Report fitted `R0` | `beta / (gamma + mu)` | `2.60218185` | ✓ |
| Bootstrap uncertainty | Interval reported | `R0` 2.5/50/97.5% = `1.74888496`, `2.00616651`, `2.28267311` | ✓ |
| Conservation | Max error below tolerance | `5.960464477539e-08` | ✓ |
| Non-negativity | Minimum compartment non-negative | `2.000000000000e+00` | ✓ |
| Fit quality | Diagnostics reported | Log-scale RMSE `1.035406` | Mixed |
| Limitations | Explicitly stated | Reporting/model caveats recorded | ✓ |

## Fitted Parameters

| Parameter | Point Estimate | Bootstrap 2.5% | Bootstrap Median | Bootstrap 97.5% |
|-----------|----------------|----------------|------------------|-----------------|
| `beta` | `0.23081955` | `0.23530088` | `0.25620280` | `0.28774245` |
| `gamma` | `0.05206253` | `0.06164448` | `0.07655121` | `0.09974708` |
| `mu` | `0.03663978` | `0.03872071` | `0.05049627` | `0.06706978` |
| `R0` | `2.60218185` | `1.74888496` | `2.00616651` | `2.28267311` |

## Hypothesis Assessment

### PARTIALLY SUPPORTED

The hypothesis is partially supported.

Supported elements:

1. The script successfully downloaded public COVID-19 data and cached them with provenance metadata.
2. The SIRD fitting procedure returned non-negative `beta`, `gamma`, and `mu` values.
3. The fitted trajectory preserved population conservation and non-negativity.
4. The script reported `R0` with bootstrap uncertainty.
5. The estimated `R0` range was above `1`, consistent with a growing early outbreak.

Cautionary elements:

1. Fit error was substantial (`log-scale RMSE = 1.035406`), indicating meaningful mismatch between deterministic SIRD curves and reported COVID-19 trajectories.
2. The fitted point estimate for `R0 = 2.60218185` fell above the bootstrap interval upper bound (`2.28267311`). This is a warning sign that the residual-bootstrap procedure and the fit landscape are unstable under model mismatch, not a clean inferential result.
3. COVID-19 reported active, recovered, and deceased counts are not direct observations of true SIRD compartments.
4. The selected 60-day Italy window likely includes changing reporting, testing, care, and intervention regimes, violating the constant-rate assumption.

## Where It Works

- The machinery for fitting `beta`, `gamma`, and `mu` works end-to-end.
- The data download/cache/provenance pattern is now available for future downloaded-data experiments.
- The model produces interpretable effective parameter estimates for a selected early outbreak window.
- The fitted trajectory still obeys SIRD conservation and non-negativity constraints.
- Bootstrap uncertainty provides a first-pass warning about parameter uncertainty and instability.

## Where It Breaks Down

- Reported confirmed cases are not equal to true active infections.
- Recovered counts in early COVID-19 datasets are especially inconsistent across countries and time.
- The model has no latent/exposed compartment, but COVID-19 has a meaningful incubation period.
- Fixed `beta`, `gamma`, and `mu` are unrealistic across a 60-day window containing behavior changes and interventions.
- Italy was not a closed, homogeneous, well-mixed population.
- Underreporting and testing availability changed rapidly during this period.
- The bootstrap interval not containing the point estimate indicates that uncertainty quantification should be improved before making strong claims.

## Interpretation

The real-data fitting iteration shows that the synthetic SIRD framework can be connected to public outbreak data, but it also demonstrates why honest limitations are essential. The estimated `R0` is plausibly above `1`, but the precise value should be interpreted as an effective model parameter for this specific window and observation model, not as a definitive epidemiological estimate for Italy.

The model is best understood here as a transparent baseline: it exposes where a simple mechanistic model captures broad growth and where it fails due to reporting artifacts, interventions, and missing biological structure.

## Comparison to Prior Work

| Comparison | Previous Best | This Result | Delta |
|-----------|---------------|-------------|-------|
| Data fidelity | Synthetic only | Downloaded public COVID-19 data | Higher realism |
| Parameter values | Chosen by configuration | Estimated from data | New capability |
| Uncertainty | Not needed for deterministic synthetic tests | Bootstrap uncertainty reported | New diagnostic |
| Model limitations | Theoretical caveats | Empirical mismatch visible in residuals | More honest assessment |

## Next Steps

1. Improve uncertainty quantification using profile likelihood or multiple starting points.
2. Test shorter early windows before major interventions to reduce fixed-rate violation.
3. Fit a model to confirmed/deaths only and treat recovered as unreliable, comparing identifiability.
4. Try a piecewise-beta SIRD model to account for intervention-driven changes in transmission.
5. Consider an SEIRD model with an exposed/latent compartment for COVID-19.
6. Compare Italy to another country or region to test robustness.

## Files Generated

- `sird_epidemic_model/hypotheses/HYPOTHESIS_04.md` — Downloaded-data fitting hypothesis.
- `sird_epidemic_model/experiments/02_downloaded/script_04_fit_published_outbreak.py` — SIRD fitting script.
- `sird_epidemic_model/data/downloaded/covid19_jhu/italy_provenance.txt` — Dataset provenance.
- `sird_epidemic_model/results/logs/script_04_fit_published_outbreak_20260713_125931.log` — Raw output.
- `sird_epidemic_model/results/figures/script_04_fit_published_outbreak_fit.png` — Observed versus fitted active/recovered/deceased curves.
- `sird_epidemic_model/results/figures/script_04_fit_published_outbreak_residuals_uncertainty.png` — Residuals and `R0` bootstrap uncertainty.
- `sird_epidemic_model/analysis/ANALYSIS_04.md` — This analysis document.

## Intellectual Contribution Notes

The user chose to proceed with a downloaded public COVID-19 time series and requested a script that fetches or reads cached data. This decision moved the project from synthetic validation into a reproducible downloaded-data phase while preserving provenance and limitations.
