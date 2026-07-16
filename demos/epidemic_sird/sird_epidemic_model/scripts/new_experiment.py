#!/usr/bin/env python
"""
Create a new experiment directory for paper-driven SMAIRT project.

Usage:
    python scripts/new_experiment.py --section 01 --name initial_analysis

This creates:
    analysis/{section}_{name}/
    ├── README.md
    ├── hypotheses.md
    └── iterations/
        ├── ITERATION_LOG.md
        └── iter_01/
            ├── NOTES.md
            ├── results/
            └── figures/
"""

import argparse
from pathlib import Path
from datetime import datetime

README_TEMPLATE = '''# {name}

## Purpose
[What question does this analysis answer?]

## Hypothesis
[What do we expect to find?]

## Data
- Input: [data files]
- Annotations: [annotation files if any]

## Methods
[Brief description of approach]

## Outputs
- `results/` - [description of results]
- `figures/` - [description of figures]

## Status
- [x] Not started
- [ ] In progress
- [ ] Complete

## Final Iteration
[To be filled when complete - which iteration was selected and why]
'''

HYPOTHESES_TEMPLATE = '''# Hypotheses for {name}

## Primary Hypothesis

**H1**: [State your primary hypothesis]

- **Rationale**: [Why do you expect this?]
- **Test**: [How will this be tested?]
- **Success criteria**: [What metrics/thresholds indicate success?]

## Secondary Hypotheses

**H2**: [Additional hypothesis if any]

- **Rationale**: 
- **Test**: 
- **Success criteria**: 

## Null Hypotheses

**H0**: [What would indicate no effect/relationship?]
'''

ITERATION_LOG_TEMPLATE = '''# Iteration Log

## Analysis: {name}

| Iter | Date | Description | Key Change | Metrics | Decision |
|------|------|-------------|------------|---------|----------|
| 01 | {date} | Initial implementation | Baseline | TBD | TBD |

## Decision Key
- **ACCEPT**: Metrics meet targets, results stable and interpretable
- **REVISE**: Promising but needs parameter tuning
- **ABANDON**: Fundamental issue, try different approach
'''

NOTES_TEMPLATE = '''# Iteration 01 Notes

## Date
{date}

## Changes from Previous
- Initial implementation

## Configuration
```yaml
# Key parameters used
seed: 1024
# Add other parameters
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

CONFIG_TEMPLATE = '''# Configuration for {name} - Iteration 01
# Created: {date}

# Random seed for reproducibility
seed: 1024

# Data paths
data:
  input: "../../data/"
  output: "results/"

# Analysis parameters
# Add your parameters here

# Output settings
output:
  figures_dir: "figures/"
  results_dir: "results/"
  save_formats: ["png", "pdf", "svg"]
'''


def create_experiment(section: str, name: str):
    """Create a new experiment directory structure."""
    base = Path(f"analysis/{section}_{name}")
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Check if already exists
    if base.exists():
        print(f"ERROR: Directory already exists: {base}")
        return
    
    # Create directories
    (base / "iterations" / "iter_01" / "results").mkdir(parents=True)
    (base / "iterations" / "iter_01" / "figures").mkdir(parents=True)
    (base / "final" / "results").mkdir(parents=True)
    (base / "final" / "figures").mkdir(parents=True)
    
    # Create files
    (base / "README.md").write_text(README_TEMPLATE.format(name=name))
    (base / "hypotheses.md").write_text(HYPOTHESES_TEMPLATE.format(name=name))
    (base / "iterations" / "ITERATION_LOG.md").write_text(
        ITERATION_LOG_TEMPLATE.format(name=name, date=date)
    )
    (base / "iterations" / "iter_01" / "NOTES.md").write_text(
        NOTES_TEMPLATE.format(date=date)
    )
    (base / "iterations" / "iter_01" / "config_01.yaml").write_text(
        CONFIG_TEMPLATE.format(name=name, date=date)
    )
    
    print(f"✓ Created experiment: {base}")
    print()
    print("Next steps:")
    print(f"  1. Edit {base}/README.md with analysis details")
    print(f"  2. Edit {base}/hypotheses.md with your hypotheses")
    print(f"  3. Create {base}/iterations/iter_01/run_analysis_01.py")
    print(f"  4. Run your analysis and update NOTES.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a new experiment directory for paper-driven SMAIRT"
    )
    parser.add_argument(
        "--section", 
        required=True,
        help="Section number (e.g., 01, 02)"
    )
    parser.add_argument(
        "--name", 
        required=True,
        help="Experiment name (use underscores, no spaces)"
    )
    args = parser.parse_args()
    
    create_experiment(args.section, args.name)
