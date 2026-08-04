# {{ project.name }}

{{ project.description }}

**Domain:** {{ project.domain }}
{% if project.research_question %}
## Research question

{{ project.research_question }}
{% endif %}
## Start here

Point an assistant at `docs/12_STEPS.md` and `prompts/AI_CONTEXT.md`. The first
describes the workflow and who owns which decision; the second describes the
assistant's role in this project. `prompts/CONTEXT_INDEX.md` says which files to read
for a given task.

Ready-made prompts for common situations are in `prompts/00_priming_prompts.md`.

## One pass through the loop

```bash
# 1. Start a track: writes the plan and the hypothesis, and no script yet
python scripts/new_track.py "The baseline exceeds chance" synthetic

# 2. Write the prediction and both criteria in the hypothesis file, and commit them
#    before any experiment exists

# 3. Create the iteration, then implement and run it from the project root
python scripts/new_iteration.py baseline synthetic --hypothesis HYPOTHESIS_01
python experiments/01_synthetic/script_01_baseline.py

# 4. Interpret the log it produced
cp analysis/ANALYSIS_TEMPLATE.md analysis/ANALYSIS_01.md

# 5. Record the outcome in analysis/ITERATION_LOG.md, then say what you would report
python scripts/select_result.py 1 --claim "The baseline exceeds chance"
```

The number ties the four records together, so any one of them leads to the rest:
hypothesis, script, log, analysis. Every numbered script is an iteration and appears in
`analysis/ITERATION_LOG.md`; utilities that test nothing live in `scripts/utilities/` and
take no number.

## Layout

```
smairt.yaml       Project contract: question, phase, capabilities, license
AGENTS.md         Pointer that directs an assistant to the project context
docs/             The research loop and project practice
prompts/          Assistant context, conventions, patterns, contribution record
background/       Research question, prior work, constraints
hypotheses/       One file per hypothesis, criteria recorded before the run
plans/            Plans for work spanning several experiments
experiments/      Numbered scripts in 01_synthetic, 02_downloaded, 03_real_data
data/             Inputs and their provenance, by phase
results/logs/     Raw execution records, never edited
results/figures/  Generated figures
analysis/         Interpretation per experiment, plus the study report
scripts/          Helpers, with shared library code in scripts/shared/
```

All three experiment phases are always present. The contract records
`starting_phase`, which never changes, and `current_phase`, which advances as the work
does.

## Managing this project

```bash
smairt              # Dashboard for this project
smairt check        # Report structural or configuration problems
smairt --help       # All commands
```

`smairt check` never modifies anything. Repairs are previewed and applied only on
confirmation, and they never touch researcher work.

## Capabilities

Paper and HPC are optional and independent. Enabling either adds files; disabling
marks the capability inactive and leaves existing files untouched. Toggle them from the
dashboard.

With Paper enabled: `paper/` for drafts and reviewer feedback, `FINAL_MANIFEST.md`
mapping claims to evidence, and three further prompts in `prompts/`.

With HPC enabled: `hpc/` for cluster configuration and job scripts. SMAIRT does not
submit, monitor, or cancel jobs.

## License

{{ project.name }} is licensed under the terms recorded in `LICENSE`.
