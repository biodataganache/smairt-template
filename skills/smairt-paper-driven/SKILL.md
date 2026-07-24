---
name: smairt-paper-driven
description: Use when helping with a SMAIRT paper-driven project — research organized around producing a specific publication, with real datasets, iterative analyses mapped to paper sections, and reviewer feedback responses.
---

# SMAIRT Paper-Driven Research

SMAIRT Paper-Driven mode is a variant of the Scientific Method with AI Research Template designed for researchers writing a specific publication. Instead of progressing through synthetic → downloaded → real data, it starts with real datasets and a paper outline, then organizes all analyses as iterative contributions to paper sections.

## Core stance

- Treat the human as the source of novelty, judgment, and intellectual contribution.
- Organize ALL work around paper deliverables: every analysis exists to produce a specific figure, table, or finding for the manuscript.
- Maintain SMAIRT rigor (audit trail, hypothesis tracking, reproducibility) within the paper-driven structure.
- Track iterations explicitly — never modify previous iterations, always create new ones.
- Proactively watch for novel contributions from the human (Active Innovation Detection).

## When to use this skill

Use `smairt-paper-driven` instead of `smairt-research` when:
- The researcher has a paper outline or structure in mind
- Real datasets are already available
- The goal is a specific publication (not open-ended exploration)
- The researcher is revising a submitted paper based on reviewer feedback

## Workflow

Paper-driven mode follows this cycle per analysis section:

```text
Paper Section → Reviewed Literature → Hypothesis → Iteration (code + config) → Results → Decision (accept/revise) → repeat or finalize
```

### The iteration loop

1. State what you expect the analysis to show (hypothesis)
2. Create/modify code with a specific config
3. Run and capture results (TeeLogger handles logging)
4. Write analysis interpretation
5. Decision: ACCEPT (finalize) or REVISE (new iteration)

### Key differences from standard SMAIRT

| Standard SMAIRT | Paper-Driven SMAIRT |
|----------------|---------------------|
| Exploratory, hypothesis-driven | Goal-directed toward paper sections |
| Data progression: synthetic → real | Starts with real data directly |
| Scripts in `experiments/XX_phase/` | Scripts in `analysis/XX_section/iterations/` |
| Open-ended future directions | Analyses mapped to specific paper elements |
| `hypotheses/HYPOTHESIS_XX.md` | `analysis/XX_section/hypotheses.md` |

## Project structure

```text
paper/
  outline.md                    # Paper structure and section goals
  drafts/                       # Version-controlled manuscript drafts
  reviewer_feedback/            # Reviewer comments (for revisions)

data/
  {dataset}/                    # Real datasets organized by source

plans/                          # Research and revision plans
prompts/
  AI_CONTEXT.md                 # Core AI instructions
  CODE_CONVENTIONS.md           # Script conventions
  KNOWN_PATTERNS.md             # Reusable patterns & known errors
  intellectual_contribution.md  # Human contribution tracking

analysis/
  ANALYSIS_PLAN.md              # Maps paper sections to analyses
  BREADCRUMB_TRAIL.md           # Running log of progress
  01_{analysis_name}/
    README.md                   # What this analysis answers
    hypotheses.md               # Per-analysis hypotheses
    iterations/
      ITERATION_LOG.md          # Decision table across iterations
      iter_01/
        config_01.yaml          # Parameters for this iteration
        run_analysis_01.py      # Analysis script
        results/                # Output data
        figures/                # Generated plots
        NOTES.md                # Observations and decision
      iter_02/
        ...
    final/
      SELECTED.md               # Which iteration was chosen and why
      results/                  # Final accepted results
      figures/                  # Final accepted figures
  XX_figures/                   # Publication-ready figures (main + supplementary)

lib/                            # Shared library (utils, visualization, data loading)
scripts/                        # Helpers (new_experiment, new_iteration, finalize, generate_manifest)
results/logs/                   # Auto-generated log files
FINAL_MANIFEST.md               # Maps all paper elements to their source analyses
```

## Required practices

Before using prior work to motivate an analysis, claim novelty, or draft paper text:

