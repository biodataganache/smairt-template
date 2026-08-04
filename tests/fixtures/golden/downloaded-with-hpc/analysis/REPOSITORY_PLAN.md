# Repository Plan

## Project: Golden HPC Study

How this repository is organized, and the conventions that keep it navigable as it
grows. Edit this file when the project's conventions change.

---

## 1. Directory Structure

```
golden_hpc_study/
├── smairt.yaml                 # Project contract: identity, phase, capabilities
├── README.md                   # Entry point
├── FINAL_MANIFEST.md           # Paper claim to evidence map (Paper capability)
│
├── background/                 # Prior work and constraints
├── hypotheses/                 # One file per hypothesis, with criteria
├── plans/                      # Plans written before multi-step work
│
├── experiments/                # Executable experiments, numbered by iteration
│   ├── 01_synthetic/
│   ├── 02_downloaded/
│   └── 03_real_data/
│
├── data/                       # Inputs and provenance, by phase
│   ├── synthetic/
│   ├── downloaded/
│   └── real/
│
├── results/                    # Durable evidence
│   ├── logs/                   # Complete captured run records
│   └── figures/                # Generated figures
│
├── analysis/                   # Interpretation and synthesis
│   ├── ANALYSIS_PLAN.md        # Tracks, iterations, metrics, figure plan
│   ├── REPOSITORY_PLAN.md      # This file
│   ├── ITERATION_LOG.md        # One row per iteration
│   ├── BREADCRUMB_TRAIL.md     # Narrative log of what was learned
│   ├── ANALYSIS_XX.md          # One interpretation per iteration
│   └── XX_figures/             # Figure workspaces
│
├── docs/                       # 12_STEPS.md, philosophy, practices
├── prompts/                    # Assistant context and researcher records
│
├── scripts/                    # Helpers
│   ├── new_script.py
│   ├── generate_manifest.py
│   ├── monitor_template.py
│   └── shared/                 # Reusable code, including TeeLogger
│
├── paper/                      # Present only with the Paper capability
└── hpc/                        # Present only with the HPC capability
```

Experiments, data, and results are separated by *kind* rather than nested per analysis.
A script lives with other scripts of its phase; its evidence lives in `results/logs/`;
its interpretation lives in `analysis/`. One iteration therefore spans four directories,
and the shared iteration number is what ties them together.

---

## 2. Naming Conventions

### Iterations

An iteration is one attempt: one script, its log, its interpretation. Numbering runs
across the whole project in the order the work happened, not per phase and not per
analysis.

| Artifact | Pattern | Example |
|---|---|---|
| Script | `script_NN_description.py` | `experiments/01_synthetic/script_04_activation_panel.py` |
| Log | `script_NN_description_<timestamp>.log` | `results/logs/script_04_activation_panel_20240115_101500.log` |
| Interpretation | `ANALYSIS_NN.md` | `analysis/ANALYSIS_04.md` |
| Hypothesis | `HYPOTHESIS_XX.md` | `hypotheses/HYPOTHESIS_01.md` |

The log name is produced by `setup_logging()`, so it matches the script without anyone
maintaining it.

### Figures

- Main: `fig_01_description.png`
- Supplementary: `fig_s01_description.png`
- Save the formats the venue needs, typically `.png` plus a vector format

### Directories

Phase directories are fixed: `01_synthetic`, `02_downloaded`, `03_real_data`. Do not add
parallel per-analysis trees; the iteration number already orders the work.

---

## 3. Shared Code

Reusable code lives in `scripts/shared/` and is imported as
`from scripts.shared.<module> import ...`.

What ships:

- `shared/logging.py` - `TeeLogger` and `setup_logging()`, the complete-capture record

What to add as the project earns it:

- Data loading that more than one experiment uses
- Figure styling shared across figures, so panels match without duplication
- Domain-specific processing that has stabilized

Extract into `shared/` only after a second experiment needs the same thing. An
experiment script should stay readable as a record of what was done, so premature
extraction costs more than the duplication it removes.

---

## 4. Iteration Tracking

`analysis/ITERATION_LOG.md` carries one row per iteration:

```markdown
| Iteration | Date | Script | Hypotheses | Kind | Changed from | Outcome |
|---|---|---|---|---|---|---|
| 03 | YYYY-MM-DD | `script_03_baseline` | H01 | single | — | Criterion met, 0.71 vs 0.65 target |
| 04 | YYYY-MM-DD | `script_04_activation_panel` | H01 | panel (8) | 03 | 3 of 8 above criterion, 1 regression |
```

`Kind` is `single` when the iteration tests one change, or `panel (N)` when it probes N
candidate directions at once.

`Outcome` is one line of prose rather than a fixed keyword. A panel cannot be described
by a single verdict: "3 of 8 above criterion, 1 regression" is the finding, and
`SUPPORTED` would discard it. Full probe-level results belong in the analysis; this row
is the index into it.

Rows are appended and never rewritten. A row that turned out to be wrong is corrected by
a later row that says so, because the sequence of attempts is itself evidence.

The decision for an iteration is recorded in its analysis and in the hypothesis status,
not in this table.

---

## 5. Final Manifest

The `FINAL_MANIFEST.md` file maps each paper element to its source:

```markdown
## Figure 1
- **Source**: `results/figures/`
- **Script**: `experiments/01_synthetic/script_03_sweep.py`
- **Evidence**: `results/logs/script_03_sweep_20240115_101500.log`
- **Generated**: YYYY-MM-DD

## Table 1
- **Source**: `results/`
- **Script**: `experiments/03_real_data/script_02_validation.py`
- **Evidence**: `results/logs/script_02_validation_20240118_143000.log`
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

Each iteration must have:

- [ ] A hypothesis file stating the prediction and the criteria, committed before the
      script exists
- [ ] A script whose docstring names the hypothesis it tests
- [ ] A complete log in `results/logs/`, unedited
- [ ] An `analysis/ANALYSIS_NN.md` interpretation
- [ ] A row in `analysis/ITERATION_LOG.md`
- [ ] For a panel, a result recorded per probe rather than a single summary

Each track must have:

- [ ] A plan in `plans/`
- [ ] An entry in the `Tracks` table of `analysis/ANALYSIS_PLAN.md`, kept current
      including when the track is abandoned
