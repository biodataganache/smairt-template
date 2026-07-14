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
| `script_01_bh_correction.py` | `H1_bh_correction_baseline.md` | Partially Supported (Recall: 36.0%, FDR: 2.70%) | 2026-06-30 |
| `script_02_parameter_sweep.py` | `H2_parameter_sweep.md` | Supported (Mapped design envelopes for $\ge 70\%$ recall) | 2026-06-30 |
| `script_03_missingness_heteroscedasticity.py` | `H3_missingness_heteroscedasticity.md` | Partially Supported (Heteroscedasticity destroys power; filtering outperforms MinDet) | 2026-06-30 |

## Naming Convention

`script_XX_brief_description.py`

## Output Convention

1. Output to console for immediate feedback
2. Output to log file via `TeeLogger`: `../../results/logs/script_XX_description_TIMESTAMP.log`
3. Reference hypothesis file in script docstring (audit trail)
