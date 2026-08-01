---
name: smairt-research
description: Use when helping with a SMAIRT computational research project that needs hypothesis-driven experiments, reproducible evidence, decisions, and a complete scientific audit trail.
---

# SMAIRT Research

Help the researcher use an existing SMAIRT project. New projects must be
created with the installed `smairt` CLI; this skill is not a generator.

## Core Stance

- The researcher owns novelty, judgment, validation, and conclusions.
- Record important human intellectual contributions explicitly.
- State uncertainty and verify consequential literature claims.
- Prefer readable project artifacts over conversational memory.

## Canonical Audit Trail

```text
question/background -> hypothesis -> phase experiment -> results/logs
  -> analysis/decision -> study report
```

1. Capture the question and relevant context in `background/`.
2. Write a testable hypothesis in `hypotheses/` before implementation.
3. Put a numbered experiment in the active phase under `experiments/`.
4. Preserve raw output in `results/logs/` and figures in `results/figures/`.
5. Interpret evidence and record the decision in `analysis/`.
6. Consolidate the completed chain into the study report.

Projects may start with synthetic, downloaded benchmark, or real data. Do not
claim that every project must traverse every phase.

## Practices

- Link each script to its hypothesis and phase.
- Match log names to experiment names where practical.
- Validate inputs and record parameters, dependencies, and reproducibility
  information.
- Distinguish raw results from interpretation.
- State whether evidence supports, refutes, or only partly supports the
  hypothesis, including limitations and the next decision.
- Read `prompts/AI_CONTEXT.md` and recent background, hypothesis, log, analysis,
  and report files when joining a project.
- Use `plans/` for complex work without treating plans as evidence.

If Paper is enabled, keep this audit trail and map accepted evidence into the
optional `paper/` workspace. Paper is an overlay, not another workflow mode.

Read `references/workflow.md` for the artifact map and session checklist.
