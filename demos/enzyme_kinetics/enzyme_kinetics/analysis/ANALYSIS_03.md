# ANALYSIS_03 - Michaelis-Menten fit to the public Puromycin dataset

Hypothesis: `hypotheses/HYPOTHESIS_03.md`
Iteration: 03
Log: recorded in `analysis/RUN_HISTORY.md`

## Data

`data/downloaded/puromycin_rates.csv`, 23 observations, provenance recorded in
`data/downloaded/README.md`. Treated: 12 observations across 6 concentrations. Untreated: 11
across 6.

## What was measured

| Condition | Vmax | SE | 95% CI | Km | SE | 95% CI | RSS | R^2 |
|---|---|---|---|---|---|---|---|---|
| treated | 212.683763 | 6.947 | [199.07, 226.30] | 0.064121 | 0.00828 | [0.0479, 0.0804] | 1195.45 | 0.9613 |
| untreated | 160.280092 | 6.480 | [147.58, 172.98] | 0.047708 | 0.00778 | [0.0325, 0.0630] | 859.60 | 0.9356 |

Treated/untreated Vmax ratio 1.326951, Km ratio 1.344030.

Lineweaver-Burk, diagnostic only: treated Vmax 195.80 (7.94% from nonlinear), Km 0.0484 (24.51%
from nonlinear); untreated Vmax 143.43 (10.51%), Km 0.0308 (35.36%).

## Against the predeclared criteria

All eight met: schema present, all values positive, both conditions above the observation and
unique-concentration minima, both fits converged, all parameters positive and finite, all
standard errors and intervals finite, fitted curves follow the observed saturation, and residuals
show no systematic structure.

## Interpretation

The method transfers to real data. Both conditions give positive, finite parameters with
intervals narrow enough to distinguish them: the treated Vmax interval [199.07, 226.30] does not
overlap the untreated [147.58, 172.98], so the higher treated Vmax is not an artefact of fitting
noise.

The Km intervals *do* overlap, [0.0479, 0.0804] against [0.0325, 0.0630]. The Km ratio of 1.344
should therefore not be reported as a real difference in substrate affinity. This is the same
weakness iterations 01 and 02 found: Km is the harder parameter, constrained by curvature that
fewer observations cover.

The Lineweaver-Burk diagnostic disagrees with the nonlinear fit by 24-35% on Km while agreeing
within 11% on Vmax. That is consistent with iteration 02 and is the reason it is not the primary
fit. Had only Lineweaver-Burk been run, the reported Km values would have been materially
different with nothing to reveal it.

## What this does not establish

That the Michaelis-Menten model is the right model for this enzyme. Residuals show no obvious
structure, but 11-12 points per condition cannot rule out mild misspecification. The claim is
credibility, not correctness -- there is no planted truth here to check against.
