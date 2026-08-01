#!/usr/bin/env bash
#SBATCH --job-name=replace_me
#SBATCH --output=results/logs/%x-%j.out
#SBATCH --error=results/logs/%x-%j.err
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

set -eu

# Load cluster-specific modules and activate the project environment here.
# Replace the command below with one numbered experiment script.
python experiments/01_synthetic/script_01_description.py
