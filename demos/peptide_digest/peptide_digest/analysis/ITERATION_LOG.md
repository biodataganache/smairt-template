# Iteration Log

> **Imported index.** This project's science predates the current workflow. These rows were read
> from the legacy `analysis/ANALYSIS_NN.md` files during migration; they were not written by
> `scripts/new_iteration.py` as they would be in a project built with the current toolkit.
>
> What that means for a reader: every outcome below is sourced to the analysis file that states
> it, and the analyses are the authority. Run dates are recorded as unknown, because the original
> executions predate this project's execution record and inventing a date would be a fabrication.
> Iterations run from here on will be recorded normally.

An iteration is one attempt at moving the work forward: one script, the log it produced, and the
interpretation of that log. Iterations are numbered across the whole project, so these records
read as a timeline of what was tried.

## Current state

| Iteration | Date | Script | Hypotheses | Kind | Changed from | Outcome |
|---|---|---|---|---|---|---|
| 01 | unknown (imported) | `script_01_tryptic_digestion_smoke_test` | HYPOTHESIS_01 | single | — | Supported. Rule-based tryptic digestion reproduced hand-curated expected peptides exactly. See ANALYSIS_01.md. |
| 02 | unknown (imported) | `script_02_missed_cleavages_validation` | HYPOTHESIS_02 | single | 01 | Supported. Missed-cleavage handling for N=0,1,2 verified against hand-curated cases. See ANALYSIS_02.md. |
| 03 | unknown (imported) | `script_03_peptide_filtration` | HYPOTHESIS_03 | single | 02 | Supported. Observable-peptide filtering behaved as predicted on mass and length bounds. See ANALYSIS_03.md. |

## Outcome history

Appended, never edited. This section is empty by design: it records *when a reading was made*,
and the readings below predate this record. The imported outcomes are in the table above, sourced
to their analysis files.

| Date | Iteration | Outcome recorded |
|---|---|---|
