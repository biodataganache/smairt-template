# SMAIRT Paper-Driven Mode Tutorial

This tutorial walks you through using SMAIRT's paper-driven mode to transform your research into a publication-ready paper.

---

## Overview

Paper-driven mode is designed for researchers who:
- Have a paper outline or structure in mind
- Have real datasets ready for analysis
- Need to develop a comprehensive analysis plan
- Want to maintain SMAIRT's reproducibility and iteration tracking benefits

**Key Difference from Standard SMAIRT:**
- Standard SMAIRT: Hypothesis → Data progression (synthetic → downloaded → real)
- Paper-Driven SMAIRT: Paper outline + Real datasets → Analysis plan → Iterative execution

Both modes share the same core principles: the 10 Steps, the audit trail, intellectual contribution tracking, and KNOWN_PATTERNS.md.

---

## Step 1: Create Your Project

```bash
# Install cookiecutter if needed
pip install cookiecutter

# Create a new SMAIRT project
cookiecutter gh:yourusername/smairt-cookiecutter
```

When prompted, select `paper_driven` for the `project_mode` option. The `starting_phase` will automatically be set to `real` since paper-driven mode works directly with your datasets.

You'll see output like:
```
📄 SMAIRT Project Created Successfully! 📄

Scientific Method with AI Research Template - PAPER-DRIVEN MODE
```

---

## Step 2: Set Up Your Paper Outline

There are two starting points for paper-driven mode:
- **2A**: You're writing a new paper (start from an outline)
- **2B**: You're revising a submitted paper based on reviewer feedback

### Step 2A: Starting from a New Paper Outline

Navigate to your project and edit `paper/outline.md`:

```markdown
# My Research Paper

## 1. Introduction
- Background on the problem
- Gap in current knowledge
- Our contribution

## 2. Methods
- Data sources
- Analysis approach

## 3. Results
### 3.1 First Analysis
- Expected figures: Fig 1, Fig 2
- Expected tables: Table 1

### 3.2 Second Analysis
- Expected figures: Fig 3
- Expected tables: Table 2

## 4. Discussion
## 5. Conclusion
```

Then continue to Step 3.

### Step 2B: Starting from Reviewer Feedback (Revision)

If you've already submitted a paper and received reviewer comments, SMAIRT paper-driven mode is ideal for organizing your revision systematically. Place your materials in the project:

1. **Put your submitted manuscript** in `paper/drafts/submitted_v1.md` (or `.pdf`)
2. **Put reviewer feedback** in `paper/reviewer_feedback/`:
   ```
   paper/reviewer_feedback/
   ├── reviewer_1.md
   ├── reviewer_2.md
   ├── reviewer_3.md
   └── editor_decision.md
   ```

Then use this prompt to generate your revision plan:

```
Please read the following files:
- paper/drafts/submitted_v1.md (our submitted manuscript)
- paper/reviewer_feedback/ (all reviewer comments)
- prompts/AI_CONTEXT.md
- prompts/CODE_CONVENTIONS.md

I need to revise this paper based on the reviewer feedback. Please help me:

1. Summarize each reviewer's key concerns (categorize as: new analysis needed,
   clarification/rewriting needed, or minor edits)

2. For each concern requiring NEW ANALYSIS, create an entry in
   analysis/ANALYSIS_PLAN.md with:
   - Which reviewer comment it addresses
   - What data/method is needed
   - Expected output (figure, table, or text)

3. Generate paper/outline.md that reflects the revised paper structure,
   noting where new content will go

4. Create a revision plan in plans/revision_plan.md with:
   - Priority ordering (address most critical concerns first)
   - Dependencies between analyses
   - Estimated iterations per analysis
   - A response-to-reviewers outline

Please organize the new analyses as numbered sections in the analysis plan,
so each reviewer concern maps to a trackable SMAIRT analysis with its own
iterations and audit trail.
```

The AI will produce:
- `paper/outline.md` — revised paper structure
- `analysis/ANALYSIS_PLAN.md` — maps reviewer concerns to new analyses
- `plans/revision_plan.md` — prioritized revision roadmap

