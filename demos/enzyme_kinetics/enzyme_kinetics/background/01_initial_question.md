# Initial question

Can enzyme kinetic parameters be recovered from measured reaction velocities at several substrate
concentrations?

## Why this needs more than one iteration

The Michaelis-Menten equation relates reaction velocity to substrate concentration through two
parameters: Vmax, the saturating velocity, and Km, the concentration at half-maximal velocity.
Fitting it to data is routine. Knowing whether the resulting numbers can be trusted is not.

Three things have to be established in order, and each depends on the one before it:

1. **Does the method work where truth is known?** Synthetic data generated from planted
   parameters is the only setting where recovery error can be measured rather than estimated.
2. **How does it degrade, and is the classical alternative worse?** The Lineweaver-Burk
   double-reciprocal plot is still taught and still used. If it is worse, that should be
   demonstrated on data with known truth rather than asserted.
3. **Does it transfer to real data?** Real assay data has no planted truth, so the question
   becomes whether the estimate is credible and whether the model fits the observed saturation.

The interesting part of this demo is step 2, where the prediction was refuted. See
`analysis/ANALYSIS_02.md`.

## Scope

Three iterations, two synthetic and one on a public dataset. Inhibition models are out of scope.
