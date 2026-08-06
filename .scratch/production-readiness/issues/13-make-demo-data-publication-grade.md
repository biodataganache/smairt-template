# Make demo data provenance publication-grade

Type: task
Status: resolved
Blocked by: 10, 11, 12

## Question

Can every retained external or curated datum be redistributed, cited, reproduced, and verified by a future reader?

## Work

- For every `data/downloaded/README.md`, record source organization, dataset or query, stable URL, retrieval date, source version or commit, license/terms, transformation, local filename, and checksum.
- Keep small Puromycin, UniProt, and STRING fixtures only when their redistribution and construction are explicit.
- Remove the committed JHU CSV snapshot. Fetch from a pinned repository commit, verify checksums, document network failure behavior, and retain only the smallest justified offline test fixture.
- For generated synthetic data, record seeds and generating scripts instead of treating generated files as external sources.
- Verify every external link and checksum from a clean checkout.

## Resolution

Resolve when a publication reviewer can answer where every input came from, whether it may be redistributed, how it was transformed, and how to reconstruct or verify it without reading experiment code.

## Resolved

Inventoried every committed payload rather than only the JHU snapshot the ticket named. Seven files
across five demos, plus three directories whose empty templates implied data that was not there.

**JHU snapshot removed.** 3.9 MB of global CSVs replaced by a fetch from pinned commit
`4360e50239b4eb6b22f3a1759323748f36752177` — the final commit before the repository was archived on
2023-03-10 — with a recorded SHA-256 per file, enforced before any fit. The previous code fetched
from mutable `master` and accepted any cache above zero bytes, so a truncated download would have
been fitted silently. Verified: a truncated cache is now detected, refused, and re-fetched.

**Offline fixture at 64 KB instead of 3.9 MB.** Italy's rows from the same pinned commit — a subset
of the real data, not a synthetic stand-in. `--offline` reproduces the invariants exactly: beta
0.23081955, gamma 0.05206253, mu 0.03663978, R0 2.60218185.

**Two findings the empty templates were hiding:**

- `ppi_network/yeast_ppi.csv` mixes STRING data with **local annotations**. The `p1_essential` and
  `p2_essential` columns are a hardcoded gene set at `script_B01:96`, not a deletion-project export
   — and Precision@3 is scored against them. Recorded as author-asserted rather than sourced.
- `protein_properties/uniprot_benchmark.csv` sequences are **truncated to 200 residues**
  (`script_03:179,194`). A transmembrane helix beyond residue 200 is removed, so a protein labelled
  transmembrane could appear soluble. The reported accuracy is for truncated sequences.

**Synthetic data** now records seeds, parameters, generating script, and line references instead of
being described as an external source. Proteomics' planted truth is 50 of 2000 proteins at
`script_01:70`.

Live services (STRING, UniProt) are documented as **not** byte-reproducible: no release version was
recorded at retrieval. The committed file plus checksum is what makes each result checkable, and
per-accession URLs are given for verifying individual entries.

Verified from a clean checkout: all four external URLs return 200, the offline and network paths
agree, and the corrupt-cache path recovers.

Three tests hold it: every payload named in a README beside it, every such README recording a
checksum, and the JHU snapshot staying uncommitted with its pin, checksums, and offline flag intact.