**Example output** in `plans/revision_plan.md`:

```markdown
# Revision Plan

## Priority 1: New Analyses Required

| # | Reviewer Comment | Analysis | Expected Output | Est. Iterations |
|---|-----------------|----------|-----------------|-----------------|
| 1 | R2.3: "Need statistical test for..." | 01_statistical_test | Table 2 (revised) | 1-2 |
| 2 | R1.5: "Show results on additional dataset" | 02_additional_dataset | Fig 4 (new) | 2-3 |
| 3 | R3.1: "Ablation study needed" | 03_ablation_study | Table 3 (new) | 2-3 |

## Priority 2: Reanalysis / Revised Figures

| # | Reviewer Comment | Analysis | Expected Output |
|---|-----------------|----------|-----------------|
| 4 | R1.2: "Error bars missing" | 04_error_bars | Fig 1-3 (revised) |

## Priority 3: Writing / Clarification Only

| # | Reviewer Comment | Section | Action |
|---|-----------------|---------|--------|
| 5 | R2.1: "Methods unclear" | Methods 2.3 | Rewrite paragraph |
| 6 | R3.4: "Cite Smith et al." | Intro | Add citation |

## Dependencies
- Analysis 02 depends on data download (check data availability first)
- Analysis 03 can run in parallel with 01

## Response to Reviewers Template
See paper/reviewer_feedback/response_draft.md
```

Then proceed with Step 3 (your data may already be in place from the original submission) and continue through the normal iteration workflow — each reviewer concern becomes a tracked analysis with its own hypothesis, scripts, logs, and interpretation.

---

## Step 3: Add Your Data

Organize your data in the `data/` directory:

```
data/
├── README.md           # Document your data sources
├── dataset_a/
│   ├── raw/
│   └── processed/
└── dataset_b/
    ├── raw/
    └── processed/
```

Update `data/README.md` with:
- Data sources and citations
- Data formats
- Any preprocessing steps
- Data access instructions (if restricted)

---

## Step 4: Create Your Analysis Plan

Edit `analysis/ANALYSIS_PLAN.md` to map your paper sections to specific analyses:

```markdown
## Paper Structure Mapping

| Paper Section | Analysis Directory | Status |
|---------------|-------------------|--------|
| Results 3.1 | `01_first_analysis/` | Not started |
| Results 3.2 | `02_second_analysis/` | Not started |

## Detailed Analysis Plan

### 01_first_analysis

**Purpose**: Answer [specific question]

**Data Inputs**:
- `data/dataset_a/processed/data.csv`

**Analysis Steps**:
1. Load and validate data
2. Apply method X
3. Generate Figure 1

**Expected Iterations**: 2-3

**Outputs**:
- Figure 1: Comparison plot
- Table 1: Summary statistics
```

You can also create a more detailed plan in `plans/` if the analysis requires multi-step coordination:

```markdown
# plans/analysis_01_plan.md

## Goal
Answer specific research question using dataset A.

## Steps
1. Data validation and characterization
2. Apply method X with baseline parameters
3. Tune parameters based on initial results
4. Generate publication-quality figures

## Risks
- Data may have missing values requiring imputation
- Method X may not converge for this data type
```

---

## Step 5: Start Your First Analysis

Use the helper script to create an analysis directory:

```bash
python scripts/new_experiment.py --section 01 --name first_analysis
```

This creates:
```
analysis/01_first_analysis/
├── README.md
├── hypotheses.md
└── iterations/
    ├── ITERATION_LOG.md
    └── iter_01/
        ├── NOTES.md
        ├── config_01.yaml
        ├── results/
        └── figures/
```

---

## Step 6: Run Your First Iteration

### 6.1 Prime Your AI

**IDE-Native (Zoo Code, Cursor, Windsurf):** Your AI can read project files directly. Start with:

```
Please read prompts/AI_CONTEXT.md, prompts/CODE_CONVENTIONS.md, and prompts/KNOWN_PATTERNS.md.

I'm working in paper-driven mode on [brief description].
I'm starting analysis 01: [analysis name].
My hypothesis: [what you expect to find]

Please help me create the analysis script using TeeLogger for the audit trail.
```

