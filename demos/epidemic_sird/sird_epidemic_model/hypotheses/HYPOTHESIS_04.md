# Hypothesis 04 — Fit SIRD Parameters to Downloaded COVID-19 Time Series

## Status: PARTIALLY SUPPORTED

## Background

The first three synthetic experiments validated the SIRD implementation under controlled conditions: conservation, non-negativity, `R0` threshold behavior, final recovered/deceased split, and flatten-the-curve interpretation. The next fidelity step is to fit `beta`, `gamma`, and `mu` to a small published outbreak time series.

For this iteration, we use downloaded public COVID-19 time series from the Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE) COVID-19 data repository, with local caching under `sird_epidemic_model/data/downloaded/`.

## Hypothesis Statement

**Prediction**:

A deterministic SIRD model fit to an early COVID-19 country-level time window can recover plausible effective parameters `beta`, `gamma`, and `mu`, and therefore an estimated `R0 = beta / (gamma + mu)`, but uncertainty and model mismatch will be substantial because reported COVID-19 data violate SIRD assumptions.

**Rationale**:

Early outbreak curves often resemble exponential growth followed by slowing, so a constant-rate SIRD model may approximate the broad trajectory over a limited window. However, reported confirmed, recovered, and death counts are affected by underreporting, reporting delays, changes in testing policy, interventions, and non-closed population assumptions. Therefore the fit should be treated as an illustrative effective-parameter fit rather than a definitive epidemiological estimate.

**Success criteria**:

- The script fetches JHU CSSE COVID-19 time series or reads cached files if they already exist.
- The script constructs active infected, recovered, and deceased trajectories from confirmed, recovered, and deaths.
- The fitting procedure returns non-negative `beta`, `gamma`, and `mu`.
- The fitted trajectory preserves SIRD conservation and non-negativity.
- The script reports `R0 = beta / (gamma + mu)` with bootstrap uncertainty.
- The script saves observed-vs-fitted plots and residual plots.
- The analysis explicitly states limitations and identifiability caveats.

## Experimental Design

- **Script**: `sird_epidemic_model/experiments/02_downloaded/script_04_fit_published_outbreak.py`
- **Phase**: downloaded
- **Track**: A (baseline SIRD fitting)
- **Data**: JHU CSSE COVID-19 global time series, cached under `sird_epidemic_model/data/downloaded/covid19_jhu/`.
- **Target series**: Italy country-level early outbreak window, starting once cumulative confirmed cases exceed a threshold and using a fixed early-window length.
- **Controls**:
  - Synthetic validation from Iterations 1–3.
  - Fit diagnostics comparing observed versus fitted active/recovered/deceased curves.
- **Key metrics**:
  - Fitted `beta`, `gamma`, `mu`
  - Estimated `R0 = beta / (gamma + mu)`
  - Bootstrap confidence interval for `R0`
  - Fit RMSE on log-transformed active/recovered/deceased counts
  - Conservation and non-negativity checks on fitted trajectory

## Dependencies

- Builds on the validated SIRD equations from synthetic scripts.
- Uses Python standard library `urllib` and `csv` for data download/loading.
- Uses `numpy`, `scipy.integrate.solve_ivp`, `scipy.optimize.least_squares`, `matplotlib`, and `scripts.shared.TeeLogger`.

## Results

The hypothesis was partially supported in `sird_epidemic_model/experiments/02_downloaded/script_04_fit_published_outbreak.py`.

Key observations from `sird_epidemic_model/results/logs/script_04_fit_published_outbreak_20260713_125931.log`:

- JHU CSSE COVID-19 global time series were downloaded and cached under `sird_epidemic_model/data/downloaded/covid19_jhu/`.
- Italy was fit over a 60-day early outbreak window from `2020-02-23` to `2020-04-22`.
- The optimizer returned non-negative parameters: `beta = 0.23081955`, `gamma = 0.05206253`, `mu = 0.03663978` per day.
- The point estimate was `R0 = 2.60218185`.
- Residual-bootstrap `R0` interval was `1.74888496` to `2.28267311`, with median `2.00616651`.
- Conservation and non-negativity checks passed on the fitted trajectory.
- Fit error was substantial (`log-scale RMSE = 1.035406`), and the point estimate fell above the bootstrap interval, reinforcing the caveat that this is an effective illustrative fit with model mismatch rather than a definitive epidemiological estimate.

See `sird_epidemic_model/analysis/ANALYSIS_04.md` for full interpretation.

## Notes

This iteration should be interpreted cautiously. COVID-19 reported active/recovered/deceased curves are not direct observations of true SIRD compartments. The purpose is to test whether the already-validated SIRD machinery can be fit to real published data while reporting uncertainty and limitations honestly.
