# Hypotheses

Track every testable hypothesis in a separate file copied from `HYPOTHESIS_TEMPLATE.md`.

## Naming

Use sequential, descriptive names such as `H1_noise_threshold.md` and
`H2_alternative_algorithm.md`.

## Audit Trail

Each hypothesis connects a prediction to methods, evidence, and interpretation:

```text
hypotheses/H1_*.md
  -> experiments/01_synthetic/script_01_*.py
  -> results/logs/script_01_*.log
  -> analysis/ANALYSIS_01.md
```

Write success and rejection criteria before running an experiment. After interpretation,
update the status to supported, refuted, partially supported, or inconclusive. Preserve
failed hypotheses and dead ends because they constrain future work.

Use next steps from one analysis to motivate the next hypothesis. Record patterns that
apply across experiments in `prompts/KNOWN_PATTERNS.md`.
