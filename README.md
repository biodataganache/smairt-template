# SMAIRT: Scientific Method with AI Research Template

A [cookiecutter](https://cookiecutter.readthedocs.io/) template for AI-accelerated scientific research. SMAIRT provides a structured framework for conducting iterative, hypothesis-driven research with AI assistants.

---

## The Hard Problem of Science

> AI excels at regression toward the mean — it can't innovate in a meaningful way. But it CAN help you get quickly to the frontier of what's already known.

SMAIRT helps you move quickly from not knowing much to being at the frontier of an area, where you can see the gaps and make genuine contributions.

---

## Overview

SMAIRT is designed for researchers who use AI tools (VSCode Roo/Zoo, Cursor, Windsurf, ChatGPT, Claude) to accelerate their research. It provides:

- **Structure** — A proven directory layout for experiments, hypotheses, analysis, and results
- **Workflow** — The scientific method in an iterative loop with clear documentation
- **AI Integration** — Prompt files and conventions that make AI assistants effective collaborators
- **Reproducibility** — Audit trails, log files, and systematic documentation

---

## Project Modes

### Standard Mode (default)

Hypothesis-driven exploration with a configurable starting phase. Choose where to begin based on your data situation:

- **Synthetic** — Full 3-phase progression (synthetic → downloaded → real). Best for algorithm development and new methods where you want fast iteration without data dependencies.
- **Downloaded** — Start with established benchmarks. Best when validated datasets already exist for your problem.
- **Real** — Start directly with your own data. Best when you're bringing your own dataset or synthetic data doesn't apply.

### Paper-Driven Mode

For research that starts with a paper outline and real datasets. Perfect for more mature ideas, paper revisions, or when you already know the structure of the story you're telling.

---

## Workflow Modes

### IDE-Native (default)
For AI-integrated IDEs where the AI has direct file access:
- **VSCode with Roo/Zoo** (recommended)
- **Cursor**
- **Windsurf**

The AI reads files directly, writes code, executes commands, and updates documentation without any copy-pasting.

### Browser-Paste
For browser-based AI tools (ChatGPT web, Claude web) where context must be manually transferred via copy/paste.

---

## Quick Start

```bash
# Install cookiecutter
pip install cookiecutter

# Create a new SMAIRT project
cookiecutter gh:biodataganache/smairt-cookiecutter
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

---

## Tutorials

- **[QUICKSTART.md](QUICKSTART.md)** — Get started in 5 minutes
- **[TUTORIAL.md](TUTORIAL.md)** — Full standard mode walkthrough
- **[TUTORIAL_PAPER_DRIVEN.md](TUTORIAL_PAPER_DRIVEN.md)** — Paper-driven mode guide
- **[TUTORIAL_HPC.md](TUTORIAL_HPC.md)** — HPC/SLURM submission guide
- **[DEMOS](/demos)** - Set of demos showcasing SMAIRT usage in action

---

## Philosophy

### AI's Role
- Getting quickly to the frontier of existing knowledge
- Iterating through hypothesis-experiment-results loops
- Generating code that can be tested immediately
- Maintaining consistency across experiments

### Your Role
- Making truly innovative connections
- Identifying novel gaps and directions
- Critical interpretation of results
- Deciding when to pivot or abandon approaches

---

## The Workflow

```
Background → Hypothesis → Methods/Code → Results → Analysis → Future Directions → (repeat)
```

### The 4-Part Structure

Every iteration produces:
1. **Background** — Context, prior work, motivation
2. **Hypothesis** — Specific, testable prediction with success criteria
3. **Methods** — The experiment script and data
4. **Results** — Output logs + interpretation in analysis files

### Data Progression

Choose your starting phase when creating a project:

| Starting Phase | Directories Created | Best For |
|----------------|--------------------|----|
| `synthetic` (default) | 01_synthetic → 02_downloaded → 03_real_data | Algorithm development, new methods |
| `downloaded` | 02_downloaded → 03_real_data | Known benchmarks, existing methods |
| `real` | 03_real_data only | Bringing your own data, domain-specific questions |

---

## Generated Project Structure

```
my_smairt_project/
├── prompts/                    # AI context and conventions
│   ├── AI_CONTEXT.md           # AI role and workflow description
│   ├── CODE_CONVENTIONS.md     # Coding standards
│   ├── KNOWN_PATTERNS.md       # Reusable patterns & known errors
│   ├── CONTEXT_INDEX.md        # What to read for different tasks
│   ├── SESSION_START.md        # Context-setting prompts
│   └── intellectual_contribution.md  # Human contribution tracking
├── plans/                      # Planning documents
├── hypotheses/                 # Per-iteration hypothesis files
│   └── HYPOTHESIS_TEMPLATE.md
├── analysis/                   # Per-iteration analysis files and research synthesis
│   ├── ANALYSIS_TEMPLATE.md
│   └── FINAL_REPORT_TEMPLATE.md
├── experiments/                # Scripts organized by phase
│   ├── 01_synthetic/
│   ├── 02_downloaded/
│   └── 03_real_data/
├── scripts/                    # Helper scripts
│   ├── shared/                 # Reusable library (logging, metrics)
│   ├── compile_for_ai.py       # Cross-tool context transfer
│   ├── new_script.py           # Script generator
│   └── monitor_template.py    # HPC job monitor template
├── results/
│   ├── logs/                   # Script output logs
│   └── figures/                # Generated visualizations
├── data/
│   ├── synthetic/
│   ├── downloaded/
│   └── real/
├── background/                 # Research context
├── docs/                       # Framework documentation
├── hpc/                        # HPC job scripts
└── paper_draft/                # Parallel narrative
```

---

## Key Features

### The Audit Trail
Every experiment produces linked artifacts:
- Hypothesis file → Script → Log file → Analysis file

The AI reads these directly (no copy-pasting needed in IDE-native mode).

### Known Patterns & Error Prevention
`prompts/KNOWN_PATTERNS.md` accumulates:
- Reusable code patterns
- Common errors and their fixes
- Consistency rules (seeds, DPI, formats)
- Pre-flight checklist

### Intellectual Contribution Tracking
Track where YOU make critical decisions in `prompts/intellectual_contribution.md`. The AI actively watches for novel contributions — unexpected connections, creative pivots, or domain insights — and asks whether to log them. This ensures your genuine innovations don't get lost in the flow of AI-assisted work.

### Multi-Track Experimentation
As projects grow, fork into parallel tracks:
```
script_A01_...  — Track A
script_B01_...  — Track B
script_X1_...   — Track X (interpretation)
```

### Shared Library
`scripts/shared/` provides reusable utilities:
- `TeeLogger` — Dual console/file logging
- Custom metrics, data loading, model architectures

### Final Report Checkpoints
`analysis/FINAL_REPORT_TEMPLATE.md` provides a consistent format for project-level research synthesis. Use it to create or update `analysis/FINAL_REPORT.md` after coherent findings emerge, before phase transitions, before handoff, before paper drafting, or at project completion.

The final report complements numbered analysis files by synthesizing the central question, study scope, audit trail, results matrix, cross-iteration conclusions, reproducibility assets, limitations, and next steps.

### Plans Directory
`plans/` holds planning documents created before complex work begins.

### Git Repository & Collaboration
Projects are initialized as git repositories by default (`create_git_repo: yes`). SMAIRT includes best-practice guides for both solo and collaborative workflows:
- **Single-user** — Commit discipline, phase tagging, atomic commits per iteration
- **Collaborative** — Branch strategy, file ownership conventions, merge conflict prevention, intellectual contribution tracking per team member

See `docs/BEST_PRACTICE_SINGLE.md` and `docs/BEST_PRACTICE_COLLABORATIVE.md` in generated projects.

### MCP Skills Integration
SMAIRT ships with two [MCP skills](skills/) that AI tool agents can load for structured guidance:
- **`smairt-research`** — The full standard-mode workflow, audit trail conventions, and script patterns
- **`smairt-paper-driven`** — Paper-driven iteration structure, analysis plans, and finalization steps

Skills give AI assistants persistent context about SMAIRT conventions without requiring manual prompt priming each session.

### HPC Support
Generated projects include an `hpc/` directory with SLURM templates, a cluster configuration file, and a job-monitoring script. See [TUTORIAL_HPC.md](TUTORIAL_HPC.md) for a walkthrough covering:
- Adapting the SLURM template to your cluster (partitions, accounts, modules)
- Submitting experiment scripts as batch jobs
- Monitoring jobs and integrating HPC logs with the audit trail

---

## AI Context Files

| File | Purpose |
|------|---------|
| `prompts/AI_CONTEXT.md` | AI's role, workflow, project structure |
| `prompts/CODE_CONVENTIONS.md` | Script template, naming, logging |
| `prompts/KNOWN_PATTERNS.md` | Reusable code, known errors, standards |
| `prompts/CONTEXT_INDEX.md` | What files to read for different tasks |
| `prompts/SESSION_START.md` | Context-setting prompts for different situations |

---

## Requirements

- Python 3.8+
- [cookiecutter](https://cookiecutter.readthedocs.io/) (`pip install cookiecutter`)
- An AI assistant (VSCode Roo/Zoo, Cursor, Windsurf, ChatGPT, Claude, etc.)

---

## Usage

### Starting a Session (IDE-Native)

Point your AI to `prompts/AI_CONTEXT.md`. It will understand the workflow and conventions. Use prompts from `prompts/SESSION_START.md` for different situations (onboarding, context refresh, planning, interpretation).

### Starting a Session (Browser-Paste)

Run `python scripts/compile_for_ai.py` and paste the output into your AI session.

### Creating New Experiments

Ask your AI to create a hypothesis file and experiment script following the conventions in `prompts/CODE_CONVENTIONS.md`.

### Recording Results

After running experiments:
1. AI reads the log file directly
2. AI writes analysis to `analysis/ANALYSIS_XX.md`
3. AI suggests updates to `prompts/KNOWN_PATTERNS.md` if new patterns/errors discovered
4. AI proposes next hypothesis

---

## Template Options

| Option | Description | Default |
|--------|-------------|---------|
| `project_name` | Human-readable project name | My SMAIRT Project |
| `project_mode` | Standard or paper-driven | standard |
| `workflow_mode` | IDE-native or browser-paste | ide_native |
| `ai_tool` | Primary AI tool used | roo_zoo |
| `domain` | Research domain | machine_learning |
| `starting_phase` | Where to begin experiments | synthetic |
| `create_git_repo` | Initialize git on creation | yes |

---

## Contributing

Contributions welcome! See the issues page for current needs.

---

## License

MIT

---

## Acknowledgments

SMAIRT was developed through iterative use of AI-assisted research workflows, refined by observing what actually works in practice (see `docs/MODERNIZATION_PROPOSAL.md`).
