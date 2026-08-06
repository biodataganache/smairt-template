---
name: smairt-paper-driven
description: Use when a SMAIRT project has the optional Paper capability enabled and accepted research evidence must be mapped to an outline, manuscript element, or reviewer response.
---

# SMAIRT Paper Overlay

The skill name is retained for discovery, but Paper is an additive capability,
not a separate project mode. Use the core SMAIRT workflow and its audit trail:

```text
question/background -> hypothesis -> phase experiment -> results/logs
  -> analysis/decision -> study report
```

Run `smairt paper enable` in an existing project, or pass `--paper` to a complete
`smairt new ./project ...` command. Guided creation asks which capabilities to include, so
it refuses the flag rather than discarding it. Do not create a second project structure for
publication work.

## Overlay Workflow

1. Read `prompts/AI_CONTEXT.md`, the current study report, and
   `paper/outline.md`.
2. Identify the claim, figure, table, section, or reviewer concern being served.
3. Link it to an existing hypothesis and phase experiment, or run a new phase
   experiment through the canonical audit trail.
4. Preserve raw evidence in `results/logs/` and the scientific decision in
   `analysis/`.
5. Use `paper/analysis/` to map accepted evidence to the outline.
6. Keep exploratory interpretation in `analysis/`; do not make manuscript text
   the sole record of a scientific decision.

The researcher remains responsible for claims, authorship, validation, and the
decision to publish. Paper deactivation does not delete files.

Read `references/paper_driven_workflow.md` for mapping and review checklists.
