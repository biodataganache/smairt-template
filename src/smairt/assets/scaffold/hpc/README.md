# HPC

This directory holds your cluster configuration and job scripts. SMAIRT never
submits, monitors, or cancels a job. Everything here is yours to run.

## Structure

```
hpc/
├── config.yaml           # Your cluster settings, read by your scripts
├── slurm_job.sh          # Safe wrapper that runs whatever command you give it
├── templates/
│   └── slurm_basic.sh    # Starting point for a fuller job script
└── logs/                 # Scheduler output and error logs
```

## Configuration

`config.yaml` records the cluster facts your scripts need in one place, so a
partition or account change is a single edit rather than a search through every
job script. Nothing reads it automatically; wire it into your own scripts.

```yaml
cluster:
  type: slurm  # or pbs, sge
  partition: default
  account: your_account

resources:
  default:
    cpus: 4
    memory: 16G
    time: "4:00:00"

paths:
  scratch: /scratch/$USER
```

## Submitting work

`slurm_job.sh` runs any command you pass it, so one wrapper covers every phase:

```bash
sbatch hpc/slurm_job.sh python3 experiments/01_synthetic/script_01_baseline.py
```

Use `templates/slurm_basic.sh` as a starting point when a job needs more than the
wrapper offers, such as module loads, an environment, or specific resources. Copy
it, do not edit it in place, so the starting point stays clean.

## Practices worth keeping

1. Test locally on a small subset before submitting. Cluster queue time is
   expensive; a shape mismatch found locally costs nothing.
2. Use scratch space for large intermediates and keep evidence you intend to
   interpret in `results/`.
3. Record the job ID alongside the hypothesis it tests, so the audit trail
   survives after the queue forgets.
4. Experiment output still belongs in `results/logs/` through `TeeLogger`.
   `hpc/logs/` holds what the scheduler itself writes, which is a different
   record and useful for a different question.
