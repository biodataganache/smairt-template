# Repository Plan

Use this starter to record project-specific organization that goes beyond the standard
SMAIRT scaffold. Do not create a second scientific audit trail.

## Stable Structure

```text
background/                 question and prior evidence
hypotheses/                 testable predictions
plans/                      planned work and decisions
data/{synthetic,downloaded,real}/
experiments/{01_synthetic,02_downloaded,03_real_data}/
results/{logs,figures}/     execution evidence
analysis/                   interpretations and study report
paper/                      optional publication overlay
hpc/                        optional cluster guidance
scripts/shared/             reusable project code
```

## Project Additions

| Path | Purpose | Owner | Naming Rule |
|---|---|---|---|
| [Path] | [Why it exists] | [Person or team] | [Convention] |

## Shared Code

Move code into `scripts/shared/` only when it is reused, complex enough to test, or needs
one fix to propagate across multiple experiments. Record public functions and consumers.

## Git and Collaboration

- Keep one hypothesis, script, log, and analysis chain per tested question.
- Prefer separate files over concurrent edits to one large record.
- Commit complete evidence slices, including useful failed runs.
- Explicitly ignore sensitive or very large artifacts; do not rely on accidental defaults.

## Retirement Record

When replacing a path or convention, record the old path, replacement, reason, and date so
links in historical analyses remain understandable.
