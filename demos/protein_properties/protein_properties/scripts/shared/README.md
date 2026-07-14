# Shared Library

Reusable code extracted from experiment scripts.

## When to Extract to Shared

Move code here when:
- The same pattern appears in 3+ scripts
- A utility is complex enough to warrant tests
- Multiple team members need the same functionality
- A bug fix needs to propagate to all scripts

## Module Guide

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `logging.py` | Dual console/file logging | `TeeLogger`, `setup_logging` |
| `metrics.py` | Evaluation metrics | *(create when needed)* |
| `data_loading.py` | Data loading utilities | *(create when needed)* |
| `models.py` | Shared model architectures | *(create when needed)* |

## Usage

From any experiment script:

```python
import sys
from pathlib import Path

# Add project root to path (from experiments/XX_phase/)
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.shared import TeeLogger, setup_logging
```

## Adding New Modules

1. Create the module file in `scripts/shared/`
2. Add imports to `__init__.py`
3. Update this README
4. Update `prompts/KNOWN_PATTERNS.md` if the pattern is widely reusable
