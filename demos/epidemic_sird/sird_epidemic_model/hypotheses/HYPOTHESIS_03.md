# Hypothesis 03 — Mu Sweep, Final Size, and Flatten-the-Curve Interpretation

## Status: SUPPORTED

## Background

The first two synthetic SIRD experiments validated the solver and showed that changing `beta` controls whether an outbreak grows or fades and how large/early the infected peak becomes. The next question is how the disease death rate `mu` changes the final recovered-vs-deceased split, and how lowering `beta` should be interpreted as flattening the curve.

## Hypothesis Statement

**Prediction**:

1. Holding `beta = 0.3` and `gamma = 0.1` fixed, increasing `mu` will increase the final deceased fraction and decrease the recovered fraction.
2. For every `mu`, the final ratio `D/R` will match `mu/gamma` to numerical tolerance, because `dD/dt / dR/dt = mu/gamma`.
3. Increasing `mu` also increases the removal rate `gamma + mu`, reducing `R0 = beta / (gamma + mu)`; therefore high enough `mu` can reduce epidemic growth even though deaths among infected individuals become more frequent.
4. Lowering `beta` while holding `gamma` and `mu` fixed will flatten the curve: lower peak infected count, later peak timing, and lower simultaneous burden.

**Rationale**:
Recovered and deceased compartments are accumulated from the infected compartment with rates `gamma` and `mu`. Their cumulative split is therefore determined by the relative removal rates. Meanwhile, `beta` controls new infections, so lowering `beta` reduces transmission and lowers the epidemic peak.

**Success criteria**:

- Every scenario has maximum conservation error `< 1e-6`.
- Every scenario has minimum compartment value `>= -1e-9`.
- The observed final `D/R` ratio matches `mu/gamma` with absolute error `< 1e-4` when recovered is nonzero.
- Increasing `mu` increases final deceased fraction across the tested range.
- Lowering `beta` from `0.3` to lower above-threshold values reduces peak infected count and delays the peak.

## Experimental Design

- **Script**: `sird_epidemic_model/experiments/01_synthetic/script_03_mu_final_size_flatten_curve.py`
- **Phase**: synthetic
- **Track**: A (initial solver validation and parameter sweeps)
- **Data**: Synthetic SIRD simulations.
- **Controls**:
  - `mu = 0.01` baseline from Iteration 1.
  - `beta = 0.3` baseline compared against lower beta scenarios.
- **Key metrics**:
  - Final recovered fraction
  - Final deceased fraction
  - Final `D/R` ratio and error relative to `mu/gamma`
  - `R0 = beta / (gamma + mu)`
  - Peak infected count and peak timing under different beta values

## Dependencies

- Builds on `sird_epidemic_model/experiments/01_synthetic/script_01_single_scenario.py` and `sird_epidemic_model/experiments/01_synthetic/script_02_beta_sweep.py`.
- Uses `numpy`, `scipy.integrate.solve_ivp`, `matplotlib`, and `scripts.shared.TeeLogger`.

## Results

The hypothesis was supported in `sird_epidemic_model/experiments/01_synthetic/script_03_mu_final_size_flatten_curve.py`.

Key observations from `sird_epidemic_model/results/logs/script_03_mu_final_size_flatten_curve_20260713_121957.log`:

- All conservation and non-negativity checks passed.
- The final deceased fraction increased monotonically across tested `mu` values, from `0.0000%` at `mu = 0.000` to `30.0649%` at `mu = 0.080`.
- Observed final `D/R` matched `mu/gamma` for every `mu` value tested.
- Lowering `beta` flattened the curve: `beta = 0.12` produced peak `I = 4.4900` on day `249.50`, whereas `beta = 0.30` produced peak `I = 265.8146` on day `39.50`.
- The intervention judgment call was to prioritize lowering `beta` first because it directly reduces simultaneous infections and hospital burden.

See `sird_epidemic_model/analysis/ANALYSIS_03.md` for full interpretation.

## Notes

This iteration connects mechanistic SIRD outputs to public-health interpretation: lowering transmission rate flattens the curve, while changing death rate changes final mortality conditional on infection dynamics.
