# Offline fixture: JHU CSSE COVID-19, Italy rows

## Contents

| Filename | Rows | Bytes | Used by |
|---|---|---|---|
| `italy_confirmed.csv` | header + 1 | 18,188 | iteration 04 with `--offline` |
| `italy_deaths.csv` | header + 1 | 16,542 | iteration 04 with `--offline` |
| `italy_recovered.csv` | header + 1 | 14,176 | iteration 04 with `--offline` |

## What this is

A subset of the real data, not a synthetic stand-in. Each file holds the header and the single
`Country/Region == "Italy"` row from the corresponding global time-series file, taken from the
pinned commit below. Those are exactly the rows `script_04_fit_published_outbreak.py` reads, so a
fit against this fixture produces the same parameters as a fit against the 3.9 MB global files:
beta 0.23081955, gamma 0.05206253, mu 0.03663978, R0 2.60218185.

## Provenance

- **Source organization**: Johns Hopkins University Center for Systems Science and Engineering
  (JHU CSSE)
- **Dataset**: COVID-19 Data Repository, global confirmed / deaths / recovered daily time series
- **Repository**: <https://github.com/CSSEGISandData/COVID-19>
- **Pinned commit**: `4360e50239b4eb6b22f3a1759323748f36752177`
- **Source version**: final commit before the repository was archived on 2023-03-10
- **Retrieved**: 2026-08-05
- **License**: CC BY 4.0 for the data. See the repository's terms of use, which permit
  redistribution with attribution for educational and academic research purposes.
- **Transformation**: row selection only. No values were altered, recomputed, or reformatted.

Upstream SHA-256, verified against the pinned URLs and enforced by the script before any fit:

| Global file | SHA-256 |
|---|---|
| `time_series_covid19_confirmed_global.csv` | `e6234a59eec4359d2577358b5220e1a7e3da74c162913cdb7d882db1413f98c2` |
| `time_series_covid19_deaths_global.csv` | `4e87757a3e059c45650a1e1856614f8e339ee3c70653c378a7ba6f7b0ee8c72e` |
| `time_series_covid19_recovered_global.csv` | `381bb7527a52114d3f07b40c25dc8aba0b6283aa535e97cba97152ce3cbdb526` |

## Reconstructing this fixture

```bash
COMMIT=4360e50239b4eb6b22f3a1759323748f36752177
BASE="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/$COMMIT/csse_covid_19_data/csse_covid_19_time_series"
for KIND in confirmed deaths recovered; do
  curl -sfL "$BASE/time_series_covid19_${KIND}_global.csv" -o "global_${KIND}.csv"
  head -1 "global_${KIND}.csv"            >  "italy_${KIND}.csv"
  awk -F, '$2 == "Italy"' "global_${KIND}.csv" >> "italy_${KIND}.csv"
done
shasum -a 256 global_*.csv   # compare against the table above
```

## Why the global files are not committed

They were, at 3.9 MB, for three rows. The script now fetches them from the pinned commit on demand
and verifies each against the checksums above, so the large payload is reproducible rather than
stored. `--offline` uses this fixture instead and needs no network.

## Caveat on the science

Reported confirmed, recovered, and deaths are not direct measurements of the SIRD compartments.
Case ascertainment changed over time and between countries, and "recovered" reporting was
particularly inconsistent. `analysis/ANALYSIS_04.md` states what this limits.
