# Analysis 03 — Mu Sweep, Final Size, and Flatten-the-Curve Interpretation

## Executive Summary

The third synthetic experiment confirmed that `mu` controls the final recovered-vs-deceased split and that lowering `beta` flattens the infected curve. In the mu sweep at fixed `beta = 0.3` and `gamma = 0.1`, final deceased fraction increased from `0.0000%` at `mu = 0.000` to `30.0649%` at `mu = 0.080`, and the observed final `D/R` ratio matched `mu/gamma` for every tested value. In the beta comparison at fixed `mu = 0.01`, lowering `beta` sharply reduced and delayed the infected peak: `beta = 0.12` peaked at `4.4900` infected on day `249.50`, while `beta = 0.30` peaked at `265.8146` infected on day `39.50`.

## Experiment Details

- **Script**: `sird_epidemic_model/experiments/01_synthetic/script_03_mu_final_size_flatten_curve.py`
- **Hypothesis**: `sird_epidemic_model/hypotheses/HYPOTHESIS_03.md`
- **Log**: `sird_epidemic_model/results/logs/script_03_mu_final_size_flatten_curve_20260713_121957.log`
- **Figures**:
  - `sird_epidemic_model/results/figures/script_03_mu_final_size_flatten_curve_mu_final_size.png`
  - `sird_epidemic_model/results/figures/script_03_mu_final_size_flatten_curve_flatten_curve_beta_comparison.png`
- **Track**: A — initial solver validation and parameter sweeps
- **Phase**: synthetic

## Key Results

| Metric | Expected | Observed | Status |
|--------|----------|----------|--------|
| Conservation across all scenarios | Max error `< 1e-6` | `3.411e-13` to `1.364e-12` | ✓ |
| Non-negativity across all scenarios | Minimum compartment `>= -1e-9` | Passed; tiny negative values were numerical roundoff | ✓ |
| `D/R` ratio | Match `mu/gamma` | Matched for every `mu` value | ✓ |
| Death-rate final size | Higher `mu` increases final deceased fraction | `0.0000%` at `mu=0.000` to `30.0649%` at `mu=0.080` | ✓ |
| Flattening by lowering beta | Lower beta gives lower/later peak | `beta=0.12`: peak `4.4900` day `249.50`; `beta=0.30`: peak `265.8146` day `39.50` | ✓ |

## Mu Sweep Table

| mu | R0 | Peak I | Peak Day | Final S % | Final R % | Final D % | Expected D/R | Observed D/R |
|----|----|--------|----------|-----------|-----------|-----------|--------------|--------------|
| `0.000` | `3.0000` | `300.7678` | `38.50` | `5.9448%` | `94.0552%` | `0.0000%` | `0.000000` | `0.000000` |
| `0.005` | `2.8571` | `282.8915` | `39.00` | `7.0098%` | `88.5621%` | `4.4281%` | `0.050000` | `0.050000` |
| `0.010` | `2.7273` | `265.8146` | `39.50` | `8.1621%` | `83.4890%` | `8.3489%` | `0.100000` | `0.100000` |
| `0.020` | `2.5000` | `233.8734` | `40.50` | `10.7209%` | `74.3993%` | `14.8799%` | `0.200000` | `0.200000` |
| `0.040` | `2.1429` | `178.1285` | `43.50` | `16.7983%` | `59.4298%` | `23.7719%` | `0.400000` | `0.400000` |
| `0.060` | `1.8750` | `131.9374` | `47.00` | `24.0488%` | `47.4695%` | `28.4817%` | `0.600000` | `0.600000` |
| `0.080` | `1.6667` | `94.0947` | `51.50` | `32.3539%` | `37.5812%` | `30.0649%` | `0.800000` | `0.800000` |

## Flatten-the-Curve Comparison

| beta | R0 | Peak I | Peak Day | Final R % | Final D % |
|------|----|--------|----------|-----------|-----------|
| `0.120` | `1.0909` | `4.4900` | `249.50` | `14.4606%` | `1.4461%` |
| `0.160` | `1.4545` | `55.5847` | `111.00` | `50.2922%` | `5.0292%` |
| `0.200` | `1.8182` | `121.7359` | `72.00` | `67.2450%` | `6.7245%` |
| `0.300` | `2.7273` | `265.8146` | `39.50` | `83.4890%` | `8.3489%` |

## Hypothesis Assessment

### SUPPORTED

