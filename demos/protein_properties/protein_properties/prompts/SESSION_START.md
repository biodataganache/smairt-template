# Session Start Guidance

## Onboarding or Context Refresh

Ask the assistant to read:

1. `smairt.yaml` for project status and capabilities.
2. `prompts/AI_CONTEXT.md` and `prompts/CONTEXT_INDEX.md` for workflow.
3. The active plan and current hypothesis.
4. Relevant experiment scripts, data provenance, raw logs, and analyses.
5. `analysis/STUDY_REPORT.md` if it exists.

Then ask for a concise summary of established evidence, open questions, and the next proposed
decision. Verify that summary against files before changing the project.

## Planning

Read existing plans, recent analyses, known patterns, and resource constraints. Create a plan
that names the hypothesis, success and rejection criteria, inputs, script, log, outputs, risks,
and expected analysis.

## Interpretation

Read the complete execution log, including stderr and traceback output. Compare observations
with criteria written before execution. Document support, refutation, boundaries, limitations,
alternative explanations, and the next decision in a new analysis file.

## Phase Transition

All phase folders already exist. Before changing `current_phase`, synthesize what transferred,
what did not, which data provenance is needed, and which experiments will test generalization.
Use `smairt settings --phase ...` to record the status change.

## HPC Preparation

When HPC support is enabled, adapt the editable files under `hpc/` to the actual cluster.
SMAIRT supplies guidance and templates but does not submit, cancel, monitor, or manage jobs.
Use `scripts/monitor_template.py` only to observe project-controlled progress files and logs.

## Handoff

A new researcher or assistant should read the same durable project files. Update missing or
stale source records before handoff; do not create a compiled snapshot or rely on a transcript.
