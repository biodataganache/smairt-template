# Hypotheses

Track all hypotheses tested throughout the project.

## The 4-Part Structure

The hypothesis is the logical question that is being tested at
this iteration of the process. Each hypothesis is documented using
`HYPOTHESIS_TEMPLATE.md` and connects to the audit trail.

## Files

- `HYPOTHESIS_TEMPLATE.md` - Template for documenting each hypothesis (copy and rename for each new one)
- `H1_*.md`, `H2_*.md`, etc. - Individual hypothesis files, named sequentially

## Naming Convention

```
H1_descriptive_name.md
H2_descriptive_name.md
H3_descriptive_name.md
```

## How Hypotheses Connect (The Audit Trail)

Each hypothesis leads to methods (the code), which produce results (auto-captured by TeeLogger to `results/logs/`), which lead to interpretation and next steps—which feed back into the next hypothesis.

```
hypotheses/H1_*.md → experiments/script_XX_*.py → results/logs/script_XX_*.log → interpretation
```

## Tips

- Write hypotheses **before** running experiments
- Be specific and testable
- Document whether each hypothesis was supported, refuted, or inconclusive
- The "Next Steps" from each hypothesis result seeds the next hypothesis
- Track patterns that emerge across hypotheses in `prompts/KNOWN_PATTERNS.md`
