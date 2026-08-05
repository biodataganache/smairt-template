# SMAIRT HPC Guidance Tutorial

HPC support is an optional project capability. It provides a small,
editable SLURM starting point; it does not submit, monitor, or manage jobs.

## Enable The Capability

Create a project with HPC guidance:

```bash
smairt new ./cluster_study \
  --name "Cluster Study" \
  --slug cluster_study \
  --description "A cluster-backed SMAIRT workspace." \
  --researcher "Your Name" \
  --domain "Not sure yet" \
  --phase real \
  --assistant opencode \
  --accept-license \
  --hpc \
  --no-git
```

Or add it to an existing SMAIRT project:

```bash
smairt hpc enable ./cluster_study
```

This creates `hpc/README.md` and `hpc/slurm_job.sh`. The generated script is a
starting point, not an executable cluster configuration.

## Adapt To Your Cluster

Edit `hpc/slurm_job.sh` for your scheduler account, partition, resource
requests, modules, environment activation, paths, and experiment command. Keep
cluster-specific credentials and site policies out of version control as
appropriate. Follow your HPC provider's documented submission procedure, such
as its `sbatch` guidance.

Record durable run output in `results/logs/` and interpret it in `analysis/`.
Keep the standard SMAIRT chain from hypothesis to experiment to raw log to
analysis; the execution environment does not change that responsibility.

## Validate The Workspace

```bash
smairt check ./cluster_study
smairt hpc disable ./cluster_study
```

Project Check diagnoses only SMAIRT structure and configuration. Disabling HPC
changes capability state but never deletes the `hpc/` directory or researcher
files. Re-enable it when needed; modified templates are preserved.
