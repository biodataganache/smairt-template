# Run History

Appended by generated iteration scripts. Each line identifies one execution, its exact log,
and whether it completed. Earlier lines are never edited.

Runs are events, so this file and `ITERATION_LOG.md` answer different questions. The
iteration log carries one current row per iteration: what it tested and how it turned out.
This file carries one line per *execution*, so a rerun does not erase the run before it and a
crash stays visible even when no interpretation is ever written for it.

A traceback that appeared only in a terminal is not part of the evidence. This is the file
that stops that happening.

| Date | Iteration | Status | Log |
|---|---|---|---|

## Migration note

This project's existing science ran before it was moved onto the current scaffold, and those
scripts do not call `record_run_status`. No rows have been backfilled: a row here asserts that a
specific execution happened and produced a specific log, and inventing one would make this file
useless for the purpose it exists to serve.

The evidence from those original runs is still present. Figures are in `results/figures/`, and the
interpretations are in `analysis/ANALYSIS_NN.md`. What is missing, honestly, is a per-execution
record for them.

Iterations created by `scripts/new_iteration.py` from here on will append rows normally.
