# Compress and update the tutorials under docs

Type: task
Status: resolved
Blocked by: 05, 02

## Question

Can deeper guidance teach the current research loop, Paper, and HPC without repeating the README or preserving obsolete root-level introductions?

## Work

- Apply the hierarchy chosen in “Design one newcomer path and a smaller documentation hierarchy.”
- Consolidate `QUICKSTART.md`, `TUTORIAL.md`, `TUTORIAL_HPC.md`, and `TUTORIAL_PAPER_DRIVEN.md` into the smallest coherent set under `docs/`.
- Teach the authoritative loop: `new_track.py`, researcher-completed hypothesis criteria, `new_iteration.py`, execution, `ANALYSIS_NN.md`, `record_outcome.py`, and optional `select_result.py`.
- Explain Paper and HPC as additive capabilities, including non-destructive deactivation, without re-teaching installation.
- Keep `docs/scaffold-transition.md` contributor-facing, correct its known stale helper inventory, and distinguish historical behavior from the current scaffold.
- Add link and command validation appropriate to the final document set.

## Resolution

Resolve when every retained tutorial has one audience and one job, all workflows match shipped code, old root paths are removed or intentionally redirected, and no introduction competes with the README.

## Answer

Four root tutorials became four documents under `docs/`, and the correctness problem behind the
overlap is fixed.

`docs/workflow.md` teaches the real loop for the first time in reader-facing documentation:
`new_track.py`, commit the criteria, `new_iteration.py`, run, analyse, `record_outcome.py`,
optionally `select_result.py`. It leads with *why* the helpers own numbering, because the old
tutorials told researchers to create experiments by hand and that silently broke the chain.

`docs/capabilities.md` merges both capability tutorials. They were one concept — additive
overlays with non-destructive deactivation — split across two files that each repeated the
enable/disable/verify shape. It also documents that `--paper` needs a destination.

`docs/upgrading.md` takes the upgrade mechanics, exit-code table, and settings detail out of the
README, where they sat between a newcomer and their first project.

`docs/development.md` takes the contributor material and adds what the last few tickets taught:
prefer CI over local runs, nothing ships as an empty directory, every helper-created file must be
declared, and pty tests wait for the screen to settle.

`QUICKSTART.md`, `TUTORIAL.md`, `TUTORIAL_HPC.md`, and `TUTORIAL_PAPER_DRIVEN.md` are deleted.
The one reference to them, in the question issue template, now points at `docs/workflow.md`.

### Verification

Every command in `workflow.md`, `capabilities.md`, and the README was executed against a fresh
project — the full loop, utilities, `open`, `check`, and Paper enable/disable including the claim
that disabling deletes nothing. All relative links resolve. 187 tests pass.
