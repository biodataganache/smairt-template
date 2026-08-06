# Make demo data provenance publication-grade

Type: task
Status: unclaimed
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
