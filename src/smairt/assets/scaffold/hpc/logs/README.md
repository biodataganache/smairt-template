# HPC Job Logs

This directory stores output and error logs from HPC jobs.

## Naming Convention

SLURM automatically names logs with the job ID:
- `{job_id}.out` - Standard output
- `{job_id}.err` - Standard error

These are the scheduler's own records. Your experiment output still goes to
`results/logs/` through `TeeLogger`, which is the evidence you interpret. Look here
when a job never got far enough to write one.

## Tips

1. Check `.err` files first when debugging. A job that fails before your script
   runs leaves nothing in `results/logs/` at all.
2. Keep logs for successful runs; they carry the resources and runtime a methods
   section needs.
3. Record job IDs next to the hypothesis being tested, in the relevant
   `hypotheses/` or `analysis/` file, so the trail survives the queue.
4. Clean up old logs periodically. Nothing here is managed for you.

## Recording jobs alongside a hypothesis

```markdown
## HPC Jobs

| Job ID | Script | Status | Runtime |
|--------|--------|--------|---------|
| 12345 | experiments/01_synthetic/script_01_baseline.py | Success | 2h 15m |
| 12346 | experiments/01_synthetic/script_02_variant.py | Failed | 0h 5m |
```
