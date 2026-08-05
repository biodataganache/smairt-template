# Golden HPC Study

A normalized downloaded-data HPC golden project.

**Domain:** Data science

## Start here

Point an assistant at `docs/12_STEPS.md` and `prompts/AI_CONTEXT.md`. The first
describes the workflow and who owns which decision; the second describes the
assistant's role in this project. `prompts/CONTEXT_INDEX.md` says which files to read
for a given task.

Ready-made prompts for common situations are in `prompts/00_priming_prompts.md`.

## One pass through the loop

```bash
# 1. Start a track: writes the plan and the hypothesis, and no script yet
python3 scripts/new_track.py "The baseline exceeds chance" synthetic

# 2. Write the prediction and both criteria in the hypothesis file, and commit them
#    before any experiment exists

# 3. Create the iteration, then implement and run it from the project root
python3 scripts/new_iteration.py baseline synthetic --hypothesis HYPOTHESIS_01
python3 experiments/01_synthetic/script_01_baseline.py

# 4. Interpret the log it produced, against the criteria you committed in step 2
cp analysis/ANALYSIS_TEMPLATE.md analysis/ANALYSIS_01.md

# 5. Record what the iteration showed, in your own words
python3 scripts/record_outcome.py 1 --outcome "Criterion met, 0.71 against a 0.65 target"

# 6. Say which iteration you would report, and what it is evidence for
python3 scripts/select_result.py 1 --claim "The baseline exceeds chance"
```

Step 5 refuses until `analysis/ANALYSIS_01.md` exists, because an outcome recorded before
the run was read is a guess wearing a record's clothes. Step 6 reads the iteration log
rather than the filesystem, so an iteration that was never recorded cannot be reported.

The number ties the four records together, so any one of them leads to the rest:
hypothesis, script, log, analysis. Every numbered script is an iteration and appears in
`analysis/ITERATION_LOG.md`; utilities that test nothing live in `scripts/utilities/` and
take no number.

`smairt open` reports where the project stands and which of these commands comes next, so
you do not have to hold the sequence in your head.

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

Golden HPC Study is licensed under the terms recorded in `LICENSE`.

SMAIRT writes `LICENSE` only for the licenses whose complete official text it ships, so
the file is never an abbreviation of the license it names. To use a different license,
replace `LICENSE` with its full official text yourself and record the choice with your
institution. `smairt check` then reports `LICENSE` as researcher-modified and will not
replace it.
