# Rewrite the four medium demos as current generated projects

Type: task
Status: dropped
Blocked by: 08, 09

## Question

Can protein properties, proteomics differential expression, PPI networks, and epidemic SIRD become reproducible current projects without weakening their scientific arguments?

## Work

- Generate all four projects with the installed CLI and migrate science through the normalized iteration recipe.
- Preserve the protein-properties calculators as scientific code and make the benchmark acquisition reproducible.
- Preserve proteomics' planted-truth and FDR reasoning, fix its dependency declaration, and regenerate its synthetic fixtures deterministically.
- Collapse PPI's Track B naming into the one numeric timeline while preserving the important conclusion that community recovery does not imply essentiality prediction.
- Replace the committed JHU snapshot in epidemic SIRD with a pinned, checksummed fetch path; preserve enough deterministic fixture data for a fast offline smoke test.
- Update each `DEMO.md`, run every formal iteration, and regenerate analyses, logs, figures, outcomes, and result selection.

## Resolution

Resolve when all four pass `smairt check`, reproduce their stated scientific invariants from documented environments, and contain no cookiecutter-era tool guidance or empty capability scaffolding.

## Open question, to settle inside this ticket

Whether `protein_properties`' calculators need a migration seam at all is not decided up front.
Its legacy scripts import calculator functions from the cookiecutter-era `scripts/shared/`,
which the current scaffold uses for logging and run-status helpers instead. The cheaper reading
is that these calculators are ordinary scientific code that belongs in `scripts/utilities/` or
inside the iteration that uses them, needing no framework change.

Do not add a seam speculatively. Carry the light demos and the first medium demos through the
recipe, then look at what the calculators actually need.

## Outcome: dropped in favour of honest legacy labelling

These four stay legacy. Verified first that their science still runs: `protein_properties`
script_02 reaches AUROC 1.0000 with its criteria passing, and the first iteration of
`epidemic_sird`, `proteomics_de`, and `ppi_network` all execute under their declared
dependencies. Nothing here is broken.

What they lack is a current tutorial and the generated run-status frame. Supplying both means
instrumenting and rerunning roughly 13 scripts, and normalising 46 `B01`/`B02` references across
10 files in `ppi_network` plus 36 `H1_`/`H2_`/`H3_` references across 16 files in
`proteomics_de` -- references that live in printed output and dependency assertions, not only in
filenames. The lighter demos already show every helper in the loop.

The `protein_properties` calculator question is settled and needed no framework change:
`scripts/shared/calculators.py` lives inside that demo and its own `__init__.py` exports the
functions. Ordinary in-demo scientific code.

Ticket 13's data-provenance work is *not* absorbed here. `ppi_network` and `protein_properties`
ship real payloads behind empty inventory templates, so that ticket stays open on its own terms.
