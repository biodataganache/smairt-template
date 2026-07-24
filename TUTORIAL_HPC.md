# SMAIRT HPC Tutorial

A guide to running SMAIRT experiments on High-Performance Computing (HPC) clusters using SLURM.

---

## Overview

Many research projects outgrow a single workstation — training models, sweeping hyperparameters, or processing large datasets often requires cluster resources. SMAIRT's `hpc/` directory provides:

- **SLURM job templates** — Ready-to-customize batch scripts
- **Cluster configuration** — Central place to record your cluster's specifics
- **Job logs** — Structured output that integrates with the audit trail
- **Monitor template** — A script to check job progress from your local machine

This tutorial walks through setting up and using HPC resources within the SMAIRT workflow.

---

## Prerequisites

- A generated SMAIRT project (any mode)
- Access to a SLURM-based HPC cluster
- SSH access and the ability to transfer files (rsync, scp, or shared filesystem)

---

## Step 1: Understand the HPC Directory

```
hpc/
├── config.yaml           # Cluster settings (⚠️ USER-SPECIFIC)
├── templates/
│   └── slurm_basic.sh    # Base SLURM submission template
└── logs/
    └── README.md         # Where job stdout/stderr land
```

All HPC-related configuration lives here, separate from experiment code.

---

## Step 2: Configure Your Cluster

Edit `hpc/config.yaml` with your cluster's details. **Every field marked ⚠️ below is user-specific and must be changed.**

```yaml
# hpc/config.yaml

cluster:
  type: slurm
  partition: gpu              # ⚠️ USER-SPECIFIC: your cluster's partition name
  account: my_lab_allocation  # ⚠️ USER-SPECIFIC: your PI's allocation/account

resources:
  default:
    cpus: 4
    memory: 16G
    time: "4:00:00"
  
  large:
    cpus: 16
    memory: 64G
    time: "12:00:00"
  
  gpu:
    cpus: 8
    memory: 32G
    time: "8:00:00"
    gpus: 1
    gpu_type: a100            # ⚠️ USER-SPECIFIC: v100, a100, h100, etc.

environment:
  # ⚠️ USER-SPECIFIC: path to YOUR conda environment on the cluster
  conda_env: /home/username/miniconda3/envs/smairt_env
  virtualenv: null
  
  # ⚠️ USER-SPECIFIC: modules available on YOUR cluster
  modules:
    - python/3.10
    - cuda/11.8

paths:
  # ⚠️ USER-SPECIFIC: your scratch space
  scratch: /scratch/username
  
  # ⚠️ USER-SPECIFIC: where the project lives on the cluster
  project: /home/username/projects/my_smairt_project

notifications:
  email: you@university.edu   # ⚠️ USER-SPECIFIC
  events:
    - END
    - FAIL
```

### Finding Your Cluster Details

| Setting | How to Find |
|---------|-------------|
| `partition` | Run `sinfo -s` on the cluster |
| `account` | Run `sacctmgr show assoc user=$USER` or ask your sysadmin |
| `modules` | Run `module avail python` and `module avail cuda` |
| `conda_env` | Run `conda env list` |
| `scratch` | Check cluster documentation or `echo $SCRATCH` |

---

## Step 3: Set Up Your Operating Environment

Before submitting jobs, ensure your cluster has the right software. Here's an example session on the cluster:

```bash
# ──────────────────────────────────────────────────────────
# EXAMPLE: Setting up a conda environment on the cluster
# ⚠️ All paths and module names are USER-SPECIFIC
# ──────────────────────────────────────────────────────────

# SSH into your cluster
ssh username@hpc.university.edu          # ⚠️ USER-SPECIFIC

# Load required modules (cluster-specific)
module load python/3.10                  # ⚠️ USER-SPECIFIC: check `module avail`
module load cuda/11.8                    # ⚠️ USER-SPECIFIC: if using GPU

# Create a dedicated conda environment
conda create -n smairt_env python=3.10 -y
conda activate smairt_env

# Install your project's dependencies
pip install numpy pandas matplotlib scikit-learn
pip install torch                         # ⚠️ USER-SPECIFIC: your ML framework

# Verify the environment
python -c "import torch; print(torch.cuda.is_available())"

# Note the environment path for config.yaml
conda env list | grep smairt_env
# Example output: /home/username/miniconda3/envs/smairt_env
```

---

## Step 4: Customize the SLURM Template

The base template at `hpc/templates/slurm_basic.sh` needs your cluster details:

