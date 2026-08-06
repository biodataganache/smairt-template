# Design one newcomer path and a smaller documentation hierarchy

Type: grilling
Status: resolved
Blocked by: None

## Question

What is the smallest truthful reading path from repository landing page to first generated project to deeper framework guidance?

## Known friction

- `README.md`, `QUICKSTART.md`, `TUTORIAL.md`, `TUTORIAL_HPC.md`, and `TUTORIAL_PAPER_DRIVEN.md` repeat installation, creation, capabilities, checks, and legacy notices.
- The individual files are mostly accurate, but a newcomer must compare several introductions to discover which one is authoritative.
- The eight demos should be evidence and examples, not competing setup guides.

## Resolution

Decide the purpose, audience, and unique information owned by `README.md` and each retained document under `docs/`. Define redirects or removals for old root paths, the tutorial hierarchy, and where contributor-only history belongs. Do not draft prose yet and do not preserve a file merely because it exists.

## Answer

### The finding that shaped the decision

The five files overlap heavily — install appears in four, the `smairt new` block in five, the
legacy notice in three — but that is not the real problem. **No reader-facing document teaches
the actual research loop.** Only `docs/scaffold-transition.md`, a contributor history, names
`new_track.py`, `new_iteration.py`, or `record_outcome.py`.

Worse, the two that try actively contradict shipped behaviour. `QUICKSTART.md:56` says "Create
an experiment in the selected `experiments/` phase directory" and `TUTORIAL.md:40` says "write
and run the experiment", while `scripts/README.md:23` reserves numbering: "Only
`new_iteration.py` assigns a number." A researcher following the front-page tutorial creates an
unnumbered script that joins no hypothesis, appears in no iteration log, and breaks the chain
the whole workflow exists to build.

So this is not a tidying exercise. Consolidation is the vehicle; correctness is the point.

### Structure

**`README.md` — the only newcomer introduction.** What SMAIRT is, install, one complete
`smairt new`, the loop in six named commands, where to go next. Everything a first-time reader
needs and nothing they do not: upgrade mechanics, exit-code tables, and limits move to `docs/`.
Target well under its current 264 lines.

**`docs/workflow.md` — the research loop, in depth.** Absorbs `QUICKSTART.md` and `TUTORIAL.md`.
The authoritative sequence: `new_track.py`, complete and commit the criteria, `new_iteration.py`,
run it, write `ANALYSIS_NN.md`, `record_outcome.py`, optionally `select_result.py`. Explains why
numbering is exclusive and why criteria are committed first.

**`docs/capabilities.md` — Paper and HPC together.** Absorbs both capability tutorials. They are
one concept — additive overlays, non-destructive deactivation — and splitting them duplicated
the enable/disable/verify shape twice.

**`docs/upgrading.md`** — scaffold versions, mismatch, `upgrade` semantics, exit codes.
**`docs/development.md`** — clone guidance, gates, goldens, blueprint diff, release.

`docs/scaffold-transition.md` stays contributor history. `docs/MODERNIZATION_PROPOSAL.md` is
already marked superseded and goes with the other historical files in ticket 04.

### Removals

`QUICKSTART.md`, `TUTORIAL.md`, `TUTORIAL_HPC.md`, `TUTORIAL_PAPER_DRIVEN.md` are deleted, not
redirected. This branch has never been `main`, so no published link points at them and a
redirect stub would be a file whose only content is an apology. Root keeps `README.md`,
`CHANGELOG.md`, `CONTEXT.md`, `AGENTS.md`, `LICENSE`.

### Rules the rewrite must hold

1. Install instructions exist in exactly one place.
2. One complete `smairt new` invocation in the README; `docs/` references it rather than
   repeating it.
3. Every documented workflow command goes through the helper that owns it — no hand-created
   numbered scripts anywhere.
4. The legacy Cookiecutter notice appears once.
5. Demos are cited as evidence, never as a setup path.

### Sequencing note

The README cannot be finished until the demos it points at exist, so ticket 06 stays blocked on
the demo work. `docs/workflow.md` and `docs/capabilities.md` do not depend on the demos and can
proceed in ticket 07 as soon as this decision lands.
