# Plan: Adopt the iteration-workflow capabilities

## What the old scripts actually gave us

Three jobs, all still valid:

| Job | Old script | What made it valuable |
|---|---|---|
| Start a research track | `new_experiment.py` | One command produced a purpose statement, a hypothesis with success criteria, and a place for the first attempt. Nobody had to remember the shape. |
| Try again | `new_iteration.py` | Copied the prior config and script forward, and created a note with `Changes from Previous` and `ACCEPT/REVISE/ABANDON`. Made repeated attempts comparable. |
| Say which attempt counts | `finalize_iteration.py` | Produced a short rationale plus a manifest entry linking a claim to the files behind it. |

The current scaffold has [`new_script.py`](../src/smairt/assets/scaffold/scripts/new_script.py:17), which covers only "create the next numbered script." It even accepts `--iteration`, but nothing in the project records what an iteration *was*.

## Why not restore them

The old scripts are welded to `analysis/<section>_<name>/iterations/iter_XX/` with a parallel `final/` snapshot. The current project is flat and separated by kind: hypotheses, experiments, logs, analysis. Restoring the old tree would create a second, competing organization.

Also, `finalize_iteration.py` deletes prior final output with `shutil.rmtree()`. That cannot come back in any form.

## What an iteration is

From the PI:

> One iteration is one script/analysis/attempt at bringing us closer to the
> solution/end goal. Sometimes an iteration just provides us with a single point
> (does X change in the model lead to performance increase), or other times it may
> include a range of tests to probe in multiple directions at once (do any of these
> changes in this panel of suggested changes lead to model improvement).

Two consequences, both of which overturn my first draft.

**An iteration is a unit of work, not a unit of hypothesis.** It is one script, its log,
and its interpretation. So the record is keyed by iteration number, project-wide,
matching how `new_script.py` already numbers scripts sequentially rather than per phase.
There is no `H01` key. An iteration *references* the hypotheses it addresses.

**An iteration may test one thing or a panel.** A single-point iteration asks one
question. A panel iteration probes several directions at once and can return a mixed
result: three of eight changes helped, one hurt, four did nothing. A record that only
holds one status per iteration cannot express that, and forcing a panel into one
`SUPPORTED` would destroy the finding.

The hypothesis template already supports the panel case through its
`Sub-Hypotheses` section (`H_XXA`, `H_XXB`). The iteration record has to preserve that
shape rather than flatten it.

In the current layout an iteration already exists as four files:

```
hypotheses/H01_*.md                      <- what it should settle, and the criteria
experiments/01_synthetic/script_04_*.py  <- the attempt
results/logs/script_04_*.log             <- what it produced
analysis/ANALYSIS_04.md                  <- what it meant
```

Nothing is missing except a **record connecting iterations to each other**: what
iteration 4 changed from iteration 3, and what was decided. That is one project-level
record, not one per hypothesis.

## Proposed helpers

### 1. `new_track.py` - start a research track

```bash
python scripts/new_track.py "Fitness data predicts response" --phase synthetic
```

Creates, only if absent:

- `hypotheses/H0X_<slug>.md` from the existing template, with the statement filled in
- `plans/PLAN_<SLUG>.md` from the plan shape already documented in `plans/README.md`
- the first iteration, by calling the same code path `new_script.py` uses

Prints the three paths and the next action. Refuses if the hypothesis file exists.

A track is broader than an iteration: it is a direction of inquiry that several
iterations chip away at.

### 2. `new_iteration.py` - the next attempt

```bash
# single-point: does one change help
python scripts/new_iteration.py "wider hidden layer" --hypothesis H01 --from 03

# panel: probe several directions at once
python scripts/new_iteration.py "activation panel" --hypothesis H01 --probes 8
```

- Creates the next numbered script, seeded from the named prior iteration's script when
  `--from` is given, otherwise from the template
- Inserts a `Changed from iteration NN` block for the researcher to state what varied
- With `--probes N`, the script is seeded to loop over N labelled variants and write one
  row per variant, so a panel result stays disaggregated from the moment it is produced
- Creates `analysis/ITERATION_LOG.md` on first use, then **appends one row** per iteration

One project-level table, which is what the old `ITERATION_LOG.md` was for:

| Iteration | Script | Hypotheses | Kind | Changed from | Outcome |
|---|---|---|---|---|---|
| 03 | `script_03_baseline` | H01 | single | — | criterion met |
| 04 | `script_04_activation_panel` | H01 A–H | panel (8) | 03 | 3 of 8 above criterion |

