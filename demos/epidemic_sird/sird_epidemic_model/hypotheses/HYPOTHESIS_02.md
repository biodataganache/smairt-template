# Hypothesis 02 — Beta Sweep and the R0 Growth Threshold

## Status: SUPPORTED

## Background

After validating the SIRD solver in `sird_epidemic_model/experiments/01_synthetic/script_01_single_scenario.py`, the next question is whether the same implementation reproduces the central theoretical prediction of the SIRD model: varying the infection rate `beta` changes `R0 = beta / (gamma + mu)`, and the `R0 = 1` threshold separates immediately fading outbreaks from outbreaks that initially grow.

This remains Phase 1 synthetic work. The goal is not yet to fit real data, but to stress-test the model across a controlled range of transmission rates.

## Hypothesis Statement

**Prediction**:
With `N = 1000`, `I0 = 1`, `gamma = 0.1`, and `mu = 0.01`, sweeping `beta` across the threshold `beta = gamma + mu = 0.11` will show:

1. For `R0 < 1`, infected counts will fade immediately, so the maximum infected count will occur at the start or remain close to the one-person seed.
2. For `R0 > 1`, infected counts will grow above the seed, peak, and then decline.
3. As `beta` increases above threshold, peak infected count will increase and peak timing will generally shift earlier.
4. All simulations will preserve `S + I + R + D = N` to numerical tolerance and keep compartments non-negative.

**Rationale**:
The initial infected growth rate is approximately determined by

`dI/dt = (beta * S/N - gamma - mu) * I`.

For a nearly fully susceptible population, this is positive when `R0 = beta / (gamma + mu) > 1`. Because `S0 = 999` rather than exactly `N = 1000`, the finite-seed effective initial growth threshold is slightly above the ideal fully susceptible threshold: `beta > (gamma + mu) * N / S0`, corresponding to `R0 > N/S0 ≈ 1.001`.

**Success criteria**:

- Every beta scenario has maximum conservation error `< 1e-6`.
- Every beta scenario has minimum compartment value `>= -1e-9`.
- Scenarios below the threshold do not grow meaningfully above the one-person seed.
- Scenarios above the threshold grow above the seed, peak, and decline.
- The script reports both the ideal threshold `R0 = 1` and the finite-seed effective threshold.
- The script saves figures showing infected curves and peak metrics versus `R0`.

## Experimental Design

- **Script**: `sird_epidemic_model/experiments/01_synthetic/script_02_beta_sweep.py`
- **Phase**: synthetic
- **Track**: A (initial solver validation and parameter sweep)
- **Data**: Synthetic SIRD simulations with fixed `N = 1000`, `I0 = 1`, `gamma = 0.1`, and `mu = 0.01`, sweeping `beta`.
- **Controls**: Below-threshold beta values act as fade-out controls; above-threshold beta values act as growth scenarios.
- **Key metrics**:
  - `R0 = beta / (gamma + mu)`
  - Maximum conservation error
  - Minimum compartment value
  - Peak infected count
  - Day of peak infection
  - Final susceptible, infected, recovered, and deceased fractions
  - Whether infected grew above the seed

## Dependencies

- Builds on the validated SIRD equations from `sird_epidemic_model/experiments/01_synthetic/script_01_single_scenario.py`.
- Uses `numpy`, `scipy.integrate.solve_ivp`, `matplotlib`, and `scripts.shared.TeeLogger`.

## Results

The hypothesis was supported in `sird_epidemic_model/experiments/01_synthetic/script_02_beta_sweep.py`.

Key observations from `sird_epidemic_model/results/logs/script_02_beta_sweep_20260713_121625.log`:

- The ideal threshold was reported as `beta = gamma + mu = 0.110000`, `R0 = 1.000000`.
- The finite-seed initial-growth threshold was reported as `beta > 0.110110`, equivalent to `R0 > 1.001001`, because `S0/N = 0.999`.
- Below-threshold beta values `0.03` through `0.11` did not grow above the one-person seed.
- Above-threshold beta values `0.12` through `0.60` grew above the seed.
- Peak infected count increased as `R0` increased above threshold, from `4.1754` at `R0 = 1.0909` to `505.8340` at `R0 = 5.4545`.
- Peak timing generally shifted earlier as `R0` increased above threshold, from day `200.00` at `R0 = 1.0909` to day `17.50` at `R0 = 5.4545`.
- All conservation checks and non-negativity checks passed.

See `sird_epidemic_model/analysis/ANALYSIS_02.md` for full interpretation.

## Notes

This experiment directly addresses the project requirement to show that the outbreak grows when `R0 > 1` and fades when `R0 < 1`, while retaining explicit conservation and non-negativity checks for every simulated scenario.
