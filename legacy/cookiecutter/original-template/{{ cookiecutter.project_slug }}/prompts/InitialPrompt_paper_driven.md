# Initial Prompt: Paper-Driven Mode

Use this prompt when starting an AI session for a paper-driven SMAIRT project.

---

## Your Task

You are helping with a paper-driven research project using the SMAIRT framework.

Please read:
- `prompts/AI_CONTEXT.md` — Your role and workflow
- `prompts/CODE_CONVENTIONS.md` — Coding standards
- `prompts/KNOWN_PATTERNS.md` — Reusable patterns and errors to avoid
- `paper/outline.md` — The paper structure we're working toward
- `analysis/ANALYSIS_PLAN.md` — How analyses map to paper sections

---

## Project Information

- **Project:** {{ cookiecutter.project_name }}
- **Author:** {{ cookiecutter.author_name }}
- **Research Question:** {{ cookiecutter.initial_research_question }}
- **Mode:** Paper-Driven (working toward a specific paper)

---

## Process

The paper-driven workflow:

1. **Paper outline exists** — The structure we're writing toward
2. **Data is available** — Real datasets ready for analysis
3. **Analysis plan maps sections** — Each paper section has defined analyses
4. **Iterative execution** — Each analysis goes through iterations until publication-ready
5. **Final manifest** — Maps final results to paper elements

---

## Key Principles

1. **Every analysis serves a paper section** — No orphan work
2. **Iterations are numbered** — iter_01, iter_02, ... → final/
3. **Decisions are documented** — ACCEPT / REVISE / ABANDON for each iteration
4. **Shared library grows** — Reusable code goes to `scripts/shared/`
5. **Patterns accumulate** — Update `KNOWN_PATTERNS.md` as you learn
6. **Plans drive complex work** — Create plan docs before multi-step analyses

---

## Questions to Ask

Before starting, the AI should ask about:
1. What data is available? (format, size, location)
2. Which paper section should we work on first?
3. Are there existing results to build on?
4. What are the computational constraints?
5. Are there specific statistical methods required?

---

## Directory Structure

```
paper/
├── outline.md              # Paper structure
└── drafts/                 # Draft versions

analysis/
├── ANALYSIS_PLAN.md        # Maps analyses to paper sections
├── ANALYSIS_TEMPLATE.md    # Template for analysis files
├── REPOSITORY_PLAN.md      # Repository-level planning
└── ANALYSIS_XX.md          # Per-iteration analysis

experiments/
├── 01_synthetic/           # If applicable
├── 02_downloaded/          # If applicable
└── 03_real_data/           # Primary for paper-driven

scripts/
├── shared/                 # Reusable library
├── new_experiment.py       # Create new analysis
├── new_iteration.py        # Create new iteration
└── finalize_iteration.py   # Mark iteration as final
```

---

## Getting Started

1. Review `paper/outline.md` and `analysis/ANALYSIS_PLAN.md`
2. Identify the first analysis to tackle
3. Create a hypothesis for it
4. Write the experiment script
5. Run, analyze, iterate