`Kind` distinguishes the two cases the PI described. `Outcome` is one line of prose
rather than a fixed keyword, because `SUPPORTED` cannot describe a panel. The full
result stays in the analysis; this row is the index.

Never overwrites a script. Never edits an existing row.

### 3. `select_result.py` - record which iteration you would report

```bash
python scripts/select_result.py --iteration 4 --claim "Activation choice drives the gain"
```

- Creates `analysis/SELECTED_<NN>.md`: which iteration, why, and every file behind it
- For a panel iteration, requires naming *which probes* support the claim, so a panel is
  never reported as though all of it succeeded
- With `--paper`, appends an entry to `FINAL_MANIFEST.md`
- Copies nothing. Deletes nothing. Evidence stays where it was produced.

This is the safe half of `finalize_iteration.py`. The old copy-to-`final/` step existed
because the old tree buried results inside `iter_XX/`. Current results are already in one
place, so a pointer is strictly better than a duplicate that can drift.

## Vocabulary this adds to `docs/12_STEPS.md`

**Iteration** — one attempt at moving the work forward: one script, its log, and its
interpretation. Numbered project-wide in the order the work happened. An iteration may
be a *single point*, testing one change, or a *panel*, probing several directions at
once. A panel returns a result per probe and is recorded that way.

**Track** — a direction of inquiry, spanning however many iterations it takes. A track
has a plan and one or more hypotheses; an iteration is one attempt within it.

Step 11 already says "revise and iterate" without defining the term, and
`new_script.py` already accepts `--iteration`. Defining it closes that gap.

## The safety rule this needs

Every existing helper is non-destructive in the strongest sense: it only creates new files. Two of the three helpers above want to **append** to a record.

Proposed rule, to be confirmed:

> A helper may create a file that does not exist, and may append a new entry to a
> record whose format it owns. It may never modify or remove an existing line.

Appending is how a log stays a log. The alternative — printing a row for someone to paste — is what people forget to do, and forgetting is what the audit trail exists to prevent.

## Separate defect found while planning

Seven shipped files still describe the retired structure. My earlier retired-term check did not cover `iter_`, `ITERATION_LOG`, `SELECTED.md`, `run_analysis_`, or `lib/`:

| File | Problem |
|---|---|
| `analysis/ANALYSIS_PLAN.md` | Documents the whole `iterations/iter_01/` + `final/` tree and a `lib/` package that does not exist |
| `analysis/REPOSITORY_PLAN.md` | Same tree, plus `lib/core/utils.py` and `lib/io/data_loader.py` function listings |
| `analysis/BREADCRUMB_TRAIL.md` | Quick Reference table has an `iter_01` column |
| `analysis/XX_figures/README.md` | Figure provenance table keyed by iteration folder |
| `paper/FINAL_MANIFEST.md` | Points at `run_analysis_XX.py` and `config_XX.yaml` |
| `prompts/iteration_review_prompt.md` | Instructs updating `ITERATION_LOG.md` and copying to `final/` |
| `docs/12_STEPS.md` | Uses "iteration" without defining it |

These must be corrected regardless, and the vocabulary they should use is exactly what the new helpers establish. Doing them together means writing the iteration vocabulary once.

Extend the guard test with the retired path terms so this cannot recur.

## Sequence

1. Confirm the append rule and the two open questions below
2. Extend the guard test with retired structure terms, and watch it fail on the 7 files
3. Write the iteration vocabulary into `docs/12_STEPS.md`
4. Correct the 7 files to the current structure
5. Build the three helpers, declaring each in the blueprint
6. Document them in `scripts/README.md`, verifying every command by running it
7. Add the routes to `prompts/CONTEXT_INDEX.md` and a prompt to `00_priming_prompts.md`
8. Regenerate goldens, run all gates, record in `docs/scaffold-transition.md`

## Open questions

1. **Is `--probes N` worth seeding into the script?** It makes a panel produce
   per-variant rows from the start, which is the thing that gets lost when a panel is
   summarized too early. The cost is a helper that writes a loop the researcher may
   restructure anyway. The alternative is documenting the panel convention and leaving
   the code to the researcher and assistant.
2. **Scripts only, or `smairt` commands too?** Above assumes project scripts, which keeps
   the tool out of scientific content and works with no tool installed. `smairt track new`
   could wrap them later.