**Browser-Paste:** Run `python scripts/compile_for_ai.py` and paste the output, followed by `prompts/InitialPrompt_paper_driven.md`.

### 6.2 Create Your Analysis Script

Create `analysis/01_first_analysis/iterations/iter_01/run_analysis_01.py`:

```python
#!/usr/bin/env python
"""
First analysis - Iteration 01

Hypothesis: [Your hypothesis]
Analysis: 01_first_analysis
Iteration: 01
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
import matplotlib.pyplot as plt

# === CONFIGURATION ===
SCRIPT_NAME = "run_analysis_01_iter01"
LOG_DIR = PROJECT_ROOT / "results" / "logs"
config = load_config('config_01.yaml')
set_seed(config.get('seed', 1024))

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

        # Set up plotting
        setup_plot_style()

        # Your analysis code here
        # ...

        # Save results
        results = {
            'metric_a': 0.85,
            'metric_b': 0.72,
        }
        save_results(results, 'results/metrics.json')

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6))
        # ... your plotting code ...
        save_figure(fig, 'figures/fig_01_comparison')

        print()
        print(f"Results: {results}")
        print(f"{'='*60}")
        print("=== COMPLETE ===")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
```

Output is automatically captured to `results/logs/run_analysis_01_iter01_YYYYMMDD_HHMMSS.log` via TeeLogger — no need to paste output anywhere.

### 6.3 Configure Your Analysis

Edit `config_01.yaml`:

```yaml
seed: 1024

data:
  input: "../../../../data/dataset_a/processed/data.csv"

parameters:
  threshold: 0.5
  method: "approach_a"

output:
  results_dir: "results/"
  figures_dir: "figures/"
```

### 6.4 Run and Document

```bash
cd analysis/01_first_analysis/iterations/iter_01
python run_analysis_01.py
```

Update `NOTES.md` with your observations:

```markdown
# Iteration 01 Notes

## Date
2024-01-15

## Changes from Previous
- Initial implementation

## Results
- metric_a: 0.85
- metric_b: 0.72

## Observations
- Method works but threshold may need tuning
- Figure shows expected pattern

## Decision
REVISE - Try different threshold values

## Next Steps
- Test threshold = 0.6, 0.7
```

Also write `analysis/ANALYSIS_01.md` for the project-level audit trail:

```markdown
# Analysis 01: First Analysis - Iteration 01

## Hypothesis
Threshold of 0.5 will be optimal for dataset A.

## Result
metric_a: 0.85, metric_b: 0.72. Threshold needs tuning.

## Interpretation
Method works but may benefit from higher threshold. Decision: REVISE.

## Next Steps
Test threshold = 0.6, 0.7 in iteration 02.
```

---

## Step 7: Iterate

### 7.1 Create Next Iteration

```bash
python scripts/new_iteration.py --analysis 01_first_analysis --iteration 02
```

This copies your previous config and script as starting points.

### 7.2 Make Changes

Edit `config_02.yaml`:
```yaml
parameters:
  threshold: 0.6  # Changed from 0.5
```

### 7.3 Run and Compare

Run the new iteration and update `ITERATION_LOG.md`:

```markdown
| Iter | Date | Description | Key Change | Metrics | Decision |
|------|------|-------------|------------|---------|----------|
| 01 | 2024-01-15 | Baseline | Initial | a=0.85, b=0.72 | Revise |
| 02 | 2024-01-16 | Tuned threshold | 0.5→0.6 | a=0.89, b=0.78 | **ACCEPT** |
```

### 7.4 Update Known Patterns

If you discovered something reusable, add it to `prompts/KNOWN_PATTERNS.md`:

```markdown
### 1.X Threshold Sensitivity for Method X
**Context**: When applying method X to datasets with high variance
**Pattern**: Start with threshold = 0.6, not 0.5
**Why**: Lower thresholds include noise; 0.6 is the sweet spot for this data type
```

