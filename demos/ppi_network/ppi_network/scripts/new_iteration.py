#!/usr/bin/env python
"""
Create a new iteration for an existing analysis.

Usage:
    python scripts/new_iteration.py --analysis 01_results/01_analysis --iteration 02

This creates:
    analysis/{analysis}/iterations/iter_{iteration}/
    ├── NOTES.md
    ├── config_{iteration}.yaml
    ├── results/
    └── figures/

If a previous iteration exists, copies the config file as a starting point.
"""

import argparse
from pathlib import Path
from datetime import datetime
import shutil

NOTES_TEMPLATE = '''# Iteration {iteration} Notes

## Date
{date}

## Changes from Previous
- [List what changed from iteration {prev_iteration}]

## Configuration
```yaml
# Key parameters changed
# See config_{iteration}.yaml for full config
```

## Results
- [Key metrics and findings]

## Observations
- [What worked well]
- [What didn't work]
- [Unexpected findings]

## Decision
[ACCEPT/REVISE/ABANDON] - [Rationale]

## Next Steps
- [If REVISE, what to try in next iteration]
'''


def create_iteration(analysis: str, iteration: str):
    """Create a new iteration for an existing analysis."""
    base = Path(f"analysis/{analysis}/iterations/iter_{iteration}")
    date = datetime.now().strftime("%Y-%m-%d")
    prev_iter = int(iteration) - 1
    
    # Check if analysis exists
    analysis_dir = Path(f"analysis/{analysis}")
    if not analysis_dir.exists():
        print(f"ERROR: Analysis directory does not exist: {analysis_dir}")
        print("Use scripts/new_experiment.py to create a new analysis first.")
        return
    
    # Check if iteration already exists
    if base.exists():
        print(f"ERROR: Iteration already exists: {base}")
        return
    
    # Create directories
    (base / "results").mkdir(parents=True)
    (base / "figures").mkdir(parents=True)
    
    # Create NOTES.md
    (base / "NOTES.md").write_text(
        NOTES_TEMPLATE.format(
            iteration=iteration,
            prev_iteration=f"{prev_iter:02d}",
            date=date
        )
    )
    
    # Copy previous iteration's config as starting point
    prev_config = base.parent / f"iter_{prev_iter:02d}" / f"config_{prev_iter:02d}.yaml"
    new_config = base / f"config_{iteration}.yaml"
    
    if prev_config.exists():
        shutil.copy(prev_config, new_config)
        print(f"✓ Copied previous config as starting point")
    else:
        # Create empty config
        new_config.write_text(f"# Configuration for iteration {iteration}\n# Created: {date}\n\nseed: 1024\n")
    
    # Copy previous iteration's script as starting point
    prev_script = base.parent / f"iter_{prev_iter:02d}" / f"run_analysis_{prev_iter:02d}.py"
    new_script = base / f"run_analysis_{iteration}.py"
    
    if prev_script.exists():
        shutil.copy(prev_script, new_script)
        print(f"✓ Copied previous script as starting point")
    
    print(f"✓ Created iteration: {base}")
    print()
    print("Next steps:")
    print(f"  1. Edit {new_config} with parameter changes")
    if new_script.exists():
        print(f"  2. Edit {new_script} with code changes")
    else:
        print(f"  2. Create {new_script}")
    print(f"  3. Run analysis and update {base}/NOTES.md")
    print(f"  4. Update iterations/ITERATION_LOG.md with results")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a new iteration for an existing analysis"
    )
    parser.add_argument(
        "--analysis",
        required=True,
        help="Path to analysis (e.g., 01_section/01_analysis)"
    )
    parser.add_argument(
        "--iteration",
        required=True,
        help="Iteration number (e.g., 02, 03)"
    )
    args = parser.parse_args()
    
    create_iteration(args.analysis, args.iteration)
