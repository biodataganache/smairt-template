# Priming Prompts

Copy-pasteable prompts for {{ project.name }}, one per situation. Fill in the bracketed
parts. For which files to open for a given task, see `prompts/CONTEXT_INDEX.md`.

## First contact

For an assistant that has not seen this project before.

```text
This is a SMAIRT project. Read docs/12_STEPS.md, prompts/AI_CONTEXT.md, and
prompts/CONTEXT_INDEX.md, then read smairt.yaml for the project contract.

Summarize the research question, the current phase, what evidence exists so far, and
which decisions are still open. Do not propose work yet.
```

## Resuming after a gap

Continue from the project's files rather than from conversation memory.

```text
Continuing this SMAIRT project. Read:
- prompts/AI_CONTEXT.md and prompts/KNOWN_PATTERNS.md
- the most recent file in hypotheses/
- the most recent file in analysis/
- the raw log in results/logs/ that the analysis refers to

Then state where the work stands and what the recorded next step is.
```

## Starting a new track

```text
Read analysis/ANALYSIS_PLAN.md, analysis/ITERATION_LOG.md, and background/.

I want to start a track on: [the question]

Tell me whether this overlaps a track already in flight or a direction already ruled
out. If it is new, propose the hypothesis statement with success and rejection criteria,
and say what result would be uninformative either way. I will choose the criteria.
```

Then create the records:

```bash
python3 scripts/new_track.py "[the question]" [synthetic|downloaded|real]
```

## Before writing an experiment

An experiment is an iteration: one script, its log, its interpretation.

```text
Read prompts/CODE_CONVENTIONS.md, prompts/KNOWN_PATTERNS.md, and
analysis/ITERATION_LOG.md.

Hypothesis: hypotheses/HYPOTHESIS_[XX].md
Phase: [synthetic | downloaded | real]

Check the iteration log for what has already been attempted on this hypothesis, then
implement the script. Reuse what is in scripts/shared/ rather than writing new
equivalents.
```

Create the iteration first, so it is numbered and recorded:

```bash
# one change
python3 scripts/new_iteration.py "[description]" [phase] --hypothesis HYPOTHESIS_[XX]

# several candidate directions at once
python3 scripts/new_iteration.py "[description]" [phase] --hypothesis HYPOTHESIS_[XX] --probes [N]

# continuing from an earlier attempt
python3 scripts/new_iteration.py "[description]" [phase] --hypothesis HYPOTHESIS_[XX] --from-iteration [NN]
```

## Interpreting results

```text
Read:
- results/logs/[the log file]
- the script that produced it
- hypotheses/HYPOTHESIS_[XX].md, including its success and rejection criteria
- analysis/ANALYSIS_TEMPLATE.md

Assess the hypothesis against the criteria that were recorded before the run. State
where the result holds and where it breaks. Draft analysis/ANALYSIS_[XX].md; leave the
significance judgment to the researcher.
```

## Planning multi-experiment work

```text
Read prompts/AI_CONTEXT.md, the recent files in analysis/, and any existing plans in
plans/.

Goal: [what the work should establish]
Constraints: [time, compute, data]

Draft a plan in plans/ naming the hypothesis it serves, the evidence that would settle
it, the smallest informative first experiment, and what would indicate the approach is
not worth continuing.
```

## Preparing an HPC job

```text
Read the experiment script, hpc/config.yaml, and hpc/templates/slurm_basic.sh.

Adapt the template for this script: resources, modules, and environment. Keep
TeeLogger output going to results/logs/. Do not submit the job.
```

## Mid-session reminder

When an assistant drifts from the project's conventions.

```text
SMAIRT reminder:
- The hypothesis is written before the experiment, the analysis after the results
- Scripts are script_XX_description.py in the phase directory, created by
  scripts/new_iteration.py, which also records the attempt
- TeeLogger captures stdout, stderr, warnings, and tracebacks into results/logs/
- Negative results stay, and state where an approach breaks
- Reference files by path rather than pasting their contents
```
