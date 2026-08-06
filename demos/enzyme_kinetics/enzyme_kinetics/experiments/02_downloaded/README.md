# Downloaded Benchmark Data Experiments

The workspace for experiments on established benchmark data. Every project carries
this phase, whether or not the work started here.

## Purpose

- Establish baselines on data others have examined, so your result has something
  to be compared against
- Test across a deliberate range: easy and hard, clean and messy
- Show that an approach is robust across datasets rather than tuned to one
- Build confidence before committing effort to your target data

For fundamental algorithm development, testing across datasets from different
disciplines is what demonstrates generalizability rather than asserting it.

If the project started at a later phase, this directory stays available. Working
backwards into benchmark data is a legitimate move when a real-data result is
ambiguous and you need a case with a known answer.

## Scripts in This Folder

| Script | Dataset Used | Hypothesis Tested | Result | Date |
|--------|--------------|-------------------|--------|------|
| | | | | |

## Naming Convention

`script_XX_brief_description.py`

Create one from the project root, which numbers it for you and wires up logging:

```bash
python3 scripts/new_iteration.py baseline downloaded --hypothesis HYPOTHESIS_01
```

The hypothesis is required, not optional. Stating what a script is meant to settle
before writing it is the point of the convention.

## Output Convention

1. Print to the console for immediate feedback.
2. Capture the full run through `TeeLogger`, which writes to
   `results/logs/script_XX_description_TIMESTAMP.log`.
3. Name the hypothesis file in the script docstring. That reference is what makes
   the audit trail followable in both directions.
