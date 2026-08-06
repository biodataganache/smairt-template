# Hypothesis [XX] - [Brief Title]

## Status

PENDING | SUPPORTED | REFUTED | PARTIALLY SUPPORTED | INCONCLUSIVE

## Background

[What question or prior result motivates this hypothesis? Link the relevant background,
analysis, or experiment records.]

## Hypothesis Statement

**Prediction**: [State a specific, testable prediction.]

**Rationale**: [Explain why the available evidence makes this prediction plausible.]

**Alternative explanations**: [List other mechanisms that could produce the same observation.]

**Success criteria**: [Define quantitative or qualitative criteria before running the test.]

**Rejection criteria**: [Define evidence that would refute or materially weaken the hypothesis.]

Both criteria belong here before any experiment script exists. A criterion written after
the data is a rationalization.

## Experimental Design

- **Phase**: synthetic | downloaded | real
- **Data**: [Inputs and provenance record]
- **Controls**: [Baselines, negative controls, or comparison methods]
- **Key metrics**: [Measurements and uncertainty estimates]
- **Randomness**: [Seeds, repetitions, or sampling plan]

## Sub-Hypotheses

Use these when a panel iteration probes several directions at once, one entry per probe.

### HYPOTHESIS_XXA: [First sub-prediction]

- **Prediction**: [Specific outcome]
- **Success criteria**: [Measurable threshold]

### HYPOTHESIS_XXB: [Second sub-prediction]

- **Prediction**: [Specific outcome]
- **Success criteria**: [Measurable threshold]

## Dependencies

- [Prior iteration, analysis, or result]
- [Data that must be available]
- [Shared functions or computing resources]

## Iterations

Several iterations usually test one hypothesis, so this is where they accumulate. The
iteration numbers and this hypothesis number are deliberately separate: iteration 07 may
well be testing hypothesis 02.

| Iteration | What it tested | Outcome |
|---|---|---|

## Results

Complete this after interpreting. Link the raw log, figures, and corresponding
`analysis/ANALYSIS_XX.md` interpretation rather than copying output into this file.

## Notes

[Record caveats, decisions, or changes made before execution.]
