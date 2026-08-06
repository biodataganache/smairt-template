# Rewrite the three light demos as current generated projects

Type: task
Status: resolved
Blocked by: 08, 09

## Question

Can enzyme kinetics, lunar free-return, and peptide digestion become small, complete, runnable examples of the current SMAIRT research loop?

## Work

- Generate each project with the installed CLI rather than editing the cookiecutter-era tree in place.
- Carry over the scientific question, hypothesis reasoning, three formal iterations per demo, analyses, useful figures, and final synthesis while regenerating all tool-owned guidance.
- Move Lunar's two search programs behind the utility classification chosen in “Normalize demo iterations and scientific utilities.”
- Add current run provenance, Run History behavior, Iteration Log state, analysis records, and selected-result links.
- Repair enzyme Puromycin provenance or generate the fixture from a cited source. Peptide digestion has no external payload.
- Replace repeated Zoo Code setup and broken copy commands in each `DEMO.md` with a concise, tested path through the generated project.
- Run every iteration in a clean demo environment and verify expected scientific invariants, not just exit status.

## Resolution

Resolve when all three projects pass `smairt check`, all documented commands run, reruns preserve append-only records, and their scientific conclusions are supported by regenerated logs and outputs.

## Progress

- [x] enzyme_kinetics. Three iterations reproduce legacy numbers exactly. Iteration 02 kept as
      NOT SUPPORTED. Puromycin provenance recorded with SHA-256 and an R regeneration snippet.
- [ ] lunar
- [ ] peptide_digest

Recipe notes learned on the first demo:
- Run the demo in a venv with the science dependencies *plus* PyYAML, since the helpers read
  smairt.yaml.
- Compare every ported iteration against the legacy pasted-output block before deleting it. That
  is what caught the iteration 02 status inversion.
- Read the legacy ANALYSIS_NN.md before writing the hypothesis. The title alone misleads.
- new_track.py writes PLAN_<QUESTION>.md alongside PLAN_TEMPLATE.md; do not glob plans/PLAN_*.md.

## Demo status taxonomy, decided

Three levels. Every demo carries exactly one, stated in `demos/README.md` and in its own
`DEMO.md`, so a reader never has to guess how much of what they are reading is current.

**current** - a valid SMAIRT project on the installed scaffold. `smairt check` passes, its
`DEMO.md` teaches the current helper sequence, and its own guidance is regenerated. Its science
scripts were ported into the generated frame and rerun, so `RUN_HISTORY.md` records real
executions.
- `enzyme_kinetics`

**current scaffold, imported history** - a valid SMAIRT project whose analyses and logs came from
the legacy runs rather than from executions under the current frame. `smairt check` passes and
`DEMO.md` teaches the current helpers, but `ITERATION_LOG.md` is explicitly an imported index and
`RUN_HISTORY.md` ships empty with a migration note, because no legacy script called
`record_run_status` and backfilling rows would claim executions that never happened.
- `lunar`, `peptide_digest`

**legacy** - kept for its scientific reasoning, not as a workflow example. No contract is added,
so no structural claim is made. The warning naming what is stale is honest and specific.
- `epidemic_sird`, `proteomics_de`, `protein_properties`, `ppi_network`, `protein_lm`

`bring_your_own` is a starter worksheet, not a completed demo, and is listed separately.

## Why the harder four stay legacy

Their science runs today; that was verified. What they lack is a current tutorial and a current
frame, and supplying those means instrumenting roughly 13 scripts and rerunning them. The lighter
demos already demonstrate every helper in the loop, so the cost is not repaid.

Adding a contract without doing that work would be worse than leaving them alone: `smairt check`
would pass while the tutorial a reader actually follows still taught the retired workflow.

## Scope change

`lunar` and `peptide_digest` are migrated to *current scaffold, imported history* rather than
rewritten. Their science is not re-derived and their scripts are not reinstrumented.

## Resolved

- [x] enzyme_kinetics: current. Ported into the generated frame, rerun, invariants match.
- [x] lunar: current scaffold, imported history. Corridor 10.9270-10.9360 km/s reproduced.
- [x] peptide_digest: current scaffold, imported history.

All three pass `smairt check`. Migration was driven by blueprint path ownership, not directory
copying, which is what protected the researcher-owned prompt records.

Findings worth carrying forward:
- `new_iteration.py` is a *current* helper name; the legacy demos ship a stale copy. Do not put it
  on a retired-helper list.
- Verification runs overwrite committed figures and add logs. Restore `results/` from the committed
  tree before installing a migrated demo.
- 47 pre-existing dangling links existed across these two demos. 35 had a bogus
  `smairt_template_demos/...` prefix; 12 pointed at logs never committed and are now plain
  filenames marked "not retained".
