# Plan: Real-Data SIRD Parameter Fitting

## Status: COMPLETED

## Problem Statement

The synthetic SIRD model has now passed core checks: conservation, non-negativity, threshold behavior around `R0 = 1`, final recovered/deceased split, and flatten-the-curve interpretation. The next stage is to fit `beta`, `gamma`, and `mu` to a small published outbreak time series and report estimated `R0 = beta / (gamma + mu)` with uncertainty and limitations.

## Approach

Use a small public outbreak dataset with time series for cases/infected and, if available, recovered and deaths. Fit the deterministic SIRD model by optimizing parameters to match observed curves. Because real data are noisy and reporting-biased, treat this as an illustrative model-fitting exercise rather than a definitive epidemiological estimate.

Candidate fitting approaches:

1. **Least-squares fit** to observed active infected, recovered, and deceased compartments if all are available.
2. **Cases/deaths-only fit** if recovered is unavailable, with stronger caveats about identifiability.
3. **Bootstrap uncertainty** by resampling residuals or using parametric noise around fitted trajectories.
4. **Profile likelihood or optimizer covariance** as a secondary uncertainty estimate.

## Success Criteria

- A reproducible downloaded/real-data script is created under `experiments/02_downloaded/` or `experiments/03_real_data/`.
- The script reports fitted `beta`, `gamma`, `mu`, and `R0`.
- The script reports uncertainty intervals for `R0` and ideally for each fitted parameter.
- The script plots observed versus fitted curves.
- The analysis explicitly states model limitations: underreporting, reporting delays, changing interventions, heterogeneous mixing, no latent period, fixed rates, and mismatch between reported cases and true infections.

## Dependencies

- [x] Synthetic single-scenario solver validated in `experiments/01_synthetic/script_01_single_scenario.py`.
- [x] Beta sweep validated threshold behavior in `experiments/01_synthetic/script_02_beta_sweep.py`.
- [x] Mu sweep validated final recovered/deceased split in `experiments/01_synthetic/script_03_mu_final_size_flatten_curve.py`.
- [x] A small published outbreak time series with sufficient metadata: JHU CSSE COVID-19 Italy time series.
- [x] Decision on whether this belongs in `experiments/02_downloaded/` or `experiments/03_real_data/`: downloaded phase.

## Steps

1. [x] Identify a suitable small public outbreak time series.
2. [x] Create `hypotheses/HYPOTHESIS_04.md` for real-data parameter fitting.
3. [x] Create `experiments/02_downloaded/script_04_fit_published_outbreak.py`.
4. [x] Implement data loading and validation.
5. [x] Implement SIRD fitting with bounded parameters: `beta >= 0`, `gamma >= 0`, `mu >= 0`.
6. [x] Estimate uncertainty with bootstrap.
7. [x] Plot observed vs fitted trajectories and residuals.
8. [x] Write `analysis/ANALYSIS_04.md` with results, caveats, and next steps.

## Expected Outputs

- `hypotheses/HYPOTHESIS_04.md`
- `experiments/02_downloaded/script_04_fit_published_outbreak.py`
- `results/logs/script_04_fit_published_outbreak_20260713_125931.log`
- `results/figures/script_04_fit_published_outbreak_fit.png`
- `results/figures/script_04_fit_published_outbreak_residuals_uncertainty.png`
- `analysis/ANALYSIS_04.md`

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Reported cases are not true active infections | High | Fit multiple observation models and state caveats clearly |
| `gamma` and `mu` are weakly identifiable from cases alone | High | Prefer data with recovered/deaths; report uncertainty honestly |
| Interventions make fixed-rate SIRD invalid | High | Fit only an early time window or allow piecewise beta in later iterations |
| Underreporting biases `R0` | High | Treat estimates as illustrative and sensitivity-test reporting scale |
| Dataset provenance is unclear | Medium | Use only a well-documented published source |

## Notes

The real-data fit should not be framed as a final epidemiological estimate. It is the next SMAIRT fidelity step: use synthetic validation to interpret a small real-world curve while making limitations explicit.
