# Hypothesis 01 — Single Scenario Outbreak Dynamics and Conservation

## Status: SUPPORTED

## Background

We are starting the SIRD epidemic model investigation. Before we sweep parameters or fit real data, we need to confirm that our numerical solver is working correctly, respects population conservation, and matches basic theoretical expectations for an epidemic with $R_0 > 1$.

This is Phase 1 (synthetic data) of the SMAIRT data progression.

## Hypothesis Statement

**Prediction**: 
For a population of $N = 1000$ with initial infected $I_0 = 1$, and parameters $\beta = 0.3$, $\gamma = 0.1$, and $\mu = 0.01$:
1. The basic reproduction number $R_0 = \frac{\beta}{\gamma + \mu} = \frac{0.3}{0.11} \approx 2.73$ is greater than 1, so the infected population $I(t)$ will exhibit an epidemic peak ($I_{peak} > I_0$ at some time $t_{peak} > 0$) before eventually fading to zero.
2. The total population $S(t) + I(t) + R(t) + D(t) = N$ will be conserved to within a numerical tolerance of $10^{-6}$ at all integration time steps.
3. In the limit $t \rightarrow \infty$, the epidemic will burn out with a non-zero portion of the population remaining susceptible ($S(\infty) > 0$), and the final ratio of deceased to recovered individuals will match the ratio of their rate parameters: $\frac{D(\infty)}{R(\infty)} = \frac{\mu}{\gamma} = 0.10$.

**Rationale**: 
1. Since $R_0 \approx 2.73 > 1$, the initial growth rate of infected individuals is positive: $\frac{dI}{dt}|_{t=0} \approx \beta I_0 - (\gamma + \mu)I_0 = 0.3 - 0.11 = 0.19 > 0$. As susceptibles are depleted, the effective reproduction number $R_t = R_0 \frac{S(t)}{N}$ will drop below 1, causing the outbreak to peak and then decay.
2. The sum of the derivatives is $\frac{dS}{dt} + \frac{dI}{dt} + \frac{dR}{dt} + \frac{dD}{dt} = 0$, meaning the total population must remain exactly constant.
3. The recovered and deceased compartments both grow proportionally to $I(t)$ with rates $\gamma$ and $\mu$ respectively. Since $\frac{dD/dt}{dR/dt} = \frac{\mu I}{\gamma I} = \frac{\mu}{\gamma}$, their cumulative ratio at any time (starting from $R_0 = 0, D_0 = 0$) must be exactly $\frac{\mu}{\gamma}$.

**Success criteria**: 
- Maximum numerical deviation of $|S(t) + I(t) + R(t) + D(t) - N| < 10^{-6}$ across all $t \in [0, 160]$.
- $I_{peak} > 1.0$ occurring at some $t_{peak} > 0$.
- Under long-term limit (160 days), $I(160) \approx 0$, $S(160) > 0$, and $|\frac{D(160)}{R(160)} - 0.1| < 10^{-4}$.

## Experimental Design

- **Script**: `sird_epidemic_model/experiments/01_synthetic/script_01_single_scenario.py`
- **Phase**: synthetic
- **Track**: Track A (Initial single-scenario validation)
- **Data**: Synthetic simulation starting with $S_0 = 999, I_0 = 1, R_0 = 0, D_0 = 0$, $N = 1000$.
- **Controls**: None (baseline validation).
- **Key metrics**:
  - Max population conservation error: $\max_t |S(t) + I(t) + R(t) + D(t) - N|$
  - Peak infected count $I_{peak}$ and time of peak $t_{peak}$
  - Final values $S(t_{final})$, $I(t_{final})$, $R(t_{final})$, $D(t_{final})$
  - Final ratio error: $|\frac{D(t_{final})}{R(t_{final})} - 0.1|$

## Dependencies

- Pure Python with `numpy`, `scipy.integrate.solve_ivp`, and `matplotlib`.
- Reusable `TeeLogger` and `setup_logging` from `sird_epidemic_model/scripts/shared/logging.py`.

## Results

The hypothesis was supported in the first run of `sird_epidemic_model/experiments/01_synthetic/script_01_single_scenario.py`.

Key observations from `sird_epidemic_model/results/logs/script_01_single_scenario_20260713_120806.log`:

- `R0 = beta / (gamma + mu) = 2.727273`, above the epidemic growth threshold.
- Maximum population conservation error was `7.958078640513e-13`, far below the `1e-6` tolerance.
- Infected count rose from `1` to a peak of `265.618355` on day `39.00`, then declined to `0.020268` by day `160`.
- Final compartments were `S = 81.626615`, `I = 0.020268`, `R = 834.866470`, and `D = 83.486647`.
- Observed `D/R = 0.100000`, matching `mu/gamma = 0.100000`.

See `sird_epidemic_model/analysis/ANALYSIS_01.md` for full interpretation.

## Notes

- Time interval: $t = 0$ to $160$ days with dense evaluation steps (e.g., $1$ day resolution) to capture the peak accurately.
