# HPC Configuration

{% if cookiecutter.project_mode == 'paper_driven' %}
This directory contains configuration for running analyses on HPC clusters.

## Structure

```
hpc/
├── config.yaml         # HPC settings
├── templates/          # Job script templates
│   ├── slurm_basic.sh
│   └── slurm_gpu.sh
└── logs/               # Job logs
```

## Configuration

Edit `config.yaml` with your cluster settings:

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
  
  gpu:
    cpus: 8
    memory: 32G
    time: "8:00:00"
    gpus: 1

paths:
  scratch: /scratch/$USER
  conda_env: /path/to/conda/env
```

## Usage

Submit jobs using the helper script:

```bash
python scripts/submit_job.py --script analysis/01_*/iterations/iter_01/run_analysis_01.py
```

Or manually:

```bash
sbatch hpc/templates/slurm_basic.sh analysis/01_*/iterations/iter_01/run_analysis_01.py
```

## Tips

1. Always test locally first with a small data subset
2. Use scratch space for large intermediate files
3. Log job IDs in your NOTES.md for each iteration
4. Check logs in `hpc/logs/` for debugging
{% else %}
This directory is only used in paper-driven mode.
{% endif %}
