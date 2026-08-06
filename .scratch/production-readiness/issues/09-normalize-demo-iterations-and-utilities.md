# Normalize demo iterations and scientific utilities

Type: task
Status: resolved
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

## Correction: the ticket's classification premise was wrong

The ticket asserted five support programs needed reclassifying as utilities, naming "Lunar's two
intercept searches" among them. Reading the demos, that is not what they are.

Lunar's `script_02_lunar_intercept` and `script_03_multi_loop_return` each carry their own
hypothesis file with a prediction, a rationale, and numbered success criteria, and each has a
matching `ANALYSIS_NN.md`. `HYPOTHESIS_02` predicts a low-energy corridor terminating in a
leading-hemisphere impact and requires Jacobi-constant drift below 1e-6. That is an attempt at a
research question, not a search utility. Demoting them to `scripts/utilities/` would delete two
formal iterations and the criteria that make them falsifiable.

Only two of the five named programs are genuinely acquisition, and the hypothesis files say so
themselves:

- PPI `script_B01_download_yeast_data`: `HYPOTHESIS_B01` names `script_B02_yeast_benchmark` as
  its script. B01 only fetches STRING data; it tests nothing.
- protein properties `script_03_download_benchmark`: `HYPOTHESIS_03` lists it as "Script 1
  (Download)" and `script_04` as "Script 2 (Classify & Window)". One hypothesis, two programs,
  only the second an attempt.

The protein LM UniProt fetcher is already an unnumbered `fetch_uniprot_families.py` rather than a
numbered script, so it is correctly classified today, and that demo is dropped in any case.

So: two utilities, not five. The true iteration count is 23 across the seven demos being
migrated, not 31 across eight.

## The migration recipe

Numbering authority is `new_track.py` and `new_iteration.py`. Never hand-name a script or
hand-edit a log row.

1. Generate the project with the installed CLI into a scratch directory.
2. For each track, `new_track.py "<question>" <phase>`, then write the real prediction and
   criteria into the generated `HYPOTHESIS_01`, preserving the original scientific prose.
3. `new_iteration.py "<description>" <phase> --hypothesis HYPOTHESIS_NN` for each attempt, in the
   order the science happened, so numbering is the tool's.
4. Port the science body into the generated script, keeping the generated frame intact:
   `setup_logging` for the exact log path, `TeeLogger`, `write_provenance(config=CONFIG)`, and
   `record_run_status` in the `finally` block.
5. Acquisition code goes to `new_utility.py --purpose ...`, taking no iteration number.
6. Run the iteration. Confirm the log lands in `results/logs/` and a line appears in
   `analysis/RUN_HISTORY.md`.
7. Write `analysis/ANALYSIS_NN.md`, then `record_outcome.py NN --outcome "..."`, which refuses
   until the analysis exists.
8. `select_result.py NN --claim "..."` for the reportable result.
9. `smairt check` must pass.

Renaming decided: PPI `B01/B02` join the one numeric timeline as the download utility plus
iteration `03`, and `ANALYSIS_B01` becomes `ANALYSIS_03`. Proteomics `H1_*`/`H2_*`/`H3_*` become
`HYPOTHESIS_01/02/03` with prose preserved.
