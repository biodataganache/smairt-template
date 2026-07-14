# 01_initial_question.md

## Brief Background

Most enzymes follow **Michaelis-Menten kinetics**: as you raise the substrate
concentration, the reaction rate rises steeply at first, then flattens toward a
maximum velocity as the enzyme saturates. Two numbers summarize an enzyme:
**Vmax** (the maximum rate) and **Km** (the substrate concentration at which the
rate is half of Vmax). Estimating Km and Vmax from measured data is one of the
most common tasks in biochemistry.

This SMAIRT project estimates Km and Vmax from data, but starts with **synthetic
data we generate from known Km and Vmax values plus realistic measurement
noise**. Because we know the true parameters, we can check whether our fitting
method recovers them before trusting it on real assay data. It also lets us
compare a classic shortcut (the linearized **Lineweaver-Burk** plot) against a
proper **nonlinear least-squares** fit and see why the textbook shortcut is
biased.

It is CPU-only, pure Python (numpy/scipy/matplotlib), and needs no external data.

## Question

Given measurements of reaction velocity (v) at several substrate concentrations
([S]), what are the enzyme's **Km and Vmax**, and how accurately can we recover
them, especially in the presence of measurement noise?

## Hypothesis

A **nonlinear least-squares fit** of the Michaelis-Menten equation directly to
(v, [S]) data will recover the true Km and Vmax more accurately than the
**Lineweaver-Burk** double-reciprocal linearization, because taking reciprocals
inflates the influence of low-substrate, high-noise points. On clean synthetic
data both should agree; as noise increases, the linearized method should become
visibly biased while the nonlinear fit stays close to truth.

## Evidence / metrics

- **Parameter recovery error:** |fitted Km - true Km| / true Km and the same for
  Vmax (synthetic data, where truth is known).
- **Method comparison:** recovered Km/Vmax from nonlinear fit vs. Lineweaver-Burk
  across increasing noise levels.
- **Goodness of fit:** residual sum of squares / R^2 of the fitted curve.
- **Visual check:** the Michaelis-Menten curve overlaid on the data, plus the
  double-reciprocal plot, as a sanity check that the saturation shape is right.

## Domain Context

### The Michaelis-Menten equation
- `v = Vmax * [S] / (Km + [S])`
- At `[S] = Km`, `v = Vmax / 2` (this is the definition of Km).
- At high `[S]`, `v -> Vmax` (enzyme saturated).

### Lineweaver-Burk (the linearized shortcut)
- Taking reciprocals: `1/v = (Km/Vmax)(1/[S]) + 1/Vmax`, a straight line.
- Historically used because a line is easy to fit by hand, but the reciprocal
  transform distorts the error structure, so low-[S] points (large 1/[S],
  noisy) dominate the fit. This is the bias the demo demonstrates.

### Inhibition (optional extension)
- **Competitive:** apparent Km increases, Vmax unchanged.
- **Noncompetitive:** Vmax decreases, Km unchanged.
- A later iteration can generate data under one inhibition model and check that
  the fit recovers the expected change in the apparent parameters.

### Fidelity ladder (SMAIRT data progression)
1. **Synthetic, clean:** generate v from known Km/Vmax with small noise; confirm
   both methods recover the truth. (Start here.)
2. **Synthetic, noisy:** increase noise and compare nonlinear vs. Lineweaver-Burk
   parameter recovery; show the linearized method's bias.
3. **Inhibition (optional):** add a competitive or noncompetitive inhibitor and
   verify the expected shift in apparent Km/Vmax.
4. **Real (optional, later):** fit a small published v-vs-[S] dataset; truth is
   unknown, so you report confidence intervals and compare to literature values.

### Caveats
- Michaelis-Menten assumes steady state, a single substrate, no product
  inhibition, and initial-rate measurements. Real assays can violate these.
  Stating the assumptions next to the fitted numbers is part of the SMAIRT
  method.

## Known parameters (suggested starting values)

| Quantity | Value |
|----------|-------|
| true Vmax | 100 (rate units) |
| true Km | 5 (concentration units) |
| substrate range [S] | ~0.5 to 50 (several points) |
| measurement noise (relative) | start ~2-5%, then increase |
| random seed | fixed (reproducibility) |
