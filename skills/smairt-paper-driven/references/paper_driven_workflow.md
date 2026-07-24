# SMAIRT Paper-Driven Workflow Reference

## Iteration structure

Each analysis section uses a strict iteration pattern:

```text
analysis/01_first_analysis/
├── README.md               # What question this answers, which paper section
├── hypotheses.md           # What we expect to find
├── iterations/
│   ├── ITERATION_LOG.md    # Decision table (see format below)
│   ├── iter_01/
│   │   ├── config_01.yaml  # Parameters
│   │   ├── run_analysis_01.py  # Script (uses TeeLogger)
│   │   ├── results/        # Output data
│   │   ├── figures/        # Plots
│   │   └── NOTES.md        # Observations + ACCEPT/REVISE decision
│   └── iter_02/
│       └── ...
└── final/
    ├── SELECTED.md          # Which iteration chosen + rationale
    ├── results/             # Accepted output
    └── figures/             # Accepted figures
```

## ITERATION_LOG.md format

```markdown
# Iteration Log: [Analysis Name]

| Iter | Date | Description | Key Change | Metrics | Decision |
|------|------|-------------|------------|---------|----------|
| 01 | YYYY-MM-DD | Baseline | Initial | [metrics] | Revise |
| 02 | YYYY-MM-DD | [change] | [what changed] | [metrics] | **ACCEPT** |
```

## Config format (YAML)

```yaml
seed: 1024

data:
  input: "../../../../data/dataset_name/processed/data.csv"
  # Use relative paths from the iteration directory

parameters:
  threshold: 0.5
  method: "approach_a"
  n_iterations: 100

output:
  results_dir: "results/"
  figures_dir: "figures/"
```

## Script template (paper-driven)

```python
#!/usr/bin/env python3
"""
Analysis: 01_first_analysis
Iteration: 01
Hypothesis: [What we expect this to show]
Paper Section: Results 3.1, Figure 1
"""

import sys
from pathlib import Path
from datetime import datetime

# === PATH SETUP ===
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging
from lib.core.utils import load_config, set_seed, save_results
from lib.visualization.style import setup_plot_style, save_figure

# === CONFIGURATION ===
SCRIPT_NAME = "run_analysis_01_iter01"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
config = load_config(Path(__file__).parent / 'config_01.yaml')
set_seed(config.get('seed', 1024))

# === MAIN CODE ===
def main():
    log_path = setup_logging(SCRIPT_NAME, LOG_DIR)

    with TeeLogger(log_path):
        print(f"{'='*60}")
        print(f"Analysis: 01_first_analysis | Iteration: 01")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Hypothesis: [state it here]")
        print(f"{'='*60}")
        print()

        setup_plot_style()

        # Load data
        # data = load_data(config['data']['input'])

        # Run analysis
        # results = analyze(data, **config['parameters'])

        # Save results
        results = {'metric_a': 0.0}
        save_results(results, 'results/metrics.json')

        # Create figures
        # fig = create_figure(results)
        # save_figure(fig, 'figures/fig_01_comparison')

        print(f"\nResults: {results}")
        print(f"{'='*60}")
        print("=== COMPLETE ===")

if __name__ == "__main__":
    main()
```

## NOTES.md template

```markdown
# Iteration XX Notes

## Date
YYYY-MM-DD

## Changes from Previous
- [What changed from the last iteration]

## Results
- metric_a: [value]
- metric_b: [value]

## Observations
- [What you noticed]
- [Unexpected findings]

## Decision
[ACCEPT / REVISE]

## Rationale
[Why this decision]

## Next Steps (if REVISE)
- [What to change next]
```

## SELECTED.md template

```markdown
# Selected Iteration

**Selected**: iter_XX
**Date**: YYYY-MM-DD

## Rationale
[Why this iteration was chosen over others]

## Key Metrics
| Metric | Value |
|--------|-------|
| metric_a | [value] |
| metric_b | [value] |

## Paper Element
- Figure X in Results Section Y
- Table Z in Results Section Y

## Reproducibility
- Config: `iterations/iter_XX/config_XX.yaml`
- Script: `iterations/iter_XX/run_analysis_XX.py`
- Log: `results/logs/run_analysis_XX_iter_XX_YYYYMMDD_HHMMSS.log`
```

## FINAL_MANIFEST.md format

```markdown
# Final Manifest

## Summary

| Paper Element | Analysis | Iteration | Figure/Table | Status |
|---------------|----------|-----------|--------------|--------|
| Figure 1 | 01_first_analysis | iter_02 | fig_01_comparison.pdf | ✓ |
| Table 1 | 01_first_analysis | iter_02 | table_01.csv | ✓ |
| Figure 2 | 02_second_analysis | iter_03 | fig_02_results.pdf | ✓ |

## Reproduction Steps

To reproduce all results:
1. Install dependencies: `pip install -r requirements.txt`
2. Run analyses in order: [list scripts]
3. Final figures are in `analysis/XX_figures/`
```

## Revision plan format

For projects starting from reviewer feedback:

```markdown
# Revision Plan

## Manuscript
- Submitted: paper/drafts/submitted_v1.md
- Decision: Major/Minor revision

## Priority 1: New Analyses Required

| # | Reviewer | Comment | Analysis Section | Expected Output | Iterations |
|---|----------|---------|-----------------|-----------------|------------|
| 1 | R2.3 | "Need statistical test" | 03_stat_test | Table 2 (revised) | 1-2 |
| 2 | R1.5 | "Additional dataset" | 04_extra_data | Fig 4 (new) | 2-3 |

## Priority 2: Reanalysis / Revised Figures

| # | Reviewer | Comment | Analysis Section | Expected Output |
|---|----------|---------|-----------------|-----------------|
| 3 | R1.2 | "Error bars missing" | 01 (rerun) | Fig 1-3 (revised) |

## Priority 3: Writing Only

| # | Reviewer | Comment | Section | Action |
|---|----------|---------|---------|--------|
| 4 | R2.1 | "Methods unclear" | Methods 2.3 | Rewrite |

## Dependencies
- [Note any ordering constraints between analyses]

## Response to Reviewers
- Template: paper/reviewer_feedback/response_draft.md
```

## Runtime integration

This skill is static instruction content, not an MCP server or API client. In a
generated project, the assistant reads the outline, analysis plan, manifest, and
prompt files directly. Zoo Code may provide user-configured Brave and Exa tools;
SMAIRT supplies the reviewed evidence workflow around them.
