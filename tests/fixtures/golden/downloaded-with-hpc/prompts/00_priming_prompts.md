# Priming Prompts for Golden HPC Study

## Project Start

```text
Read smairt.yaml, prompts/AI_CONTEXT.md, and prompts/CONTEXT_INDEX.md.
Summarize the current research question, active phase, evidence, and unresolved decisions.
```

## Context Refresh

```text
Read the active plan, current hypothesis, its experiment script, recent raw logs, and the
corresponding analysis. Continue from durable project records rather than conversation memory.
```

## Before Writing Code

```text
Read prompts/CODE_CONVENTIONS.md and prompts/KNOWN_PATTERNS.md. Identify the hypothesis,
inputs, expected log, and analysis path before changing an experiment.
```

## Before Interpreting Results

```text
Read the hypothesis, script, complete log, and data provenance. Assess predeclared criteria,
boundaries, limitations, and alternative explanations using analysis/ANALYSIS_TEMPLATE.md.
```

## Before Planning

```text
Read existing plans in plans/ and the most recent analysis files. Propose a plan that
names the hypothesis it serves and the evidence that would settle it.
```

## Mid-Task Reminder

Use when an assistant drifts from the project's conventions mid-session:

```text
SMAIRT reminder:
- Scripts are named script_XX_description.py in the phase directory
- Use TeeLogger from scripts/shared so stdout, stderr, warnings, and tracebacks land
  in results/logs/
- Check prompts/KNOWN_PATTERNS.md before writing code
- Write the hypothesis before the experiment, the analysis after the results
- State where an approach works and where it breaks; negative results are results
- Link files rather than copying their contents into new context
```
