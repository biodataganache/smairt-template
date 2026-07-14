"""
Shared utilities for this SMAIRT project.

As your project grows, extract common patterns into this shared library.
Typical modules:

- logging.py   — TeeLogger for dual console/file output
- metrics.py   — Evaluation metrics used across experiments
- data_loading.py — Data loading and preprocessing functions
- models.py    — Model architectures shared across scripts

Usage from experiment scripts:
    from scripts.shared import TeeLogger, setup_logging
    from scripts.shared.data_loading import load_data
    from scripts.shared.metrics import compute_score

If import paths are tricky (e.g., from experiments/03_real_data/), add:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
"""

from scripts.shared.logging import TeeLogger, setup_logging

__all__ = [
    "TeeLogger",
    "setup_logging",
]
