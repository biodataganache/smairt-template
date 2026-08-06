# Iteration Log

Two records in one file, because a reader needs two different things from them.

An iteration is one attempt at moving the work forward: one script, the log it produced,
and the interpretation of that log. Iterations are numbered across the whole project, so
these records read as a timeline of what was tried.

## Current state

One row per iteration, in the order the work happened. This is the scannable view: what
has been attempted, and what came of each attempt. `scripts/new_iteration.py` adds a row
when it creates an iteration.

`Kind` is `single` when the iteration tests one change, or `panel (N)` when it probes N
candidate directions at once.

`Outcome` is prose rather than a keyword. A panel that improves three of eight candidates
and regresses one cannot be described by a single verdict, and `SUPPORTED` would discard
the finding. Write what happened; the full result belongs in the matching
`analysis/ANALYSIS_NN.md`, and this table is the index into it.

`scripts/record_outcome.py` fills `[Record after interpreting]` the first time an outcome
is recorded. After that the cell holds your words, so a revised understanding is yours to
write; the helper appends to the history below and leaves the row alone. `smairt check`
reports a row that no longer agrees with the latest history entry.

| Iteration | Date | Script | Hypotheses | Kind | Changed from | Outcome |
|---|---|---|---|---|---|---|
| 01 | 2026-08-05 | `script_01_synthetic_nonlinear_fit` | HYPOTHESIS_01 | single | — | Supported: nonlinear least squares recovered Vmax within 2.626% and Km within 6.424% at 3% noise, both inside the 10% criterion. Km is the less precisely recovered parameter. |
| 02 | 2026-08-05 | `script_02_noise_lineweaver_comparison` | HYPOTHESIS_02 | single | — | NOT SUPPORTED: the predeclared breakdown rule was never triggered. Nonlinear fitting failed the Km criterion first, at 10% noise. Relative noise, not the reciprocal transform, decided the ordering. Lineweaver-Burk is still clearly worse at 40% noise, with 7 of 50 replicates nonphysical against nonlinear's 0. |
| 03 | 2026-08-05 | `script_03_puromycin_real_fit` | HYPOTHESIS_03 | single | — | Supported: both conditions gave positive, finite, plausible parameters. Non-overlapping Vmax intervals support the higher treated Vmax; overlapping Km intervals mean the Km ratio must not be reported as a real difference. |

## Outcome history

Appended, never edited. Every recording and every revision adds a line here, so a
conclusion that changed still shows what it changed from. The sequence of attempts, and of
readings of those attempts, is itself evidence.

| Date | Iteration | Outcome recorded |
|---|---|---|
| 2026-08-05 | 01 | Supported: nonlinear least squares recovered Vmax within 2.626% and Km within 6.424% at 3% noise, both inside the 10% criterion. Km is the less precisely recovered parameter. |
| 2026-08-05 | 02 | NOT SUPPORTED: the predeclared breakdown rule was never triggered. Nonlinear fitting failed the Km criterion first, at 10% noise. Relative noise, not the reciprocal transform, decided the ordering. Lineweaver-Burk is still clearly worse at 40% noise, with 7 of 50 replicates nonphysical against nonlinear's 0. |
| 2026-08-05 | 03 | Supported: both conditions gave positive, finite, plausible parameters. Non-overlapping Vmax intervals support the higher treated Vmax; overlapping Km intervals mean the Km ratio must not be reported as a real difference. |
