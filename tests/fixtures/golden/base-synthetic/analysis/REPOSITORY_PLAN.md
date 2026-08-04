# Repository Plan

## Project: Golden Synthetic Study

This document defines the repository organization for the paper-driven project.

---

## 1. Directory Structure

```
golden_synthetic_study/
├── paper/                      # Paper documents
│   ├── outline.md              # Paper outline/structure
│   ├── drafts/                 # Version-controlled drafts
│   └── reviewer_feedback/      # Feedback documents
│
├── data/                       # All datasets
│   ├── README.md               # Data documentation
│   └── {dataset_name}/         # Organized by source
│
├── analysis/                   # All analyses
│   ├── ANALYSIS_PLAN.md        # Analysis planning
│   ├── REPOSITORY_PLAN.md      # Repository organization
│   ├── BREADCRUMB_TRAIL.md     # Running log
│   ├── 01_{section}/           # Maps to paper section
│   ├── 02_{section}/
│   └── XX_figures/             # Final publication figures
│
├── lib/                        # Shared library
│   ├── __init__.py
│   ├── core/                   # Core utilities
│   ├── io/                     # Data I/O
│   ├── processing/             # Processing functions
│   └── visualization/          # Plotting
│
├── prompts/                    # AI prompts & context
│   ├── InitialPrompt_paper_driven.md
│   ├── AI_CONTEXT.md
│   ├── CODE_CONVENTIONS.md
│   ├── KNOWN_PATTERNS.md
│   └── ...
│
├── plans/                      # AI-generated plans (git-tracked)
│   └── README.md
│
├── hpc/                        # HPC configuration (if needed)
│   ├── config.yaml
│   └── templates/
│
├── scripts/                    # Utility scripts
│   ├── new_script.py
│   ├── generate_manifest.py
│   ├── monitor_template.py
│   └── shared/                 # TeeLogger & shared utilities
│
├── results/                    # All output
│   ├── logs/                   # Auto-captured script output
│   └── figures/                # Generated figures
│
├── FINAL_MANIFEST.md           # Maps results to paper
└── README.md
```

---

## 2. Naming Conventions

### Directories
- Analysis sections: `01_descriptive_name/`, `02_descriptive_name/`
- Iterations: `iter_01/`, `iter_02/`

### Files
- Scripts: `run_analysis_01.py`, `run_analysis_02.py`
- Configs: `config_01.yaml`, `config_02.yaml`
- Notes: `NOTES.md` (in each iteration)

### Figures
- Main figures: `fig_01_description.png`
- Supplementary: `fig_s01_description.png`
- Save in multiple formats: `.png`, `.pdf`, `.svg`

---

## 3. Shared Library Functions

### lib/core/utils.py
- `load_config()` - Load YAML/JSON config
- `ensure_dir()` - Create directory if needed
- `save_results()` - Save results to file

### lib/io/data_loader.py
- `load_data()` - Load dataset by name
- `save_data()` - Save processed data

### lib/processing/
- Add domain-specific processing functions

### lib/visualization/style.py
- `setup_plot_style()` - Set publication style
- `save_figure()` - Save in multiple formats
- `COLORS` - Consistent color palette

---

## 4. Iteration Tracking

### ITERATION_LOG.md Format

```markdown
| Iter | Date | Description | Key Change | Metrics | Decision |
|------|------|-------------|------------|---------|----------|
| 01 | YYYY-MM-DD | Baseline | Initial | metric=X | Revise |
| 02 | YYYY-MM-DD | Tuned | param change | metric=Y | ACCEPT |
```

### Decision Options
- **ACCEPT** - Meets targets, use for paper
- **REVISE** - Promising, needs tuning
- **ABANDON** - Fundamental issue

---

## 5. Final Manifest

The `FINAL_MANIFEST.md` file maps each paper element to its source:

```markdown
## Figure 1
- **Source**: `results/figures/`
- **Script**: `experiments/01_synthetic/script_03_sweep.py`
- **Evidence**: `results/logs/script_03_sweep-20240115-101500.log`
- **Generated**: YYYY-MM-DD

## Table 1
- **Source**: `results/`
- **Script**: `experiments/03_real_data/script_02_validation.py`
- **Evidence**: `results/logs/script_02_validation-20240118-143000.log`
```

Naming the log rather than an iteration number is what makes a claim checkable: the
log records the code, inputs, and output of the run that produced the evidence.

---

## 6. Git Workflow

### Branches
- `main` - Stable, paper-ready results
- `dev` - Active development
- `analysis/{name}` - Specific analysis work

### Commits
- Use descriptive commit messages
- Reference analysis/iteration in commits
- Tag paper submission versions

---

## 7. Documentation Requirements

Each analysis must have:
- [ ] `README.md` - Purpose, data, methods
- [ ] `ITERATION_LOG.md` - All iterations
- [ ] `NOTES.md` - Per-iteration notes
- [ ] `SELECTED.md` - Final selection rationale
