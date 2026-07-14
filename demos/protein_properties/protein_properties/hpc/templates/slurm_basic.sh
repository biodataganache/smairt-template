#!/bin/bash
#SBATCH --job-name=smairt_job
#SBATCH --output=../../hpc/logs/%j.out
#SBATCH --error=../../hpc/logs/%j.err
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=4:00:00
{% if cookiecutter.project_mode == 'paper_driven' %}
# SMAIRT Paper-Driven Mode - Basic SLURM Template
# 
# Usage:
#   sbatch slurm_basic.sh /path/to/script.py
#
# Or with custom resources:
#   sbatch --cpus-per-task=8 --mem=32G slurm_basic.sh /path/to/script.py

# Get the script to run
SCRIPT=$1

if [ -z "$SCRIPT" ]; then
    echo "Usage: sbatch slurm_basic.sh /path/to/script.py"
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

# Change to script directory
cd $(dirname $SCRIPT)

# Run the script
python $(basename $SCRIPT)

# Print completion info
echo "=========================================="
echo "Finished at: $(date)"
echo "=========================================="
{% else %}
# This template is only used in paper-driven mode
echo "Paper-driven mode not enabled"
{% endif %}
