# Downloaded data

## Contents

| Filename | Source | Description | Used by |
|---|---|---|---|
| `puromycin_rates.csv` | R `datasets::Puromycin` | 23 initial-rate observations of a Michaelis-Menten reaction, treated and untreated | iteration 03 |

## Provenance

`puromycin_rates.csv` is the `Puromycin` dataset distributed with R in the `datasets` package,
which is part of a base R installation. The data originate from Treloar (1974) and are described
in Bates and Watts, *Nonlinear Regression Analysis and Its Applications* (1988), as data on the
reaction velocity of an enzymatic reaction with and without treatment by puromycin.

- Columns: `conc` (substrate concentration, ppm), `rate` (initial velocity, counts/min/min),
  `state` (`treated` or `untreated`), `source` (constant provenance string on every row).
- Rows: 23. The `treated` condition has 12 observations, `untreated` has 11. R's copy has one
  missing `untreated` observation, which is why the two conditions differ in count.
- SHA-256: `54277a6f316cbb71d82e77679ef29af018d6a1296144d98185c7b4d33e6aeba0`

To regenerate it from a base R installation:

```r
write.csv(
  transform(datasets::Puromycin, source = "R datasets::Puromycin"),
  "puromycin_rates.csv",
  row.names = FALSE
)
```

The file is committed because it is 23 rows and the demo must run offline. The checksum above is
what makes the committed copy checkable against the cited source rather than merely asserted to
match it.

## Licence

R's `datasets` package is distributed under GPL-2 | GPL-3. This dataset is widely redistributed
as a standard nonlinear-regression teaching example.