- Follow the generated project's `prompts/LITERATURE_RESEARCH.md` workflow.
- Treat Brave and Exa results as candidates until the researcher approves them.
- Never request or write provider API keys; those stay in Zoo Code's GUI.
- Read approved `references/sources/*/reference.md` records and verify important claims.

When creating analysis scripts:

- Use `TeeLogger` from `scripts/shared/logging` for automatic log capture.
- Reference the hypothesis and analysis section in the docstring.
- Use configs (YAML) to separate parameters from code.
- Use the shared library (`lib/`) for consistent visualization and data loading.
- Set reproducibility seeds via config.
- Check `prompts/KNOWN_PATTERNS.md` before generating code.

When interpreting results:

- Evaluate through the stated hypothesis for that analysis section.
- Make a clear ACCEPT or REVISE decision with rationale.
- If REVISE: specify what to change in the next iteration.
- If ACCEPT: document why this iteration is sufficient.
- Update KNOWN_PATTERNS.md with any new reusable patterns or errors discovered.

When finalizing:

- Run `scripts/finalize_iteration.py` to copy accepted results to `final/`.
- Update `FINAL_MANIFEST.md` to map the accepted iteration to its paper element.
- Ensure all figures are publication-ready (proper labels, fonts, format).

## Revision workflow

When the project starts from reviewer feedback:

1. Place submitted manuscript in `paper/drafts/submitted_v1.md`
2. Place reviewer comments in `paper/reviewer_feedback/`
3. Generate a revision plan that:
   - Categorizes each reviewer concern (new analysis / rewrite / minor edit)
   - Maps new analyses to numbered sections in `analysis/ANALYSIS_PLAN.md`
   - Creates `plans/revision_plan.md` with priority ordering and dependencies
4. Execute each new analysis as a tracked SMAIRT iteration
5. Compile response-to-reviewers from the analysis results

## Context reload

When joining an existing paper-driven project:

1. Read `prompts/AI_CONTEXT.md`, `prompts/CODE_CONVENTIONS.md`, and `prompts/KNOWN_PATTERNS.md`.
2. Read `paper/outline.md` and `analysis/ANALYSIS_PLAN.md` for the big picture.
3. Check `analysis/BREADCRUMB_TRAIL.md` for recent progress.
4. Read the most recent `ITERATION_LOG.md` and `NOTES.md` for current state.
5. If revision: read `plans/revision_plan.md` for priorities.
6. Continue from the latest recorded state.

## Starting prompt (new paper)

```text
Please read prompts/AI_CONTEXT.md, prompts/CODE_CONVENTIONS.md, and prompts/KNOWN_PATTERNS.md.

I'm working in SMAIRT paper-driven mode.
- Paper topic: [brief description]
- Current section: [which analysis I'm working on]
- Data: [what data is available in data/]

Please help me with [specific task: create analysis script / interpret results /
design next iteration / prepare final figures].
```

## Starting prompt (revision)

```text
Please read:
- prompts/AI_CONTEXT.md and prompts/KNOWN_PATTERNS.md
- paper/drafts/submitted_v1.md (our submitted manuscript)
- paper/reviewer_feedback/ (all reviewer comments)

I need to revise this paper. Please:
1. Summarize each reviewer's key concerns (categorize as: new analysis needed /
   clarification / minor edits)
2. For concerns requiring NEW ANALYSIS, create entries in analysis/ANALYSIS_PLAN.md
3. Generate plans/revision_plan.md with priority ordering and dependencies
4. Generate a response-to-reviewers outline

Each new analysis should be a trackable SMAIRT section with iterations and audit trail.
```

## Active Innovation Detection

Watch for novel contributions. When the human proposes something beyond standard approaches — a new framing, unexpected connection, creative pivot, or interpretation that wouldn't follow from the data alone — ask:

> "This seems like a novel contribution (briefly describe why). Would you like me to log it in `prompts/intellectual_contribution.md`?"

## Reference

Read `references/paper_driven_workflow.md` for detailed iteration structure, config format, and finalization procedures.
