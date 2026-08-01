# Real Data Experiments
{% if cookiecutter.starting_phase == 'real' %}
The primary workspace for your experiments with real data.
{% else %}
The final phase: testing on your actual target data.
{% endif %}

## Purpose
{% if cookiecutter.starting_phase == 'real' %}
- Test your hypothesis directly on your target data
- Build up patterns and techniques from real-world observations
- Develop robust approaches where the data itself guides iteration
{% elif cookiecutter.starting_phase == 'downloaded' %}
- Validate whether approaches that worked on benchmark data transfer to your target data
- Test the actual hypothesis with actual target data
- Internal checks become possible
{% else %}
- Validate whether approaches that worked on synthetic and benchmark data transfer
- Test the actual hypothesis with actual target data
- Internal checks become possible
{% endif %}

## Scripts in This Folder

| Script | Data Used | Hypothesis Tested | Result | Date |
|--------|-----------|-------------------|--------|------|
| | | | | |

## Naming Convention

`script_XX_brief_description.py`

## Output Convention

1. Output to console for immediate feedback
2. Output to log file via `TeeLogger`: `../../results/logs/script_XX_description_TIMESTAMP.log`
3. Reference hypothesis file in script docstring (audit trail)
