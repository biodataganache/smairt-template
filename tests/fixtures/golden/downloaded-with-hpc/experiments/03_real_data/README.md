# Real Data Experiments

The workspace for experiments on your actual target data. Every project carries
this phase, and for most projects it is where the real question gets answered.

## Purpose

- Test the actual hypothesis against the actual target data
- Establish whether approaches that held on synthetic or benchmark data transfer
- Build patterns from real-world observation, where the data guides iteration
- Make internal consistency checks possible, since this is the data you care about

A method that works on synthetic data and fails here has still told you something
precise: the boundary lies between the two. Record where it breaks rather than only
that it broke.

## Scripts in This Folder

| Script | Data Used | Hypothesis Tested | Result | Date |
|--------|-----------|-------------------|--------|------|
| | | | | |

## Naming Convention

`script_XX_brief_description.py`

Create one from the project root, which numbers it for you and wires up logging:

```bash
python3 scripts/new_iteration.py validation real --hypothesis HYPOTHESIS_01
```

The hypothesis is required, not optional. Stating what a script is meant to settle
before writing it is the point of the convention.

## Output Convention

1. Print to the console for immediate feedback.
2. Capture the full run through `TeeLogger`, which writes to
   `results/logs/script_XX_description_TIMESTAMP.log`.
3. Name the hypothesis file in the script docstring. That reference is what makes
   the audit trail followable in both directions.

## Provenance

Real data carries constraints synthetic data does not: licensing, sensitivity, and
sheer size. Record where it came from and under what terms in
`data/real/README.md`, and keep the data itself out of version control unless you
are certain it belongs there.