---

## Step 8: Finalize Results

When you're satisfied with an iteration:

```bash
python scripts/finalize_iteration.py --analysis 01_first_analysis --iteration 02
```

This:
1. Copies results and figures to `final/`
2. Creates `SELECTED.md` documenting your choice
3. Updates `FINAL_MANIFEST.md`

Edit `final/SELECTED.md` with your rationale:

```markdown
# Selected Iteration

**Selected**: iter_02
**Date**: 2024-01-16

## Rationale
Iteration 02 achieved better metrics (a=0.89 vs 0.85) with the
adjusted threshold. Results are stable across multiple runs.

## Key Metrics
| Metric | Value |
|--------|-------|
| metric_a | 0.89 |
| metric_b | 0.78 |
```

---

## Step 9: Track Progress

### Update the Breadcrumb Trail

Add entries to `analysis/BREADCRUMB_TRAIL.md`:

```markdown
### 2024-01-16 - First Analysis Complete

**What was done**:
- Completed first analysis with 2 iterations
- Final threshold: 0.6
- Generated Figure 1

**Key findings**:
- Method X shows 89% accuracy
- Threshold of 0.6 optimal for this dataset

**Next steps**:
- Begin second analysis
- Apply same approach to dataset_b
```

### Track Intellectual Contributions

Update `prompts/intellectual_contribution.md`:

```markdown
## Analysis 01 - First Analysis

### What I Contributed
- Identified threshold sensitivity as the key parameter
- Chose to tune threshold rather than switch methods (AI suggested method Y)
- Interpreted the metric improvement in context of the research question

### Where AI Helped
- Generated boilerplate analysis code
- Suggested visualization approaches
- Implemented parameter sweep efficiently
```

> **Note:** If your AI has Active Innovation Detection enabled, it will proactively flag when you make novel contributions — you don't have to remember to log them yourself.

### Generate Manifest

```bash
python scripts/generate_manifest.py
```

---

## Step 10: Prepare for Publication

### Final Figures

Copy publication-ready figures to `analysis/XX_figures/`:

```
analysis/XX_figures/
├── main/
│   ├── fig_01_comparison.pdf
│   ├── fig_02_results.pdf
│   └── fig_03_summary.pdf
└── supplementary/
    ├── fig_s01_details.pdf
    └── fig_s02_additional.pdf
```

### Review FINAL_MANIFEST.md

Ensure all paper elements are documented:

```markdown
## Summary

| Paper Element | Analysis | Iteration | Status |
|---------------|----------|-----------|--------|
| Figure 1 | 01_first_analysis | iter_02 | ✓ Finalized |
| Figure 2 | 02_second_analysis | iter_03 | ✓ Finalized |
| Table 1 | 01_first_analysis | iter_02 | ✓ Finalized |
```

### Review the Audit Trail

Your project now contains a complete record:

```
results/logs/
├── run_analysis_01_iter01_20240115_143022.log
├── run_analysis_01_iter02_20240116_091544.log
└── run_analysis_02_iter01_20240117_102233.log

analysis/
├── ANALYSIS_01.md    # Interpretation of iter_01
├── ANALYSIS_02.md    # Interpretation of iter_02
└── ...
```

Each script run is automatically logged. Hypotheses, scripts, logs, and analyses form the complete breadcrumb trail.

---

## Tips for Success

### 1. Use AI Effectively

**IDE-Native** (recommended): Your AI reads files directly. Point it to context:
```
Please read the log file at results/logs/run_analysis_01_iter02_*.log
and help me interpret the results against HYPOTHESIS_01.md.
```

For iteration reviews:
```
Please read analysis/01_first_analysis/iterations/ITERATION_LOG.md
and prompts/iteration_review_prompt.md to help me evaluate whether
to accept or revise this iteration.
```

**Browser-Paste**: Run `python scripts/compile_for_ai.py` to get a single file you can paste.

### 2. Document Everything

