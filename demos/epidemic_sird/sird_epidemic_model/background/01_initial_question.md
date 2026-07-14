# 01_initial_question.md

## Brief Background

When a new infectious disease spreads, public-health teams need to answer urgent
questions: How fast will cases rise? Will hospitals be overwhelmed? How many
people will recover, and how many will die? **Compartmental models** are the
classic mathematical tool for this. They divide a population into groups
("compartments") and write **differential equations** for how people flow between
them over time.

This SMAIRT project builds the **SIRD** model, one of the foundational models in
epidemiology. It splits a fixed population into four compartments -
**S**usceptible (can still catch the disease), **I**nfected (currently sick and
contagious), **R**ecovered (immune), and **D**eceased - and tracks how the
outbreak evolves. It starts with **synthetic data we generate from known
parameters** (an infection rate, a recovery rate, and a death rate we choose), so
we can confirm the solver and the analysis are correct before interpreting any
real epidemic curve. A key quantity, the **basic reproduction number R0**, tells
us whether an outbreak grows or dies out, and the model lets us test that
prediction directly.

It is CPU-only, pure Python (numpy/scipy/matplotlib), and needs no external data.

## Question

Given infection, recovery, and death rates, how does an outbreak described by the
SIRD model evolve over time - what is the peak number simultaneously infected,
when does it occur, and what fraction of the population ultimately recovers versus
dies - and does the epidemic grow or fade as predicted by the basic reproduction
number R0?

## Hypothesis

The outbreak's behavior is governed by **R0 = beta / (gamma + mu)** (infection
rate divided by the total rate of leaving the infected compartment). When
**R0 > 1** the number of infected will first **grow** to a peak and then decline;
when **R0 < 1** it will decline monotonically from the start with no epidemic
peak. The peak infected count and the final split between recovered and deceased
will be determined by the chosen rates, and a numerical solution will match the
model's known conserved quantity (S + I + R + D stays constant) and the expected
qualitative behavior.

## Evidence / metrics

- **Conservation check:** S + I + R + D must equal the total population `N` at
  every time step (to within numerical tolerance). This validates the solver.
- **R0 prediction:** compute R0 = beta / (gamma + mu) and confirm the simulated
  epidemic grows (peak present) when R0 > 1 and fades when R0 < 1.
- **Peak infection:** the maximum of I(t) and the time it occurs, across
  different beta values.
- **Final outcome:** the fraction Recovered vs. Deceased at long time (the
  epidemic's "final size").
- **Visual check:** S, I, R, D curves over time on one plot, plus how the infected
  peak shifts as the infection rate `beta` changes.

## Domain Context

### The SIRD equations
With population `N = S + I + R + D` held constant:
- `dS/dt = -beta * S * I / N`
- `dI/dt =  beta * S * I / N - gamma * I - mu * I`
- `dR/dt =  gamma * I`
- `dD/dt =  mu * I`

Parameters:
- `beta` = infection (transmission) rate.
- `gamma` = recovery rate (1/gamma is the mean infectious period).
- `mu` = disease death rate.

### The basic reproduction number
- `R0 = beta / (gamma + mu)` = the average number of new infections caused by one
  infected person in a fully susceptible population.
- `R0 > 1` -> outbreak grows to a peak; `R0 < 1` -> outbreak fades.

### Why a numerical solver
- The SIRD system is **nonlinear** (the `S*I` term) and has **no simple
  closed-form solution**, so it must be integrated numerically (e.g. a
  Runge-Kutta method such as `scipy.integrate.solve_ivp`). The conservation law
  `S + I + R + D = N` gives a built-in correctness check on that integration.

### Fidelity ladder (SMAIRT data progression)
1. **Synthetic, single scenario (start here):** pick `N`, `beta`, `gamma`, `mu`
   and one infected seed; integrate the SIRD equations and confirm S+I+R+D is
   conserved and the curves look sensible.
2. **Synthetic, parameter sweep:** vary `beta` (hence R0) and show the infected
   peak growing/shifting, and the R0 = 1 threshold separating growth from decay.
3. **Real (optional, later):** fit `beta`, `gamma`, `mu` to a small published
   outbreak time series (e.g. an early COVID-19 or influenza curve) and report the
   estimated R0 with its uncertainty and the model's limitations.

### Caveats
- SIRD assumes a well-mixed, closed population with constant rates and no births,
  reinfection, latency, or interventions. Real epidemics violate these; stating
  those assumptions next to the numbers is part of the SMAIRT method.

## Known values (suggested starting parameters, for validation)

| Quantity | Value |
|----------|-------|
| population `N` | 1,000 |
| initial infected `I0` | 1 |
| infection rate `beta` | 0.3 /day |
| recovery rate `gamma` | 0.1 /day |
| death rate `mu` | 0.01 /day |
| implied R0 | 0.3 / (0.1 + 0.01) ≈ 2.7 (outbreak grows) |
| time interval | `t` = 0 to 160 days |
| conservation invariant | S + I + R + D = N at all times |
| random seed | fixed (reproducibility, if any noise is added) |
