# Add a demo verification seam

Type: task
Status: unclaimed
Blocked by: 10, 11, 12, 13

## Question

What is the smallest stable interface that proves every demo is a current, runnable scientific example without making CI execute every expensive experiment on every matrix cell?

## Work

- Design one verification module or script whose interface covers project contract validity, `smairt check`, dependency/import health, documented command existence, and fast scientific invariants.
- Keep heavyweight network/model runs behind an explicit slower adapter only if there are genuinely two execution modes. One adapter is not a reason to invent a seam.
- Apply the deletion test: deleting this module should force verification complexity back into eight demos and CI, demonstrating real depth and leverage.
- Make the interface the test surface. Avoid per-demo test glue that merely mirrors each script's implementation.
- Decide, based on measured runtime, whether verification runs in every CI cell, one representative cell, or a scheduled job; update the map's fog with the decision.

## Resolution

Resolve when one command gives maintainers a truthful fast signal for all eight demos, slower evidence runs are explicit, and CI exercises the chosen interface at the documented cadence.
