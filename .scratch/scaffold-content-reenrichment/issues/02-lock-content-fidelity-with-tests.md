# 02 - Lock content fidelity with tests

Status: ready-for-agent
Type: task
Blocked by: 01

## Question

How do we make "restored" falsifiable, so that placeholder content fails the suite instead of passing review?

## Context

The current gap exists because generator and checker agreed with each other while the content quietly thinned. `docs/scaffold-transition.md` records every asset as "Restored at same path," which was true and still allowed `prompts/KNOWN_PATTERNS.md` to ship at 179 bytes against a 12,541-byte original.

ADR 0001 already requires independent verification of the generated surface. Golden projects satisfy that for structure and exact text, but they cannot distinguish intentional brevity from accidental loss — regenerating them absorbs any change. A separate, cheap signal is needed.

This ticket lands the tests before the content work, so the backlog has a definition of done that does not depend on a reviewer's judgement of prose.

## Acceptance

- A fidelity test compares each re-enriched scaffold asset against its counterpart under `legacy/cookiecutter/original-template/{{ cookiecutter.project_slug }}/` and fails when retained bytes fall below a declared per-asset floor.
- The floor is data, not scattered literals: one readable table or mapping that a reviewer can audit in a single place.
- Assets with no legacy counterpart are explicitly exempted by name, not by silent absence: `.gitignore`, `hpc/slurm_job.sh`, `paper/analysis/README.md`, `paper/FINAL_MANIFEST.md`, `paper/README.md`.
- A prohibition test asserts generated guidance contains no reference to retired concepts: workflow modes, browser-paste or session-transfer compilation, the filenames `compile_for_ai.py`, `new_experiment.py`, `new_iteration.py`, `finalize_iteration.py`, claims that phase directories are conditional, or claims that SMAIRT submits or manages cluster jobs.
- Both tests fail loudly against the current thinned scaffold, proving they detect the defect they exist for.
- Tests assert byte ratios and forbidden substrings only. No test asserts an exact sentence of guidance.

## Notes

Expect this ticket to leave the suite red. That is the point: tickets 03 through 07 turn it green by supplying content. Record the starting failure count in the ticket comments so progress is measurable.

The byte floor is a detection heuristic. A shorter asset that fully covers current behavior is acceptable — in that case, lower the declared floor for that asset deliberately and record why, rather than padding the prose.
