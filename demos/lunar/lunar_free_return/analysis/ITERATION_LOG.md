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
| 01 | unknown (imported) | `script_01_trajectory_sweep` | HYPOTHESIS_01 | single | — | Supported. Free-return corridor found at TLI 10.9270-10.9360 km/s; best case 10.9300 km/s gives 118.0 km return perigee and 23,938.3 km closest lunar approach. See ANALYSIS_01.md. |
| 02 | unknown (imported) | `script_02_lunar_intercept` | HYPOTHESIS_02 | single | 01 | Supported. Direct leading-hemisphere impact found below the free-return corridor speed, with Jacobi drift under 1e-6. See ANALYSIS_02.md. |
| 03 | unknown (imported) | `script_03_multi_loop_return` | HYPOTHESIS_03 | single | 01 | Partially supported. Safe flight and low-Earth return achieved, but the 3-loop target was not: maximum was 1.2711 loops, identifying a physical constraint. See ANALYSIS_03.md. |

## Outcome history

Appended, never edited. This section is empty by design: it records *when a reading was made*,
and the readings below predate this record. The imported outcomes are in the table above, sourced
to their analysis files.

| Date | Iteration | Outcome recorded |
|---|---|---|