The hypothesis is supported. The final recovered/deceased split behaved exactly as expected from the SIRD equations: `D/R = mu/gamma`. Increasing `mu` increased the deceased fraction among removed individuals and, because it also increased the total removal rate `gamma + mu`, reduced `R0` and reduced the infected peak in this fixed-beta sweep.

The flatten-the-curve comparison also supported the hypothesis. Lower beta values produced lower peaks and later peak timing, which is the mechanistic basis for reducing hospital burden even when an outbreak still grows.

### Where It Works (Boundaries)

- The final `D/R` ratio is highly robust in this closed deterministic SIRD model.
- The synthetic simulations clearly separate final mortality effects (`mu`) from transmission effects (`beta`).
- Lowering `beta` has a direct and interpretable effect on peak burden.

### Where It Breaks Down / Limitations

- In this model, increasing `mu` both increases mortality and shortens time spent infected. Real disease severity and infectious duration may not be linked this simply.
- Deaths are modeled as a direct flow from infected to deceased, with no hospitalization compartment, reporting delay, or age/risk structure.
- Flattening the curve is represented only by lowering `beta`; real interventions may change contact patterns heterogeneously and over time.
- The model still assumes fixed rates, homogeneous mixing, closed population, no latent period, no reinfection, and no changes in behavior or policy over time.

## Cross-Iteration Answer to the Initial Question

The first three synthetic iterations now satisfy the requested "done" criteria for a working baseline SIRD model:

1. `S + I + R + D = N` stayed conserved to numerical tolerance in all tested scenarios.
2. Compartments stayed non-negative to numerical tolerance.
3. `R0 = beta / (gamma + mu)` was reported alongside model outputs and figures.
4. The outbreak grew when `R0` was above threshold and faded when below threshold.
5. Peak infected count and timing were reported.
6. Final recovered-vs-deceased split was reported and matched the theoretical `D/R = mu/gamma` relationship.
7. Parameter-sweep figures show how infected peaks grow and shift as beta changes.

## Judgment Call

The intervention I would prioritize first is lowering `beta`, because it directly reduces simultaneous infections and therefore the peak burden on hospitals. Shortening the infectious period by increasing effective removal through rapid isolation or treatment also lowers `R0`, but it depends on detection speed, compliance, and clinical capacity. In the synthetic SIRD results, lowering `beta` is the clearest direct lever for flattening the curve.

## Implications

The model is now validated enough for the next stage: fitting SIRD parameters to a small published outbreak time series. The synthetic results give checks that any real-data fit should satisfy: plausible `R0`, conservation under the mechanistic model, non-negative compartments, honest uncertainty, and explicit caveats about model mismatch.

## Next Steps

1. Identify a small published outbreak time series with at least infected/cases and ideally recovered/deceased counts.
2. Fit `beta`, `gamma`, and `mu` using nonlinear least squares or likelihood-based optimization.
3. Estimate uncertainty using bootstrap resampling, profile likelihood, or approximate covariance from the optimizer.
4. Report estimated `R0 = beta / (gamma + mu)` with uncertainty.
5. State limitations honestly: reporting delays, undercounting, changing interventions, heterogeneous mixing, and mismatch between reported cases and true infections.

## Files Generated

- `sird_epidemic_model/hypotheses/HYPOTHESIS_03.md` — Mu-sweep and flatten-the-curve hypothesis.
- `sird_epidemic_model/experiments/01_synthetic/script_03_mu_final_size_flatten_curve.py` — Mu-sweep and beta-comparison script.
- `sird_epidemic_model/results/logs/script_03_mu_final_size_flatten_curve_20260713_121957.log` — Raw output.
- `sird_epidemic_model/results/figures/script_03_mu_final_size_flatten_curve_mu_final_size.png` — Final-size plot across `mu`.
- `sird_epidemic_model/results/figures/script_03_mu_final_size_flatten_curve_flatten_curve_beta_comparison.png` — Flatten-the-curve infected-curve comparison.
- `sird_epidemic_model/analysis/ANALYSIS_03.md` — This analysis document.

## Intellectual Contribution Notes

The user specified the scientific interpretation requirements: explicitly validate conservation and non-negativity before trusting curves, sweep beta to locate the `R0 = 1` threshold, sweep `mu` to examine recovered/deceased final size, and record a judgment call about intervention priority. That direction shaped the sequence from solver validation to interpretable public-health conclusions.
