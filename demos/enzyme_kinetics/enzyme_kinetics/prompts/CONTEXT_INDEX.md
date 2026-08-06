# Context Index

Which files to read for a given task. Read what the task needs rather than everything
at once.

## Starting on this project for the first time

| Order | File | What it gives |
|---|---|---|
| 1 | `docs/12_STEPS.md` | The workflow, and who owns which decision |
| 2 | `prompts/AI_CONTEXT.md` | The assistant's role in this project |
| 3 | `smairt.yaml` | The project contract: question, phase, capabilities |
| 4 | `prompts/CODE_CONVENTIONS.md` | How code here is written |
| 5 | `prompts/KNOWN_PATTERNS.md` | What already works, and what already failed |
| 6 | `background/` | The research question and its context |
| 7 | Most recent `analysis/ANALYSIS_*.md` | Where the work currently stands |

## Starting a new track

| File | Why |
|---|---|
| `analysis/ANALYSIS_PLAN.md` | The tracks already in flight, and what each one settles |
| `plans/README.md` | What a plan contains |
| `background/` | Whether the question has already been approached |
| `scripts/README.md` | `new_track.py` starts a track with a plan and a hypothesis, before any script exists |

## Writing a new experiment

An experiment is an iteration: one script, its log, its interpretation.

| File | Why |
|---|---|
| The relevant `hypotheses/HYPOTHESIS_XX.md` | What is being tested, and what would refute it |
| `analysis/ITERATION_LOG.md` | What has already been attempted, and what came of it |
| `prompts/CODE_CONVENTIONS.md` | Script structure and naming |
| `prompts/KNOWN_PATTERNS.md` | Patterns to reuse instead of reinventing |
| `scripts/shared/__init__.py` | Utilities that already exist |
| The script named in `Changed from` | What this attempt varies |

Use `scripts/new_iteration.py`, which numbers the script and records the attempt. Add
`--probes N` when the iteration tests several candidate directions at once rather than one.

## Interpreting results

| File | Why |
|---|---|
| The log in `results/logs/` | The raw output being interpreted |
| The script that produced it | Methodology context |
| `hypotheses/HYPOTHESIS_XX.md` | The criteria recorded before the run |
| `analysis/ANALYSIS_TEMPLATE.md` | The structure to write into |
| `analysis/ITERATION_LOG.md` | Where to record the outcome, and what earlier attempts showed |
| `scripts/README.md` | `record_outcome.py` writes the outcome once the analysis exists |

For a panel iteration, report every probe. Three of eight above criterion with one
regression is the finding; a single verdict would discard it.

With the Paper capability enabled, `prompts/iteration_review_prompt.md` adds a fuller
review procedure. It is listed here only as an addition, because a project without that
capability does not have the file.

## Recording a result you would report

| File | Why |
|---|---|
| `analysis/ITERATION_LOG.md` | Which attempt is the one worth reporting |
| The log behind that attempt | The evidence the claim rests on |
| `scripts/README.md` | `select_result.py` writes the record and points at the evidence |
| `FINAL_MANIFEST.md` | With the Paper capability, the claim to evidence map |

## Planning multi-experiment work

| File | Why |
|---|---|
| `plans/README.md` | What a plan contains |
| `plans/` | Plans already in flight |
| `analysis/ANALYSIS_PLAN.md` | Tracks, planned iterations, metrics, and figure plan |
| Recent `analysis/` files | What has been established |
| `prompts/AI_CONTEXT.md` | Workflow constraints |

## Writing or updating the study report

| File | Why |
|---|---|
| `analysis/STUDY_REPORT_TEMPLATE.md` | Structure for the project-level synthesis |
| `analysis/STUDY_REPORT.md`, if present | The version to update rather than replace |
| Recent `analysis/ANALYSIS_*.md` | Evidence to synthesize |
| `hypotheses/HYPOTHESIS_*.md` | The status of each hypothesis tested |
| `prompts/intellectual_contribution.md` | Contributions to credit |

Suggest this when a coherent finding emerges, before a phase transition, before a
handoff, or when asked for project status.

## Debugging a failure

| File | Why |
|---|---|
| `prompts/KNOWN_PATTERNS.md` | Whether this error is already known here |
| The failing script | The code |
| The log in `results/logs/` | Full output, including warnings and traceback |
| `scripts/shared/` | Whether shared code is the cause |

## Resuming after a gap

| File | Why |
|---|---|
| Most recent two or three `analysis/ANALYSIS_*.md` | What happened recently |
| Most recent `hypotheses/HYPOTHESIS_*.md` | The current question |
| `prompts/session_log.md` | Why the recent decisions were made |
| `plans/` | The active direction |

Resume from these files rather than from conversation memory.

## Preparing an HPC job

| File | Why |
|---|---|
| The experiment script | What needs to run |
| `hpc/config.yaml` | Cluster, partition, account, resources |
| `hpc/templates/slurm_basic.sh` | The template to copy and adapt |
| `scripts/shared/logging.py` | Keeping log capture intact on a cluster |

Present when the HPC capability is enabled.

## Where everything lives

```
smairt.yaml          Project contract: question, phase, capabilities, license
docs/                The workflow and project practice
prompts/             Assistant context, conventions, patterns, contribution record
background/          Research question, prior work, constraints
hypotheses/          One file per hypothesis, with criteria recorded before the run
plans/               Plans for work spanning several experiments
experiments/         Numbered scripts, by data phase
results/logs/        Raw execution records, never edited
results/figures/     Generated figures
analysis/            Interpretation, one file per experiment, plus the study report
data/                Inputs and their provenance, by phase
scripts/             Helpers, and shared library code in scripts/shared/
paper/               Publication workspace, when Paper is enabled
hpc/                 Cluster configuration and job scripts, when HPC is enabled
```
