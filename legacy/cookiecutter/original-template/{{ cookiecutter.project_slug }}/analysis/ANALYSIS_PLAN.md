# Analysis Plan

{% if cookiecutter.project_mode == 'paper_driven' %}
## Project: {{ cookiecutter.project_name }}

**Author**: {{ cookiecutter.author_name }}  
**Created**: [DATE]  
**Last Updated**: [DATE]

---

## 1. Overview

{{ cookiecutter.description }}

**Research Question**: {{ cookiecutter.initial_research_question }}

---

## 2. Paper Structure Mapping

| Paper Section | Analysis Directory | Status |
|---------------|-------------------|--------|
| Results 4.1 | `01_results_section_a/` | Not started |
| Results 4.2 | `02_results_section_b/` | Not started |
| Supplementary | `XX_supplementary/` | Not started |

---

## 3. Execution Framework

### 3.1 Iteration Workflow

Each analysis follows this structure:
```
analysis_name/
├── iterations/
│   ├── ITERATION_LOG.md
│   ├── iter_01/
│   │   ├── run_analysis_01.py
│   │   ├── config_01.yaml
│   │   ├── results/
│   │   ├── figures/
│   │   └── NOTES.md
│   └── iter_02/
└── final/
    ├── SELECTED.md
    ├── results/
    └── figures/
```

### 3.2 Shared Library

Common functions are in `lib/`:
- `lib/core/` - Core utilities
- `lib/io/` - Data loading/saving
- `lib/processing/` - Data processing
- `lib/visualization/` - Plotting functions

### 3.3 Computational Resources

- [ ] Local machine
- [ ] HPC cluster
- [ ] Cloud (GPU)

---

## 4. Detailed Analysis Plan

### 4.1 [Analysis Section A]

**Directory**: `analysis/01_results_section_a/`

**Purpose**: [What question does this answer?]

**Data Inputs**:
- [List data files]

**Analysis Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Iterations**: 2-3

**Outputs**:
- Results: [Description]
- Figures: [List figures]
- Tables: [List tables]

### 4.2 [Analysis Section B]

**Directory**: `analysis/02_results_section_b/`

**Purpose**: [What question does this answer?]

**Data Inputs**:
- [List data files]

**Analysis Steps**:
1. [Step 1]
2. [Step 2]

**Expected Iterations**: 2-3

**Outputs**:
- Results: [Description]
- Figures: [List figures]

---

## 5. Evaluation Framework

### 5.1 Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| [Metric 1] | [Description] | [Target value] |
| [Metric 2] | [Description] | [Target value] |

### 5.2 Validation Approaches

- [ ] [Validation method 1]
- [ ] [Validation method 2]
- [ ] [Cross-dataset comparison]

---

## 6. Figure Plan

### Main Figures

| Figure | Description | Analysis Source | Status |
|--------|-------------|-----------------|--------|
| Fig 1 | [Description] | `01_results_section_a/` | Not started |
| Fig 2 | [Description] | `02_results_section_b/` | Not started |

### Supplementary Figures

| Figure | Description | Analysis Source | Status |
|--------|-------------|-----------------|--------|
| S1 | [Description] | [Source] | Not started |

---

## 7. Timeline

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1 | [Tasks] | [Deliverables] |
| 2 | [Tasks] | [Deliverables] |
| 3 | [Tasks] | [Deliverables] |

---

## 8. Data Requirements

| Dataset | Location | Format | Size | Status |
|---------|----------|--------|------|--------|
| [Dataset 1] | `data/[path]` | [Format] | [Size] | Available |
| [Dataset 2] | `data/[path]` | [Format] | [Size] | Needed |

---

## 9. Hypotheses

### H1: [Hypothesis 1]
- **Statement**: [Clear, testable statement]
- **Test**: [How will this be tested?]
- **Analysis**: [Which analysis addresses this?]

### H2: [Hypothesis 2]
- **Statement**: [Clear, testable statement]
- **Test**: [How will this be tested?]
- **Analysis**: [Which analysis addresses this?]

---

## 10. Execution Notes

### Reproducibility
- Random seed: 1024
- All parameters documented in config files
- Environment captured in requirements.txt

### Quality Checklist
- [ ] All analyses have ITERATION_LOG.md
- [ ] Final iterations documented in SELECTED.md
- [ ] Figures saved in multiple formats (PNG, PDF, SVG)
- [ ] FINAL_MANIFEST.md updated
{% else %}
This file is only used in paper-driven mode.

For standard SMAIRT mode, see:
- `hypotheses/README.md` for hypothesis tracking
- `experiments/` for experiment organization
{% endif %}
