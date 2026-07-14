# Analysis 01 — Single-Scenario SIRD Validation

## Executive Summary

The first synthetic SIRD scenario successfully validated the numerical solver and the core model behavior. With `N = 1000`, `I0 = 1`, `beta = 0.3`, `gamma = 0.1`, and `mu = 0.01`, the implied basic reproduction number was `R0 = 2.727273`, so the epidemic was expected to grow, peak, and then fade. The simulation matched that expectation: infected individuals peaked at `265.618355` on day `39.00`, then declined to near zero by day `160`, while population conservation held to numerical precision.

## Experiment Details

- **Script**: `sird_epidemic_model/experiments/01_synthetic/script_01_single_scenario.py`
- **Hypothesis**: `sird_epidemic_model/hypotheses/HYPOTHESIS_01.md`
- **Log**: `sird_epidemic_model/results/logs/script_01_single_scenario_20260713_120806.log`
- **Figure**: `sird_epidemic_model/results/figures/script_01_single_scenario_sird_curves.png`
- **Track**: A — initial solver validation
- **Phase**: synthetic

## Key Results

| Metric | Expected | Observed | Status |
|--------|----------|----------|--------|
| `R0 = beta / (gamma + mu)` | Greater than 1 | `2.727273` | ✓ |
| Population conservation | Max error `< 1e-6` | `7.958078640513e-13` | ✓ |
| Infected curve behavior | Rise above seed, peak, then decline | Peak `265.618355` on day `39.00`; final infected `0.020268` | ✓ |
| Final total population | `1000` | `1000.000000` | ✓ |
| Final deceased/recovered ratio | `mu/gamma = 0.100000` | `0.100000` | ✓ |
| Figure output | Four SIRD curves saved | `results/figures/script_01_single_scenario_sird_curves.png` | ✓ |

## Parameter Summary

The script used the suggested starting parameters from `background/01_initial_question.md`:

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `N` | `1000` | Total closed population |
| `S0` | `999` | Initial susceptible population |
| `I0` | `1` | One infected seed |
| `R0 compartment` | `0` | Initial recovered population |
| `D0` | `0` | Initial deceased population |
| `beta` | `0.3 /day` | Transmission rate |
| `gamma` | `0.1 /day` | Recovery rate |
| `mu` | `0.01 /day` | Disease death rate |
| `t` | `0` to `160` days | Integration interval |

## Hypothesis Assessment

### SUPPORTED

The hypothesis is supported for this single synthetic scenario.

The key credibility checks all passed:

1. **Conservation check**: The maximum error in `S + I + R + D - N` was `7.958078640513e-13`, far below the tolerance of `1e-6`. This strongly validates the implementation of the ODE system and the numerical integration for this scenario.
2. **Epidemic shape**: Because `R0 = 2.727273 > 1`, the infected compartment was expected to grow initially. It rose from `1` infected individual to a peak of `265.618355` on day `39.00`, then declined to `0.020268` by day `160`.
3. **Final compartment behavior**: Most of the population eventually moved into recovered or deceased compartments, while a small susceptible fraction remained. Final values were:
   - `S(final) = 81.626615` (`8.1627%`)
   - `I(final) = 0.020268` (`0.0020%`)
   - `R(final) = 834.866470` (`83.4866%`)
   - `D(final) = 83.486647` (`8.3487%`)
4. **Recovered/deceased ratio**: The observed final `D/R` ratio was `0.100000`, matching `mu/gamma = 0.100000`.

### Where It Works (Boundaries)

- This implementation works for a closed, well-mixed SIRD model with fixed rates and no external data.
- It correctly preserves total population under the SIRD equations.
- It gives the expected qualitative behavior for an above-threshold outbreak where `R0 > 1`.
- It produces both immediate console output and a persistent log file through `TeeLogger`.
- It produces a visual check of all four compartments over time.

### Where It Breaks Down / Limitations

- This is only one above-threshold scenario, so it does not yet test the `R0 = 1` boundary.
- It does not yet verify that an outbreak fades monotonically when `R0 < 1`.
- It assumes a closed population, constant rates, homogeneous mixing, no births, no reinfection, no latency period, and no interventions.
- The peak day is evaluated on a one-day grid; future scripts could use finer time resolution or continuous peak optimization if needed.

## Comparison to Prior Work

This is the first executable experiment in the project, so there is no prior script baseline. It establishes the initial validated solver for future iterations.

| Comparison | Previous Best | This Result | Delta |
|-----------|---------------|-------------|-------|
| Validated SIRD solver | None | Solver passes conservation and qualitative dynamics checks | New baseline |
| SIRD figure output | None | Four-curve plot generated | New baseline |
| Log-based audit trail | None | Timestamped log written to `results/logs/` | New baseline |

## Implications

The model implementation is credible enough to use as the basis for the next SMAIRT iteration. Since conservation, peak behavior, and final compartment ratios all match theory in this single scenario, the next step should stress-test the relationship between `beta`, `R0`, and outbreak behavior.

## Next Steps

1. Create `script_02_beta_sweep.py` in `experiments/01_synthetic/` to vary `beta` while holding `gamma = 0.1` and `mu = 0.01` fixed.
2. Include values below and above the threshold `beta = gamma + mu = 0.11`, so that some runs have `R0 < 1` and others have `R0 > 1`.
3. For each beta value, measure peak infected count, day of peak, final recovered fraction, final deceased fraction, and whether infected grows above the initial seed.
4. Plot peak infected count and peak timing as functions of `R0`.

## Files Generated

- `sird_epidemic_model/hypotheses/HYPOTHESIS_01.md` — First hypothesis for the single-scenario SIRD validation.
- `sird_epidemic_model/experiments/01_synthetic/script_01_single_scenario.py` — First numbered synthetic experiment script.
- `sird_epidemic_model/results/logs/script_01_single_scenario_20260713_120806.log` — Raw run output.
- `sird_epidemic_model/results/figures/script_01_single_scenario_sird_curves.png` — Four-curve SIRD visualization.
- `sird_epidemic_model/analysis/ANALYSIS_01.md` — This analysis document.

## Cross-Iteration Update

After Iterations 2 and 3, the broader validation questions requested in the initial SMAIRT workflow have been answered:

- **Did `S + I + R + D` stay conserved?** Yes. Iteration 1 had maximum conservation error `7.958078640513e-13`, and later sweeps also stayed far below `1e-6`.
- **Did compartments stay non-negative?** Yes. Iteration 1 was rerun with an explicit all-time non-negativity assertion, and later sweeps included the same validation.
- **What was the peak infected count and timing?** In the baseline scenario, infected peaked at `265.618355` on day `39.00` in the original run and `265.8146` on day `39.50` in the finer-grid sweep.
- **Did the outbreak grow when `R0 > 1` and fade when `R0 < 1`?** Yes. Iteration 2 showed fade-out for beta values through `0.11` and growth for beta values from `0.12` upward, with the finite-seed threshold reported as `R0 > 1.001001`.
- **How did the recovered/deceased split change with death rate?** Iteration 3 showed final deceased fraction increasing from `0.0000%` at `mu=0.000` to `30.0649%` at `mu=0.080`, while observed `D/R` matched `mu/gamma` for every tested `mu`.

## Intellectual Contribution Notes

The project framing and first question were provided by the user through `background/01_initial_question.md`. The user explicitly directed the project to start with a single, checkable synthetic scenario before parameter sweeps, then required conservation and non-negativity checks before trusting curves, a beta sweep to locate the `R0 = 1` threshold, a death-rate sweep for final-size interpretation, and a judgment call about intervention priority.
