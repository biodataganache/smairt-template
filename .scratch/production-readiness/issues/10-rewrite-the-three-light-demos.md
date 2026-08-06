# Rewrite the three light demos as current generated projects

Type: task
Status: in progress
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
