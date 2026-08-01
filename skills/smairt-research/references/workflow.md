# SMAIRT Workflow Reference

## Artifact Map

| Stage | Typical location | Record |
| --- | --- | --- |
| Question/background | `background/` | Question, context, sources, constraints |
| Hypothesis | `hypotheses/HYPOTHESIS_XX.md` | Prediction and success criteria |
| Phase experiment | `experiments/<phase>/script_XX_*.py` | Method, data, parameters, code |
| Results/logs | `results/logs/`, `results/figures/` | Raw output and generated figures |
| Analysis/decision | `analysis/ANALYSIS_XX.md` | Interpretation, limitations, decision |
| Study report | Project report artifact | Supported conclusions and provenance |

Every generated project contains all data and experiment phase directories. The
starting phase records provenance; the current phase identifies the active focus.
Projects do not need to traverse every phase when that would not answer the question.

## Joining A Project

1. Read `smairt.yaml` and `prompts/AI_CONTEXT.md`.
2. Read the current question/background and hypothesis.
3. Inspect the relevant experiment and its raw log before interpreting it.
4. Read the latest analysis/decision and study report.
5. Continue from the recorded state and preserve links between artifacts.

## Experiment Checklist

- Number and describe the script clearly.
- Reference its hypothesis and phase.
- Record data provenance, configuration, dependencies, and seeds where useful.
- Write raw command output to `results/logs/`.
- Do not embed interpretation in place of raw evidence.
- Create an analysis record after execution, not before observing results.

## Optional Paper Overlay

When Paper is enabled, use `paper/outline.md` and `paper/analysis/` to map
accepted project evidence to publication elements. The underlying phase
experiment, raw log, analysis/decision, and study report remain authoritative.
