#!/bin/bash
#SBATCH --job-name=smairt_job
#SBATCH --output=hpc/logs/%j.out
#SBATCH --error=hpc/logs/%j.err
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=4:00:00
# Basic SLURM template. Copy it rather than editing it in place, so this starting
# point stays clean for the next job. Submit from the project root.
#
# Usage:
#   sbatch hpc/templates/slurm_basic.sh experiments/01_synthetic/script_01_baseline.py
#
# Or with custom resources:
#   sbatch --cpus-per-task=8 --mem=32G hpc/templates/slurm_basic.sh <script>

# Get the script to run
SCRIPT=$1

if [ -z "$SCRIPT" ]; then
    echo "Usage: sbatch hpc/templates/slurm_basic.sh <script>"
    exit 1
fi

# Print job info
echo "=========================================="
echo "SLURM Job ID: $SLURM_JOB_ID"
echo "Running on: $(hostname)"
echo "Started at: $(date)"
echo "Script: $SCRIPT"
echo "=========================================="

# Load modules (uncomment and modify as needed)
# module load python/3.10

# Activate environment (uncomment one)
# source /path/to/venv/bin/activate
# conda activate myenv

# Run the script from the project root, so its own paths resolve and TeeLogger
# writes to results/logs/ as it does for a local run.
python3 "$SCRIPT"

# Print completion info
echo "=========================================="
echo "Finished at: $(date)"
echo "=========================================="
