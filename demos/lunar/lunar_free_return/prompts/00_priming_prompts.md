# Priming Prompts for the current demo project

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

## Mid-Task Reminder

- Write hypotheses before experiments.
- Use numbered phase experiment scripts.
- Capture stdout, stderr, warnings, and tracebacks in `results/logs/`.
- Preserve negative results and state where an approach breaks.
- Link files instead of copying their contents into new context bundles.
