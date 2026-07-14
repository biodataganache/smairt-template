# Context Index

A structured guide for the AI to know which files to read for different tasks.
Instead of loading everything at once, read what's relevant to the current task.

---

## Project Onboarding (First Time)

Read these files to understand the project from scratch:

| Order | File | Purpose |
|-------|------|---------|
| 1 | `prompts/AI_CONTEXT.md` | Your role and the workflow |
| 2 | `prompts/CODE_CONVENTIONS.md` | How to write code |
| 3 | `prompts/KNOWN_PATTERNS.md` | Patterns to reuse, errors to avoid |
| 4 | `background/` | Research question and context |
| 5 | Most recent `analysis/ANALYSIS_*.md` | Current state of the project |

---

## Writing a New Experiment

| File | Why |
|------|-----|
| `prompts/CODE_CONVENTIONS.md` | Script template and naming |
| `prompts/KNOWN_PATTERNS.md` | Reusable patterns |
| `scripts/shared/__init__.py` | Available shared utilities |
| Relevant `hypotheses/HYPOTHESIS_XX.md` | What we're testing |
| Most recent related script | Build on prior work |

---

## Interpreting Results

| File | Why |
|------|-----|
| The log file in `results/logs/` | Raw output to interpret |
| The script that generated it | Methodology context |
| `hypotheses/HYPOTHESIS_XX.md` | What we predicted |
| `analysis/ANALYSIS_TEMPLATE.md` | Template for writing analysis |
| `prompts/intellectual_contribution.md` | Record user insights |

---

## Planning a New Track

| File | Why |
|------|-----|
| `plans/README.md` | Plan template |
| Recent `analysis/` files | What's been learned |
| `plans/` directory | Existing plans for context |
| `prompts/AI_CONTEXT.md` | Workflow constraints |

---

## HPC Job Preparation

| File | Why |
|------|-----|
| The experiment script | What needs to run |
| `hpc/` directory | Existing job script templates |
| `prompts/CODE_CONVENTIONS.md` (HPC section) | HPC conventions |
| `scripts/shared/logging.py` | Logging setup for HPC |

---

## Debugging / Error Resolution

| File | Why |
|------|-----|
| `prompts/KNOWN_PATTERNS.md` | Check if this error is known |
| The failing script | Code to debug |
| The error log | Error details |
| `scripts/shared/` | Check if shared code is the issue |

---

## Context Refresh (After a Gap)

| File | Why |
|------|-----|
| Most recent 2-3 `analysis/ANALYSIS_*.md` | What happened recently |
| Most recent `hypotheses/HYPOTHESIS_*.md` | Current hypothesis |
| `prompts/KNOWN_PATTERNS.md` | Accumulated knowledge |
| `plans/` (active plans) | Current direction |

---

## Cross-Tool Transfer

When switching to a different AI tool:
1. Run `python scripts/compile_for_ai.py`
2. Provide the output file `prompts/compiled_for_ai.md` to the new tool

---

## File Inventory

### Core Prompt Files
- `prompts/AI_CONTEXT.md` — AI role and workflow description
- `prompts/CODE_CONVENTIONS.md` — Coding standards
- `prompts/KNOWN_PATTERNS.md` — Reusable patterns and known errors
- `prompts/SESSION_START.md` — Context-setting prompts
- `prompts/intellectual_contribution.md` — Human contribution tracking
- `prompts/CONTEXT_INDEX.md` — This file

### Planning & Tracking
- `plans/` — Planning documents for tracks and complex work
- `hypotheses/` — Per-iteration hypothesis files
- `analysis/` — Per-iteration analysis files
- `background/` — Research context and literature

### Code
- `experiments/01_synthetic/` — Phase 1 scripts
- `experiments/02_downloaded/` — Phase 2 scripts
- `experiments/03_real_data/` — Phase 3 scripts
- `scripts/shared/` — Reusable library code
- `scripts/compile_for_ai.py` — Project state compiler

### Results
- `results/logs/` — Script output logs
- `results/figures/` — Generated visualizations

### Infrastructure
- `hpc/` — HPC job scripts and configurations
- `data/` — Data files organized by phase
