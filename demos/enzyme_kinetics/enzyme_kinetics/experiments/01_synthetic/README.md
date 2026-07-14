# Synthetic Data Experiments

Some questions (not all) might be amenable to experimentation with synthetic
data. This is convenient, especially at the start of the process, because it
makes the scripts self-contained and the data can be synthesized with different
noise levels, and with different types of structures.

## Purpose

- Fast iteration without dependencies
- Test if code works before committing to real data
- Very rapid turnaround time

## Scripts in This Folder

| Script | Hypothesis Tested | Result | Date |
|--------|-------------------|--------|------|
| | | | |

## Naming Convention

`script_XX_brief_description.py`

## Output Convention

1. Output to console for immediate feedback
2. Output to log file via `TeeLogger`: `../../results/logs/script_XX_description_TIMESTAMP.log`
3. Reference hypothesis file in script docstring (audit trail)
