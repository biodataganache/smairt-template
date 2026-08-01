# Code Conventions for This Project

When generating code for this project, follow these conventions.

---

## Script Naming

### Sequential Numbering (Early Project)

Use numbered scripts for each iteration:

```
script_XX_brief_description.py
```

Examples:
- `script_01_initial_synthetic_test.py`
- `script_02_add_noise_robustness.py`
- `script_03_iris_benchmark.py`

### Track-Based Naming (Mature Project)

When the project forks into parallel investigations, use letter-prefixed tracks:

```
script_[TRACK][NN]_brief_description.py
```

Examples:
- `script_A01_baseline_method.py` — Track A: Core approach
- `script_B01_alternative_data_exploration.py` — Track B: Alternative data source
- `script_C31_pretraining_baseline.py` — Track C: Pretraining strategy
- `script_D01_fusion_baseline.py` — Track D: Multi-source fusion
- `script_X1_embedding_dynamics.py` — Track X: Interpretation & diagnostics

Track assignments should be documented in `plans/`.

### HPC Scripts

Scripts designed for HPC execution append `_hpc`:

```
script_D06_hpc.py
script_E03_hpc.py
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
results/logs/script_B05_multi_source_20240220_091544.log
```

The `setup_logging()` function handles this automatically.

---

## Directory Conventions

Place scripts in the appropriate phase directory:
{% if cookiecutter.starting_phase == 'synthetic' %}
```
experiments/
├── 01_synthetic/          # Phase 1: Synthetic data tests
│   ├── script_01_xxx.py
│   └── script_02_xxx.py
├── 02_downloaded/         # Phase 2: Benchmark data tests
│   ├── script_03_xxx.py
│   └── script_04_xxx.py
├── 03_real_data/          # Phase 3: Real data tests
│   ├── script_05_xxx.py
│   ├── script_B01_xxx.py  # Track B starts here
│   └── script_D01_xxx.py  # Track D starts here
└── interpretation/        # Interpretation & diagnostics scripts (Track X)
    └── script_X1_xxx.py
```
{% elif cookiecutter.starting_phase == 'downloaded' %}
```
experiments/
├── 02_downloaded/         # Phase 1: Benchmark data tests
│   ├── script_01_xxx.py
│   └── script_02_xxx.py
├── 03_real_data/          # Phase 2: Real data tests
│   ├── script_03_xxx.py
│   ├── script_B01_xxx.py  # Track B starts here
│   └── script_D01_xxx.py  # Track D starts here
└── interpretation/        # Interpretation & diagnostics scripts (Track X)
    └── script_X1_xxx.py
```
{% elif cookiecutter.starting_phase == 'real' %}
```
experiments/
├── 03_real_data/          # All experiments go here
│   ├── script_01_xxx.py
│   ├── script_02_xxx.py
│   ├── script_B01_xxx.py  # Track B
│   └── script_D01_xxx.py  # Track D
└── interpretation/        # Interpretation & diagnostics scripts (Track X)
    └── script_X1_xxx.py
```
{% endif %}

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
hpc/script_D06_hpc.csh
hpc/script_E03_hpc.csh
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