```bash
#!/bin/bash
# ──────────────────────────────────────────────────────────
# SMAIRT SLURM Job Template
# ──────────────────────────────────────────────────────────

#SBATCH --job-name=smairt_job
#SBATCH --output=../../hpc/logs/%j.out
#SBATCH --error=../../hpc/logs/%j.err
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=4:00:00

# ⚠️ USER-SPECIFIC: Uncomment and set YOUR partition and account
#SBATCH --partition=gpu                  # ⚠️ USER-SPECIFIC
#SBATCH --account=my_lab_allocation      # ⚠️ USER-SPECIFIC

# ⚠️ USER-SPECIFIC: Uncomment for GPU jobs
##SBATCH --gres=gpu:1
##SBATCH --constraint=a100               # ⚠️ USER-SPECIFIC: gpu type

# ⚠️ USER-SPECIFIC: Uncomment for email notifications
##SBATCH --mail-user=you@university.edu
##SBATCH --mail-type=END,FAIL

# ─── Environment Setup ───────────────────────────────────
# ⚠️ USER-SPECIFIC: Load YOUR cluster's modules
# module load python/3.10
# module load cuda/11.8

# ⚠️ USER-SPECIFIC: Activate YOUR environment (pick one)
# source /home/username/miniconda3/etc/profile.d/conda.sh
# conda activate smairt_env
#   -- OR --
# source /home/username/venvs/smairt/bin/activate

# ─── Job Execution ───────────────────────────────────────
SCRIPT=$1

if [ -z "$SCRIPT" ]; then
    echo "Usage: sbatch slurm_basic.sh /path/to/script.py"
    exit 1
fi

echo "=========================================="
echo "SLURM Job ID: $SLURM_JOB_ID"
echo "Running on: $(hostname)"
echo "Started at: $(date)"
echo "Script: $SCRIPT"
echo "CPUs: $SLURM_CPUS_PER_TASK"
echo "Memory: $SLURM_MEM_PER_NODE"
echo "=========================================="

# Change to script directory so relative paths work
cd $(dirname $SCRIPT)

# Run the experiment
python $(basename $SCRIPT)

EXIT_CODE=$?

echo "=========================================="
echo "Finished at: $(date)"
echo "Exit code: $EXIT_CODE"
echo "=========================================="

exit $EXIT_CODE
```

### Creating Specialized Templates

For common job types, create additional templates:

```bash
# hpc/templates/slurm_gpu.sh — GPU training jobs
cp hpc/templates/slurm_basic.sh hpc/templates/slurm_gpu.sh
# Edit to uncomment GPU lines, increase memory/time

# hpc/templates/slurm_array.sh — Parameter sweeps
# Add: #SBATCH --array=0-9
```

---

## Step 5: Submit an Experiment

### From Your Local Machine (Shared Filesystem)

If your cluster has a shared filesystem (NFS, Lustre):

```bash
# Navigate to your project
cd /path/to/my_smairt_project

# Submit a specific experiment script
sbatch hpc/templates/slurm_basic.sh experiments/01_synthetic/01_baseline.py

# Submit with resource overrides
sbatch --mem=32G --time=8:00:00 \
    hpc/templates/slurm_basic.sh experiments/02_downloaded/03_validate.py
```

### From a Local Workstation (rsync transfer)

If you develop locally and submit remotely:

```bash
# ⚠️ USER-SPECIFIC: your cluster hostname and project path
CLUSTER="username@hpc.university.edu"
REMOTE_DIR="/home/username/projects/my_smairt_project"

# Sync project to cluster (excluding large data)
rsync -avz --exclude='data/real/' --exclude='.git/' \
    ./ ${CLUSTER}:${REMOTE_DIR}/

# SSH in and submit
ssh ${CLUSTER} "cd ${REMOTE_DIR} && sbatch hpc/templates/slurm_basic.sh experiments/01_synthetic/01_baseline.py"
```

---

## Step 6: Monitor Jobs

### Built-in SLURM Commands

```bash
# Check your running jobs
squeue -u $USER

# Detailed job info
scontrol show job <JOB_ID>

# Watch output in real-time
tail -f hpc/logs/<JOB_ID>.out
```

### SMAIRT Monitor Script

The template at `scripts/monitor_template.py` provides a starting point for automated monitoring:

```python
# Customize scripts/monitor_template.py for your needs
# It can:
# - Check job status via subprocess calls to squeue
# - Parse partial output from hpc/logs/
# - Report progress to the console
```

---

## Step 7: Integrate HPC Logs with the Audit Trail

When jobs complete, their output lands in `hpc/logs/`. To maintain the SMAIRT audit trail:

### Option A: Direct Log Integration

Configure your experiment scripts to write directly to `results/logs/` (recommended):

```python
# In your experiment script, use TeeLogger
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

log_path = setup_logging("script_01_example", PROJECT_ROOT / "results" / "logs")
with TeeLogger(log_path):
    print("This output is displayed and logged")
```

