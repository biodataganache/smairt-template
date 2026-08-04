# Iteration Log

One row per iteration, in the order the work happened.

An iteration is one attempt at moving the work forward: one script, the log it produced,
and the interpretation of that log. Iterations are numbered across the whole project, so
this table reads as a timeline of what was tried.

`scripts/new_iteration.py` appends a row when it creates an iteration. Rows are appended
and never rewritten: a row that turned out to be wrong is corrected by a later row saying
so, because the sequence of attempts is itself evidence.

`Kind` is `single` when the iteration tests one change, or `panel (N)` when it probes N
candidate directions at once.

`Outcome` is prose rather than a keyword. A panel that improves three of eight candidates
and regresses one cannot be described by a single verdict, and `SUPPORTED` would discard
the finding. Write what happened; the full result belongs in the matching
`analysis/ANALYSIS_NN.md`, and this table is the index into it.

Fill in `Outcome` after interpreting the run, not before.

| Iteration | Date | Script | Hypotheses | Kind | Changed from | Outcome |
|---|---|---|---|---|---|---|
