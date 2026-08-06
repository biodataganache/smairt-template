# Rewrite the protein language model demo as a current generated project

Type: task
Status: dropped
Blocked by: 08, 09

## Question

Can the largest demo preserve its nine-step scientific narrative while remaining runnable, explicit about model downloads, and representative of the current framework?

## Work

- Generate a fresh current project and recreate nine hypotheses, nine formal iterations, nine analyses, and the final synthesis through the current helper interfaces.
- Preserve the sequence from synthetic generator validation through motif, conservation, family, covariation, and coupling tests to the ESM-2 real-data rung.
- Move UniProt acquisition to the chosen utility seam and document accession-level provenance.
- Make PyTorch, `fair-esm`, model-weight downloads, CPU expectations, network access, cache location, and runtime explicit. Provide a deterministic fast verification path without pretending it proves the full model result.
- Regenerate the 17 figures and compare scientific invariants with the retained historical outputs before deleting old structure.
- Add current provenance, run status, outcome records, and selected-result evidence to every rung.

## Resolution

Resolve when a clean environment can run the documented default path, the optional ESM-2 rung is independently reproducible, `smairt check` passes, and all claims in the demo are traceable to current logs and analyses.

## Outcome: dropped, not deferred

Decided against rewriting this demo. It is ~4,300 lines across nine rungs, needs PyTorch,
optional `fair-esm`, and a model-weight download, so it is the most expensive demo to migrate
and the least likely to be run by a newcomer.

It stays in the repository as a legacy demo under the `demos/README.md` warning. The cost of
migration is not repaid by what it teaches about the current workflow: the light and medium
demos already show every helper in the loop, on data a reader can obtain in seconds.

Ticket 09's recipe is written so this demo *could* be migrated later. Nothing here blocks it.
