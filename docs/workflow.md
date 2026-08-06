# The research workflow

SMAIRT records a chain of evidence. This is how you build it.

Every command here runs inside a generated project. If you do not have one yet, see the
[README](../README.md).

## Why helpers instead of writing files yourself

You could create `script_01_baseline.py` by hand. Do not.

An iteration is one attempt at moving the work forward, and its **number** is what joins the
four records that describe it:

```text
hypotheses/HYPOTHESIS_01.md
  -> experiments/01_synthetic/script_01_baseline.py
  -> results/logs/script_01_baseline_20260805_173826_686563.log
  -> analysis/ANALYSIS_01.md
```

Only `new_iteration.py` assigns that number, because two things assigning numbers eventually
assign the same one. A script you create yourself joins no hypothesis, appears in no iteration
log, and breaks the chain the workflow exists to build. The helpers are not conveniences; they
are what keeps the record joinable.

## The loop

### 1. Start a track

```bash
python3 scripts/new_track.py "Fitness data predicts response" synthetic
```

A track is a direction of inquiry. This writes a plan and a hypothesis, and stops there.

The phase is `synthetic`, `downloaded`, or `real` — see [Phases](#phases).

### 2. Write the criteria, and commit them

Open the new `hypotheses/HYPOTHESIS_NN.md` and fill in the prediction and both criteria: what
result would support it, and what result would count against it. Then commit that file.

Committing before an experiment exists is what keeps the test a test. A criterion written after
you have seen the output is not a prediction. This is why `new_track.py` deliberately stops
here rather than creating the first script for you.

### 3. Create the iteration and run it

```bash
python3 scripts/new_iteration.py baseline synthetic --hypothesis HYPOTHESIS_01
python3 experiments/01_synthetic/script_01_baseline.py
```

The helper takes the next number, writes the script with logging already wired, and records the
iteration in `analysis/ITERATION_LOG.md`.

Running it writes two things you do not have to manage: a uniquely named log in
`results/logs/`, and a line in `analysis/RUN_HISTORY.md` recording that execution and its exact
log. Immediate reruns cannot overwrite each other, so a crash stays visible even if a later run
succeeds. A traceback that appeared only in your terminal is not evidence.

### 4. Interpret the result

```bash
cp analysis/ANALYSIS_TEMPLATE.md analysis/ANALYSIS_01.md
python3 scripts/record_outcome.py 1 --outcome "Criterion met, 0.71 against a 0.65 target"
```

Write what the log actually shows in the analysis file, then record the outcome. The analysis is
yours: SMAIRT never reads, rewrites, or judges it.

### 5. Iterate, or report

```bash
python3 scripts/new_iteration.py "wider layer" synthetic --hypothesis HYPOTHESIS_01 --from-iteration 1
python3 scripts/select_result.py 1 --claim "The baseline exceeds chance"
```

`--from-iteration` records what an attempt came from, so the sequence of attempts stays
readable later. `select_result.py` marks an iteration as the evidence for a claim you intend to
report.

## Where you are

```bash
smairt open .
```

Reports what the project is missing next and the command that addresses it, derived from the
records rather than from a fixed script. Run it whenever you lose the thread.

## Phases

Every project contains all three phase directories from the start. The phase you pass to a
helper decides where its script lands:

| Argument | Directory | For |
|---|---|---|
| `synthetic` | `experiments/01_synthetic/` | Data you generated, where you know the answer |
| `downloaded` | `experiments/02_downloaded/` | Public or benchmark data |
| `real` | `experiments/03_real_data/` | The data the question is actually about |

Starting synthetic is the recommended habit: a method that cannot recover a signal you planted
yourself will not be trusted on data where nobody knows the answer.

`current_phase` in `smairt.yaml` records where attention is. It does not restrict where you
work.

## Utilities

A script that supports the work without testing anything — a downloader, a converter, a figure
regenerator — is a utility, not an iteration:

```bash
python3 scripts/new_utility.py fetch_reference_data --purpose "Download the reference set"
```

It takes no number and appears in no log, because numbering something that settles no question
would put a row in the iteration log for it. Shared code that several scripts import belongs in
`scripts/shared/`.

## Checking the structure

```bash
smairt check .
```

Read-only. It reports structural and configuration problems — a missing managed file, a stale
scaffold version, an iteration referencing a hypothesis that does not exist. It does not assess
whether your science is correct, and never will.

`smairt repair .` previews deterministic fixes for tool-owned files. Both leave your work alone.

## What SMAIRT will not do

SMAIRT does not perform science. It does not validate a conclusion, judge a hypothesis, or
decide whether a result is good. The question, the evidence, and the interpretation are yours.

What it does is make the trail hard to lose: a run through the generated frame is logged, and a
claim recorded through the workflow can be traced to the log that supports it.

The guarantee is about what the workflow records going forward, not about work that predates it.
Two of the demos carry science that ran before this execution record existed, and they say so
rather than presenting a reconstructed trail as a captured one.

## Next

- [Paper and HPC capabilities](capabilities.md)
- [Upgrading an existing project](upgrading.md)
- Worked examples: [`demos/`](../demos/)
