# Normalize demo iterations and scientific utilities

Type: task
Status: unclaimed
Blocked by: 02, 03

## Question

Can the old scientific work enter the current generated-project interface without preserving a second numbering system or treating data acquisition as an experiment?

## Work

- Use `new_track.py` and `new_iteration.py` as the sole numbering authority when recreating plans, hypotheses, and iterations.
- Reclassify five support programs as utilities or fold them into a real iteration: Lunar's two intercept searches, protein properties' benchmark downloader, PPI's STRING downloader, and protein LM's UniProt fetcher.
- Normalize PPI `script_B01/B02` and `ANALYSIS_B01` into one project-wide numeric timeline.
- Normalize proteomics hypotheses from `H1_*` to `HYPOTHESIS_NN` while preserving scientific prose.
- Define the repeatable migration recipe for carrying science code into a fresh generated project: provenance header, `record_run_status`, exact log path, matching analysis, and recorded outcome.
- Test the recipe through generated-project and helper interfaces, not through migration-only private functions.

## Resolution

Resolve when one documented recipe can migrate the remaining 31 formal iterations and five utilities without manual numbering or hidden workflow exceptions.
