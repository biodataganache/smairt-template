# Analysis 02 — Beta Sweep and the R0 Growth Threshold

## Executive Summary

The beta sweep confirmed the expected SIRD threshold behavior. With `gamma = 0.1` and `mu = 0.01`, the ideal threshold is `beta = gamma + mu = 0.11`, corresponding to `R0 = 1`. Because the simulation starts with `S0 = 999` rather than exactly `N = 1000`, the finite-seed initial-growth threshold is slightly higher: `R0 > 1.001001`. The observed results matched this: beta values through `0.11` faded immediately, while beta values from `0.12` upward grew above the seed, peaked, and then declined.

## Experiment Details

- **Script**: `sird_epidemic_model/experiments/01_synthetic/script_02_beta_sweep.py`
- **Hypothesis**: `sird_epidemic_model/hypotheses/HYPOTHESIS_02.md`
- **Log**: `sird_epidemic_model/results/logs/script_02_beta_sweep_20260713_121625.log`
- **Figures**:
  - `sird_epidemic_model/results/figures/script_02_beta_sweep_infected_curves.png`
  - `sird_epidemic_model/results/figures/script_02_beta_sweep_peak_metrics_vs_r0.png`
- **Track**: A — initial solver validation and parameter sweep
- **Phase**: synthetic

## Key Results

| Metric | Expected | Observed | Status |
|--------|----------|----------|--------|
| Conservation across all beta values | Max error `< 1e-6` | `2.274e-13` to `9.095e-13` | ✓ |
| Non-negativity across all beta values | Minimum compartment `>= -1e-9` | `0.000e+00` minimum reported | ✓ |
| Below-threshold behavior | `R0 < 1` should fade immediately | beta `0.03` through `0.11` did not grow above seed | ✓ |
| Above-threshold behavior | `R0 > 1` should grow above seed | beta `0.12` through `0.60` grew above seed | ✓ |
| Peak infected trend | Higher beta should increase peak burden | peak grew from `4.1754` at `R0=1.0909` to `505.8340` at `R0=5.4545` | ✓ |
| Peak timing trend | Higher beta should generally shift peak earlier | peak shifted from day `200.00` at `R0=1.0909` to day `17.50` at `R0=5.4545` | ✓ |

## Beta Sweep Table

| beta | R0 | Predicted Growth | Observed Growth | Peak I | Peak Day | Final R % | Final D % |
|------|----|------------------|-----------------|--------|----------|-----------|-----------|
| `0.030` | `0.2727` | False | False | `1.0000` | `0.00` | `0.1249%` | `0.0125%` |
| `0.060` | `0.5455` | False | False | `1.0000` | `0.00` | `0.1996%` | `0.0200%` |
| `0.090` | `0.8182` | False | False | `1.0000` | `0.00` | `0.4846%` | `0.0485%` |
| `0.100` | `0.9091` | False | False | `1.0000` | `0.00` | `0.8379%` | `0.0838%` |
| `0.110` | `1.0000` | False | False | `1.0000` | `0.00` | `1.8349%` | `0.1835%` |
| `0.120` | `1.0909` | True | True | `4.1754` | `200.00` | `4.9939%` | `0.4994%` |
| `0.160` | `1.4545` | True | True | `55.5847` | `111.00` | `48.7867%` | `4.8787%` |
| `0.200` | `1.8182` | True | True | `121.7359` | `72.00` | `67.2083%` | `6.7208%` |
| `0.300` | `2.7273` | True | True | `265.8146` | `39.50` | `83.4889%` | `8.3489%` |
| `0.450` | `4.0909` | True | True | `411.4196` | `24.00` | `89.2743%` | `8.9274%` |
| `0.600` | `5.4545` | True | True | `505.8340` | `17.50` | `90.5113%` | `9.0511%` |

## Hypothesis Assessment

### SUPPORTED

The beta sweep supports the hypothesis. The ideal theoretical threshold `R0 = 1` was correctly located at `beta = 0.11`, and the simulation correctly reported the finite-seed correction caused by starting with `S0/N = 0.999`. The observed growth/fade classification matched the finite-seed threshold for every beta value tested.

### Where It Works (Boundaries)

- The validated solver remains numerically stable across a wide beta range from `0.03` to `0.60`.
- Conservation and non-negativity checks passed for every scenario.
- The threshold behavior is clear: below threshold, infections fade; above threshold, infections grow and peak.
- The infected peak grows larger and occurs earlier as beta increases, matching the expected qualitative interpretation.

### Where It Breaks Down / Limitations

- The `beta = 0.12` run is only slightly above threshold and reaches its maximum at the simulation endpoint (`200` days), so a longer time horizon would better capture its complete decline.
- The parameter sweep uses deterministic synthetic data and does not yet include observation noise, reporting delays, or fitting uncertainty.
- This sweep varies only `beta`; it does not yet test how changing `mu` alters the recovered/deceased final split.

## Comparison to Prior Work

| Comparison | Previous Best | This Result | Delta |
|-----------|---------------|-------------|-------|
| Validated SIRD solver | Single `R0 > 1` scenario | Multiple beta values across threshold | Broader validation |
| Growth/fade threshold | Not directly tested | `R0 = 1` threshold demonstrated | New evidence |
| Flatten-the-curve behavior | Suggested qualitatively | Lower beta produces smaller/later peaks | Initial support |

## Implications

This iteration shows that the SIRD implementation is not merely producing plausible curves; it is reproducing a theoretical threshold prediction. Lowering `beta` is therefore a credible synthetic representation of transmission-reducing interventions such as distancing, masking, or reduced contact rates. The simulations show the mechanism behind "flatten the curve": lower `beta` produces a smaller infected peak and shifts the peak later, reducing instantaneous burden.

## Next Steps

1. Run a `mu` sweep to quantify how the final recovered/deceased split changes when the disease death rate changes.
2. Pair the `mu` sweep with explicit comparisons of high-beta and low-beta scenarios to discuss flattening the curve.
3. After synthetic validation, prepare a real-data fitting plan for estimating `beta`, `gamma`, and `mu` from a small published outbreak time series.

## Files Generated

- `sird_epidemic_model/hypotheses/HYPOTHESIS_02.md` — Beta-sweep hypothesis.
- `sird_epidemic_model/experiments/01_synthetic/script_02_beta_sweep.py` — Beta-sweep script.
- `sird_epidemic_model/results/logs/script_02_beta_sweep_20260713_121625.log` — Raw output.
- `sird_epidemic_model/results/figures/script_02_beta_sweep_infected_curves.png` — Infected curves across beta values.
- `sird_epidemic_model/results/figures/script_02_beta_sweep_peak_metrics_vs_r0.png` — Peak size and peak timing versus R0.
- `sird_epidemic_model/analysis/ANALYSIS_02.md` — This analysis document.

## Intellectual Contribution Notes

The user directed that the second iteration explicitly sweep `beta`, locate the `R0 = 1` threshold, and demonstrate that infected peaks grow and shift with transmission rate. That direction shaped this iteration and clarified the scientific validation standard beyond visual plausibility.
