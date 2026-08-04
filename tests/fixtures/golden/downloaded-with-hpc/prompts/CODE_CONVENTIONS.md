# Code Conventions for This Project

When generating code for this project, follow these conventions.

---

## Script Naming

Every numbered script is an iteration, created by `scripts/new_iteration.py`:

```
script_NN_brief_description.py
```

Examples:
- `script_01_initial_synthetic_test.py`
- `script_02_add_noise_robustness.py`
- `script_03_iris_benchmark.py`

Numbering is sequential across the whole project rather than per phase or per track, so
the filenames read as the order the work happened. The helper assigns the number, because
two things handing out numbers independently would eventually hand out the same one.

### Tracks are recorded, not encoded in filenames

A track is a direction of inquiry spanning as many iterations as it takes. Several tracks
can be in flight at once, and an iteration belongs to one of them — but the track is
recorded in `analysis/ANALYSIS_PLAN.md` and in the iteration's hypothesis, not in the
script's name.

Naming a script for its track would fork the numbering, and a fork means the numbers no
longer order the work. It also hides iterations from the helpers, which find them by
number.

### Utilities

Code that supports the research without testing anything — a downloader, a figure
regenerator — is not an iteration. Create it with `scripts/new_utility.py`, which writes to
`scripts/utilities/` and takes no number.

### HPC Scripts

An iteration that runs on a cluster keeps its number and appends `_hpc`:

```
script_06_hpc.py
```

---

## Required Output Format

Every script should:

1. **Print to console** for immediate feedback
2. **Write to log file** using `TeeLogger` from `scripts/shared/logging`
3. **Include hypothesis in docstring** for the audit trail

---

## Script Template

```python
#!/usr/bin/env python3
"""
Script XX: Brief description of what this script tests

Hypothesis: HYPOTHESIS_XX.md
Phase: synthetic / downloaded / real
Track: [A/B/C/D/...] (if applicable)
Iteration: [X]

Depends on:
  - [list prior scripts or data this builds on]
"""

import sys
from pathlib import Path
from datetime import datetime

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

# === CONFIGURATION ===
SCRIPT_NAME = "script_XX_description"
LOG_DIR = PROJECT_ROOT / "results" / "logs"

# === MAIN CODE ===
def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Script: {SCRIPT_NAME}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: [State hypothesis here]")
        print(f"{'='*60}")
        print()

        # ========================================
        # YOUR CODE HERE
        # ========================================



        # ========================================
        # END YOUR CODE
        # ========================================

        print()
        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
```

---

## The Audit Trail

Every experiment produces a complete audit trail across multiple files:

| Artifact | Location | Purpose |
|----------|----------|---------|
| Hypothesis | `hypotheses/HYPOTHESIS_XX.md` | What we predict and why |
| Script | `experiments/XX_phase/script_XX_*.py` | What code was run |
| Log file | `results/logs/script_XX_*.log` | Raw output |
| Analysis | `analysis/ANALYSIS_XX.md` | Interpretation & next steps |

This replaces the legacy "paste output as comments" pattern. The AI reads log
files directly — no need to copy output into scripts.

---

## Using the Shared Library

Extract common code to `scripts/shared/` when patterns repeat across 3+ scripts:

```python
# Import shared utilities
from scripts.shared import TeeLogger, setup_logging
from scripts.shared.data_loading import load_data
from scripts.shared.metrics import compute_score
```

See `scripts/shared/README.md` for guidance on when and how to extract code.

---

## Log File Naming

Log files go in `results/logs/` and include timestamps for uniqueness:

```
results/logs/script_01_initial_test_20240115_143022.log
results/logs/script_05_multi_source_20240220_091544.log
```

The `setup_logging()` function handles this automatically.

---

## Directory Conventions

Place scripts in the appropriate phase directory:
```
experiments/
├── 01_synthetic/          # Phase 1: Synthetic data tests
│   ├── script_01_xxx.py
│   └── script_02_xxx.py
├── 02_downloaded/         # Phase 2: Benchmark data tests
│   ├── script_03_xxx.py
│   └── script_04_xxx.py
└── 03_real_data/          # Phase 3: Real data tests
    ├── script_05_xxx.py
    └── script_06_xxx.py
```

Numbering continues across phases, so a script's number says when it happened and its
directory says what data it used.

---

## Data Validation

Include data validation checks where appropriate:

```python
# Validate input data
assert data is not None, "Data failed to load"
assert len(data) > 0, "Data is empty"
print(f"Loaded {len(data)} samples")
print(f"Data shape: {data.shape}")
```

---

## Documenting Limitations

When results show limited success, document where and why:

```python
# === LIMITATIONS OBSERVED ===
# - Works on synthetic data up to X% accuracy
# - Breaks down when noise > Y%
# - Not robust to Z
# - Works within certain boundaries but breaks down under specific conditions
```

---

## Recording Patterns & Errors

### When to Add a Pattern

After solving a non-trivial coding problem, add the working pattern to
`prompts/KNOWN_PATTERNS.md`:
- Data loading approaches that work
- API call configurations
- Model initialization patterns

### When to Add an Error

After resolving a bug that cost significant time, add it to
`prompts/KNOWN_PATTERNS.md`:
- What happened (error message)
- Impact (time lost, wrong results, etc.)
- The fix
- Prevention strategy

---

## HPC Conventions

### Device-Agnostic Code

Scripts that may run on HPC should support CPU/GPU switching via configuration:

```python
CONFIG = {
    "hardware": {
        "accelerator": "gpu",    # "gpu", "cpu", "auto"
        "devices": 1,            # 1, 4, "auto"
        "precision": "32-true",  # "32-true", "bf16-mixed"
    },
    "training": {
        "max_epochs": 100,
        "batch_size": 64,
    }
}
```

### SLURM Job Scripts

Place in `hpc/` with naming matching the experiment script:

```
hpc/script_06_hpc.csh
```

### Monitor Scripts

For long-running HPC jobs, create companion monitor scripts:

```python
# scripts/monitor_XX_progress.py
# Reads partial results and reports progress
```

---

## The 4-Part Structure in Code

Remember that each script is part of the 4-part structure:

1. **Background** → documented in `background/` folder and hypothesis file
2. **Hypothesis** → stated in script docstring, detailed in `hypotheses/HYPOTHESIS_XX.md`
3. **Methods** → the script itself (code + data)
4. **Results** → the log file output + `analysis/ANALYSIS_XX.md`
