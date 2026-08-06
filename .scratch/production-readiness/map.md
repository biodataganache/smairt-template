# Production-ready framework repository

## Destination

This branch is ready to replace `main` as SMAIRT's publication-facing framework repository: a newcomer has one truthful front door, every active document and example matches the installed toolkit, all eight demos are reproducible current generated projects, platform and package checks are green, and an independent adversarial review finds no unresolved release blocker.

## Notes

- This is a planning map. A ticket resolves one decision or one prerequisite task; implementation work begins only when that ticket is claimed.
- Treat `CONTEXT.md` as the domain language and `docs/adr/0001-0003` as accepted decisions. Do not re-litigate those ADRs without evidence of real friction.
- Use the codebase-design vocabulary when changing architecture: **module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, and **locality**. The interface is the test surface. Apply the deletion test before extracting or retaining a module. One adapter is a hypothetical seam; two adapters make it real.
- Rewrite all eight completed demos against the current `smairt` CLI. Do not preserve the cookiecutter-era structure merely for compatibility.
- Keep small downloaded fixtures only with publication-grade provenance. Fetch the 4.1 MB JHU COVID-19 data on demand from a pinned source rather than committing the snapshot.
- Make `README.md` the single newcomer front door. It should point to current demos for examples and to a smaller `docs/` hierarchy for depth. Compress and update the tutorials rather than keeping five competing introductions.
- Delete `plans/` and `adversarial_review1.md` after confirming their durable outcomes are represented by current documentation and changelog entries.
- Remove `.scratch/smairt-agentic-fork/` and `docs/adr/0004-0010` from this branch. All 17 files were verified byte-for-byte identical to `fork/planning/agentic-science-foundation`; they belong to `sarodarte2/smairt-lab` and are already there.
- Do cleanup before opening the pull request. Reproduce the support matrix before then; the final pull request remains the authoritative GitHub Actions run.
- Use `ai-incubator/gpt-5.6-sol-project` for the final adversarial review, at the highest available reasoning setting.
- Do not commit the three untracked `docs/experimental/*.pdf` files. They are unreferenced source material for the fork effort, not toolkit documentation.

## Decisions so far

<!-- Closed ticket decisions are appended here as one-line context pointers. -->

- [Correct false statements in shipped guidance](issues/02-correct-false-shipped-guidance.md) — fixed each at the level the falsehood lived: `smairt open` now reports state through the dashboard's own `next_workflow_action()`, guided creation refuses `--paper`/`--hpc` instead of discarding them, and `CONTEXT_INDEX.md` no longer promises an iteration `new_track.py` never creates.
- [Prove the supported platform matrix before the pull request](issues/01-prove-the-supported-platform-matrix.md) — all six cells green on real runners after fixing what only a clean checkout could see: `scripts/utilities` shipped empty, so Git dropped it from every clone and from the golden fixtures meant to catch exactly that drift. Scaffold bumped to `0.5.0`; CI now reachable from `verify/**` and `workflow_dispatch`.

- [Decide whether Run History is a declared scaffold asset](issues/03-decide-run-history-ownership.md) — declared as `researcher-work` and shipped with every project, because ADR 0001 makes the blueprint authoritative and an evidence record should not be invisible to check, inspect, and upgrade. Found and fixed two defects on the way: the golden updater deleted fixtures before proving the tool worked, and nothing asserted the blueprint was loadable.

- [Design one newcomer path and a smaller documentation hierarchy](issues/05-design-one-newcomer-path.md) — README as the only introduction; `docs/workflow.md`, `docs/capabilities.md`, `docs/upgrading.md`, `docs/development.md` for depth; the four root tutorials deleted rather than redirected. The overlap was the visible problem, but the real one is that no reader-facing doc teaches the helper-driven loop and two actively contradict it by telling researchers to hand-create numbered scripts.

- [Remove fork and superseded planning residue](issues/04-remove-fork-and-planning-residue.md) — 17 fork files returned to the fork's keeping after re-verifying they were byte-identical there, plus 6 superseded planning records deleted and the 3 experimental PDFs dropped. ADRs resume at 0004; survivors keep their numbers because they are cited.

## Not yet specified

- Whether demo verification belongs in every CI matrix cell, one representative cell, or a separate scheduled job. This becomes decidable after the demo smoke interface and runtime are known.
- Whether merging this effort should immediately create the `v0.4.0` tag or leave release publication as a separately approved act.
- Whether the portable `skills/` directory remains part of this framework repository after its current instructions are corrected, or ultimately belongs with the SMAIRT Lab fork.
- Whether `demos/bring_your_own/` remains a standalone worksheet once the newcomer path and eight current demos are complete.

## Out of scope

- Implementing the nine SMAIRT Lab agentic-science tickets; that work belongs to `sarodarte2/smairt-lab`.
- Publishing to PyPI. This effort may make the package publishable, but repository readiness and package publication are separate approvals.
- Reworking `legacy/cookiecutter/` beyond keeping it clearly isolated as a historical reference.
- Adding Paper or HPC to demos that do not scientifically need those capabilities. Empty legacy directories are not a reason to enable a capability.
