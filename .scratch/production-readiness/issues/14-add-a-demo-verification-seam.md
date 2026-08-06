# Add a demo verification seam

Type: task
Status: resolved
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

## Resolved

`tests/test_demos.py` is the seam, now 45 tests. It asserts the status taxonomy covers every demo,
and per demo: conforming demos carry `smairt.yaml`, `ITERATION_LOG.md`, `RUN_HISTORY.md`, `LICENSE`;
ship no retired helper; have guides naming `new_track.py`, `new_iteration.py`, `record_outcome.py`
and not claiming "no solution scripts"; and have no dangling local links. Legacy demos must declare
their status before their first section and point at `docs/workflow.md`.

Scope note: this checks the contract and the reader-facing claims, not scientific invariants.
Re-running demo science in CI would need the demo dependency sets installed; the invariants were
verified manually during migration and the key numbers are quoted in each `DEMO.md` so a reader can
check them.
