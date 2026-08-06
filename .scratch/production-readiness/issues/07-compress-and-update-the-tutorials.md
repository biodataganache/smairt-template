# Compress and update the tutorials under docs

Type: task
Status: unclaimed
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
