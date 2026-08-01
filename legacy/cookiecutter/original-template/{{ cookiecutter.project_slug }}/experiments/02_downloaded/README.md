# Downloaded Benchmark Data Experiments
{% if cookiecutter.starting_phase == 'downloaded' %}
The starting workspace for your experiments with established benchmark data.
{% endif %}

## Purpose
{% if cookiecutter.starting_phase == 'downloaded' %}
- Start with well-characterized benchmark data to validate your approach
- Establish baselines that others have examined before
- Diversity: easy data, hard data, messy experimental data, cleaner data
- Build confidence before moving to your target (real) data
{% else %}
This phase provides:
- Data that many people have looked at before
- Diversity: easy data, hard data, messy experimental data, cleaner data
- A nice range of things to test on
- Validation that your approach is robust across different datasets
{% endif %}

For fundamental algorithm development, testing across datasets from different disciplines demonstrates robustness and generalizability.

## Scripts in This Folder

| Script | Dataset Used | Hypothesis Tested | Result | Date |
|--------|--------------|-------------------|--------|------|
| | | | | |

## Naming Convention

`script_XX_brief_description.py`

## Output Convention

1. Output to console for immediate feedback
2. Output to log file via `TeeLogger`: `../../results/logs/script_XX_description_TIMESTAMP.log`
3. Reference hypothesis file in script docstring (audit trail)