### Option B: Copy HPC Logs After Completion

```bash
# After job 12345 completes:
cp hpc/logs/12345.out results/logs/01_baseline_hpc.log

# Or create a symlink
ln -s ../../hpc/logs/12345.out results/logs/01_baseline_hpc.log
```

### Connecting to Analysis

The audit trail remains:
```
hypotheses/H_01_baseline.md → experiments/01_synthetic/01_baseline.py 
    → results/logs/01_baseline_*.log → analysis/ANALYSIS_01.md
```

The only difference from local runs is *where* the script executes — the logs still feed into the same analysis workflow.

---

## Step 8: Common Patterns

### Parameter Sweeps with SLURM Arrays

```bash
#!/bin/bash
#SBATCH --job-name=sweep
#SBATCH --array=0-9
#SBATCH --output=../../hpc/logs/%A_%a.out

# Each array task gets a different SLURM_ARRAY_TASK_ID
PARAMS=(0.001 0.005 0.01 0.05 0.1 0.5 1.0 5.0 10.0 50.0)
LR=${PARAMS[$SLURM_ARRAY_TASK_ID]}

python experiments/01_synthetic/02_sweep.py --learning-rate $LR
```

### Multi-Node Jobs

```bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=8

# For distributed training (e.g., PyTorch DDP)
srun python experiments/03_real_data/05_distributed_train.py
```

### Recording HPC-Specific Patterns in KNOWN_PATTERNS.md

Add cluster-specific patterns to `prompts/KNOWN_PATTERNS.md`:

```markdown
### 5.5 HPC-Specific Patterns

**Working pattern (SLURM on OurCluster):**
- Partition `gpu` requires `--gres=gpu:1` explicitly
- Jobs >24h must use partition `long`
- `module load cuda/11.8` must come BEFORE conda activate
- Scratch at /scratch/$USER is purged every 30 days

**Known errors:**
- OOM on gpu partition: increase `--mem` (default 16G insufficient for model X)
- "slurmstepd: Exceeded memory limit": reduce batch size or request more memory
```

---

## Example: Complete HPC Workflow

Here's a complete example from hypothesis to HPC submission to analysis:

```bash
# 1. Create hypothesis (local)
#    → hypotheses/H_03_large_scale.md

# 2. Write experiment script (local)  
#    → experiments/02_downloaded/03_large_scale.py
#    Uses TeeLogger, writes to results/logs/

# 3. Submit to cluster
sbatch --partition=gpu --gres=gpu:1 --mem=64G --time=12:00:00 \
    hpc/templates/slurm_basic.sh experiments/02_downloaded/03_large_scale.py

# 4. Monitor
squeue -u $USER
tail -f hpc/logs/<JOB_ID>.out

# 5. After completion, sync results back (if not on shared filesystem)
rsync -avz ${CLUSTER}:${REMOTE_DIR}/results/ ./results/
rsync -avz ${CLUSTER}:${REMOTE_DIR}/hpc/logs/ ./hpc/logs/

# 6. AI reads logs and writes analysis
#    → analysis/ANALYSIS_03.md
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `sbatch: error: Batch job submission failed: Invalid account` | Check `sacctmgr show assoc user=$USER` for valid accounts |
| Job immediately fails | Check `hpc/logs/<JOB_ID>.err` — usually a module or path issue |
| `ModuleNotFoundError` | Ensure conda/venv activation is uncommented in the template |
| Output logs empty | Verify `--output` path exists; `mkdir -p hpc/logs/` on cluster |
| Job pending forever | Try `squeue -u $USER -t PD` and check `scontrol show job` for reason |
| GPU not detected | Ensure `--gres=gpu:1` is set AND the correct CUDA module is loaded |

---

## User-Specific Checklist

Before your first HPC submission, verify:

- [ ] `hpc/config.yaml` — all ⚠️ fields filled with your cluster values
- [ ] `hpc/templates/slurm_basic.sh` — partition, account, modules, environment uncommented
- [ ] Conda/venv on cluster has all project dependencies installed
- [ ] `hpc/logs/` directory exists on the cluster
- [ ] Test with a short job first: `--time=0:05:00` and a simple print script

---

## Tips

- **Start small**: Submit a 5-minute test job before committing to 12-hour runs
- **Use `--mail-type=END,FAIL`** to get notified when jobs finish (especially long ones)
- **Log everything**: TeeLogger + SLURM output files = complete record
- **Record cluster patterns** in `prompts/KNOWN_PATTERNS.md` § 5.5 (HPC-Specific Patterns)
- **Use array jobs** for parameter sweeps instead of submitting many individual jobs
- **Check quotas**: `quota -s` or cluster-specific commands before large runs
