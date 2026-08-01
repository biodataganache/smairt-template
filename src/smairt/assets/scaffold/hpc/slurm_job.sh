#!/usr/bin/env bash
#SBATCH --job-name={{ project.slug }}
#SBATCH --output=results/logs/%x-%j.out
#SBATCH --error=results/logs/%x-%j.err

set -eu

if [ "$#" -eq 0 ]; then
  echo "Usage: sbatch hpc/slurm_job.sh <experiment-command> [arguments...]" >&2
  echo "Choose a command and paths appropriate for the current project phase." >&2
  exit 2
fi

"$@"