- Update `NOTES.md` after every iteration
- Keep `ITERATION_LOG.md` current
- Write per-iteration analysis files (`analysis/ANALYSIS_XX.md`)
- Update `prompts/KNOWN_PATTERNS.md` when you solve errors or create reusable code
- Track intellectual contributions (or let Active Innovation Detection help)

### 3. Use Consistent Styling

Always use the shared library for plots:
```python
from lib.visualization.style import setup_plot_style, save_figure, COLORS
setup_plot_style()
```

### 4. Set Seeds for Reproducibility

```python
from lib.core.utils import set_seed
set_seed(1024)  # Default seed
```

### 5. Keep Iterations Separate

Never modify a previous iteration's files. Always create a new iteration for changes.

### 6. Maintain Known Patterns

When you discover something important — a working code pattern, a recurring error, or a project-specific convention — add it to `prompts/KNOWN_PATTERNS.md`. This prevents the AI from repeating past mistakes across sessions.

---

## Directory Structure Reference

```
your_project/
├── paper/
│   ├── outline.md              # Paper structure
│   ├── drafts/                 # Version-controlled drafts
│   └── reviewer_feedback/      # Feedback documents
│
├── data/
│   └── {dataset}/              # Your datasets
│
├── plans/                      # Research plans & coordination
│
├── prompts/                    # AI context files
│   ├── AI_CONTEXT.md           # Core AI instructions
│   ├── CODE_CONVENTIONS.md     # Script structure rules
│   ├── KNOWN_PATTERNS.md       # Reusable patterns & errors
│   ├── SESSION_START.md        # Priming prompts
│   └── intellectual_contribution.md
│
├── analysis/
│   ├── ANALYSIS_PLAN.md        # Maps analyses to paper
│   ├── REPOSITORY_PLAN.md      # Repository organization
│   ├── BREADCRUMB_TRAIL.md     # Running log
│   ├── ANALYSIS_01.md          # Per-iteration interpretations
│   ├── 01_{analysis}/
│   │   ├── README.md
│   │   ├── hypotheses.md
│   │   ├── iterations/
│   │   │   ├── ITERATION_LOG.md
│   │   │   ├── iter_01/
│   │   │   └── iter_02/
│   │   └── final/
│   │       ├── SELECTED.md
│   │       ├── results/
│   │       └── figures/
│   └── XX_figures/             # Final publication figures
│
├── results/
│   ├── logs/                   # Auto-generated by TeeLogger
│   └── figures/
│
├── lib/                        # Shared library
│   ├── core/utils.py
│   ├── io/data_loader.py
│   ├── processing/transforms.py
│   └── visualization/style.py
│
├── scripts/
│   ├── shared/                 # TeeLogger, setup_logging
│   ├── new_experiment.py
│   ├── new_iteration.py
│   ├── finalize_iteration.py
│   ├── compile_for_ai.py
│   └── generate_manifest.py
│
├── FINAL_MANIFEST.md           # Maps results to paper
└── README.md
```

---

## Common Workflows

### Starting Fresh
1. Create project with `paper_driven` mode
2. Add paper outline
3. Add data
4. Create analysis plan (in `analysis/ANALYSIS_PLAN.md` and/or `plans/`)
5. Start first analysis

### Continuing Work
1. AI reads recent analysis files and logs for context (IDE-native)
2. Review `prompts/KNOWN_PATTERNS.md` for reusable patterns and errors to avoid
3. Review `ANALYSIS_PLAN.md` for next steps
4. Create new iteration or new analysis
5. Update documentation (including KNOWN_PATTERNS.md)

### Preparing Submission
1. Run `generate_manifest.py`
2. Review all `SELECTED.md` files
3. Collect final figures
4. Verify reproducibility
5. Review `prompts/intellectual_contribution.md` for attribution

---

## Getting Help

- Review `prompts/InitialPrompt_paper_driven.md` for AI assistance
- Check `prompts/SESSION_START.md` for session priming prompts
- See `analysis/REPOSITORY_PLAN.md` for conventions
- See `lib/README.md` for shared library usage
- Read `docs/SMAIRT_PHILOSOPHY.md` for framework principles
