# Downloaded data

| Filename | Rows | Source | Used by |
|---|---|---|---|
| `yeast_ppi.csv` | header + 15 | STRING database API v12 | iteration B02 (`script_B02_yeast_benchmark.py`) |

- **SHA-256**: `e0bf2ca888b4f8b2a28ac92fedc9225cea9c0ce837a17ac769f706efa78d5142`

## Provenance

- **Source organization**: STRING Consortium (string-db.org)
- **Dataset**: STRING v12 protein-protein interaction network, *Saccharomyces cerevisiae*
  (NCBI taxon 4932)
- **Endpoint**: `https://string-db.org/api/tsv/network`
- **Query**: the ten genes `RPL3, RPL4, RPS3, RPS4, HTA1, HTB1, HHO1, ACT1, MYO2, COF1`, chosen to
  span three biological modules — ribosome, chromatin, and cytoskeleton — so that community
  detection has a curated ground truth to be scored against.
- **Retrieved**: 2026-07 by `script_B01_download_yeast_data.py`
- **License**: STRING data are released under CC BY 4.0.
- **Transformation**: the API's TSV response was reduced to the columns `p1, p2, score`, and two
  columns were **added locally** (see below). The `source` column records `STRING_API`, meaning
  this file came from the live API rather than from the script's hardcoded fallback.

## What is not from STRING

Two columns in this file are **local annotations, not STRING data**, and the distinction matters
because the benchmark's Precision@3 metric is scored against them:

- `p1_essential` / `p2_essential`: membership in the hardcoded set
  `{RPL3, RPL4, RPS3, RPS4, ACT1, COF1, MYO2}`, defined at
  `script_B01_download_yeast_data.py:96`. These reflect well-established yeast essentiality but are
  **not** a programmatic export from the *Saccharomyces* Genome Deletion Project, and no accession
  or version is recorded for them.
- `module`: the curated three-way module assignment used as the community-detection ground truth.

A reviewer should treat the essentiality labels as author-asserted rather than sourced. Recomputing
them from a cited deletion-project release would make the Precision@3 result independently
checkable; today it is not.

## Reproducing the query

```bash
GENES="RPL3%0dRPL4%0dRPS3%0dRPS4%0dHTA1%0dHTB1%0dHHO1%0dACT1%0dMYO2%0dCOF1"
curl -sfL "https://string-db.org/api/tsv/network?identifiers=$GENES&species=4932&caller_identity=smairt_pipeline"
```

STRING is a live service and its scores change between releases, so this query is **not** expected
to reproduce the committed file byte-for-byte. The committed file plus its checksum is what makes
the recorded result checkable; the query above is how to obtain current data for comparison.

## Fallback path

If the API is unreachable, `script_B01` substitutes a hardcoded interaction list and marks the
`source` column `Curated_Fallback`. Any file whose `source` column is not `STRING_API` did not come
from the database.
