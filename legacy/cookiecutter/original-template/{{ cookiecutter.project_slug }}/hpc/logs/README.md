# HPC Job Logs

{% if cookiecutter.project_mode == 'paper_driven' %}
This directory stores output and error logs from HPC jobs.

## Naming Convention

SLURM automatically names logs with the job ID:
- `{job_id}.out` - Standard output
- `{job_id}.err` - Standard error

## Tips

1. Check `.err` files first when debugging
2. Keep logs for successful runs (useful for paper methods section)
3. Note job IDs in your iteration NOTES.md files
4. Clean up old logs periodically

## Example Log Entry in NOTES.md

```markdown
## HPC Jobs

| Job ID | Script | Status | Runtime |
|--------|--------|--------|---------|
| 12345 | run_analysis_01.py | Success | 2h 15m |
| 12346 | run_analysis_02.py | Failed | 0h 5m |
```
{% else %}
This directory is only used in paper-driven mode.
{% endif %}
