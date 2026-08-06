# Scripts

Helpers for the research loop. All of them are non-destructive: they create files that do
not exist and append new lines to records they own. None of them modifies or removes a
line that is already there.

Run each from the project root, and use `--help` for the full argument list.

| Helper | What it does |
|---|---|
| `new_track.py` | Starts a track: a plan and a hypothesis, before any script exists |
| `new_iteration.py` | Creates the next iteration and records it in the iteration log |
| `record_outcome.py` | Records what an iteration turned out to show, once you have interpreted it |
| `select_result.py` | Records which iteration you would report, and the evidence behind it |
| `new_utility.py` | Creates an unnumbered utility script that is not an iteration |
| `generate_manifest.py` | Prints or writes an inventory of research artifacts |
| `monitor_template.py` | Observes a progress file from a long or remote run |
| `shared/` | Reusable code: logging capture and iteration bookkeeping |

## One numbering authority

Every numbered script under `experiments/` is an iteration, and every iteration appears in
`analysis/ITERATION_LOG.md`. Only `new_iteration.py` assigns a number, because two helpers
handing out numbers independently would eventually hand out the same one.

Work that supports the research without testing anything — a downloader, a figure
regenerator — is a utility. It lives in `scripts/utilities/`, takes no number, and gets no
row. That keeps the numbering a readable timeline of attempts rather than a mix of attempts
and errands.

## The loop these support

```bash
# 1. Start a direction of inquiry
python3 scripts/new_track.py "Fitness data predicts response" synthetic

# 2. Write the prediction and both criteria in the hypothesis file, and commit them

# 3. Create the iteration, then implement and run it
python3 scripts/new_iteration.py baseline synthetic --hypothesis HYPOTHESIS_01
python3 experiments/01_synthetic/script_01_baseline.py

# 4. Interpret the log, then record what the iteration showed
cp analysis/ANALYSIS_TEMPLATE.md analysis/ANALYSIS_01.md
python3 scripts/record_outcome.py 1 --outcome "Criterion met, 0.71 against a 0.65 target"

# 5. Try again, or report the result
python3 scripts/new_iteration.py "wider layer" synthetic --hypothesis HYPOTHESIS_01 --from-iteration 1
python3 scripts/select_result.py 1 --claim "The baseline exceeds chance"
```

## new_track.py

```bash
python3 scripts/new_track.py "Fitness data predicts response" synthetic
```

Creates two things: `hypotheses/HYPOTHESIS_XX.md` and `plans/PLAN_<NAME>.md`. The
hypothesis number is assigned from the files already present, so identifiers stay unique
and ordered.

It deliberately does **not** create the first script. Write the prediction and both
criteria into the hypothesis file and commit them before running `new_iteration.py`.
Committing the criteria first is what keeps the test a test rather than a
rationalization — and a helper that created the hypothesis and the script in the same
instant would leave nothing to show any ordering at all.

How much that commit proves is worth being clear about: local history can be rewritten and
dates can be set by hand, so it is a record you keep for yourself and offer to someone who
trusts it, not a proof against someone who does not. `docs/12_STEPS.md` step 4 says what to
do when you need the stronger claim.

### Optional rigor declarations

Advanced project settings can ask `new_track.py` and `new_iteration.py` to add blank
fields for multiplicity policy, discovery/validation role, unit of inference, and
per-probe hypothesis status. These switches change only files created afterward. They do
not rewrite templates or existing research files, block work, or name a statistical
method. Standing commitments live in researcher-owned `analysis/RIGOR.md`; an assistant
may suggest wording, but the researcher approves, edits, or rejects it.

These questions matter even when the extra fields are disabled: multiple probes create
more opportunities for accidental passes, adapting and validating on the same data can
hide overfitting, repeated measurements need not be independent units, and one panel
verdict can conceal mixed probe outcomes.

## new_iteration.py

An iteration is one attempt: one script, its log, its interpretation.

```bash
# a single point: does one change help
python3 scripts/new_iteration.py "wider layer" synthetic --hypothesis HYPOTHESIS_01

# a panel: do any of these candidates help
python3 scripts/new_iteration.py "activation panel" synthetic --hypothesis HYPOTHESIS_01 --probes 8

# continue from an earlier attempt instead of the blank template
python3 scripts/new_iteration.py "wider layer" synthetic --hypothesis HYPOTHESIS_01 --from-iteration 3
```

`--hypothesis` is required, because naming what an attempt should settle before writing
it is the convention this project runs on.

Numbering is sequential across the whole project rather than per phase, so filenames read
as the order the work happened:

```
experiments/01_synthetic/script_01_baseline.py
experiments/02_downloaded/script_04_benchmark_sweep.py
experiments/03_real_data/script_07_validation.py
```

Every run adds one row to the `Current state` table in `analysis/ITERATION_LOG.md`:

| Iteration | Date | Script | Hypotheses | Kind | Changed from | Outcome |
|---|---|---|---|---|---|---|
| 03 | 2024-01-15 | `script_03_baseline` | HYPOTHESIS_01 | single | — | [Record after interpreting] |
| 04 | 2024-01-18 | `script_04_activation_panel` | HYPOTHESIS_01 | panel (8) | 03 | [Record after interpreting] |

`record_outcome.py` replaces that placeholder once you have interpreted the run. `Outcome`
is prose, not a keyword: a panel that improves three of eight candidates and regresses one
cannot be described by `SUPPORTED`.

### Panels

`--probes N` seeds the script with a loop over N labelled probes that reports a result for
each one. A panel result stays broken out from the moment it is produced, which is the
thing that gets lost when a panel is summarized too early.

Report every probe, including the ones that changed nothing and the ones that made things
worse. A panel where one of eight candidates helped has told you something about the other
seven, and that pattern usually transfers better than the winner.

### Continuing from an earlier attempt

`--from-iteration N` copies iteration N's script forward and re-heads it for the new
iteration, so the new attempt starts from working code. State what changed in the
`Changed from iteration NN` line: the difference between two iterations is the thing under
test, and a reader should not have to reconstruct it from a diff.

The copy gets its own `SCRIPT_NAME`, so it writes its own log rather than the earlier
iteration's.

## record_outcome.py

```bash
python3 scripts/record_outcome.py 4 --outcome "3 of 8 above criterion, 1 regression"
```

Records what an iteration turned out to show. It refuses until `analysis/ANALYSIS_NN.md`
exists, because an outcome written before the run has been interpreted is a guess.

Two things happen, and the difference is the point:

- A line is **appended** to the `Outcome history` table, always. Nothing there is ever
  edited, so a conclusion you later revise still shows what it changed from.
- The `Current state` row's outcome cell is **filled**, but only while it still holds the
  placeholder `new_iteration.py` wrote. Once it holds your prose, it is yours to change,
  and the helper says so rather than overwriting you.

So a revision appends and stops. `smairt check` then reports the row as disagreeing with
the latest history line, which is your cue to update it.

## select_result.py

```bash
python3 scripts/select_result.py 4 --claim "Activation choice drives the gain"
python3 scripts/select_result.py 4 --claim "Three activations help" --probes "probe_01,probe_03,probe_07"

# With the Paper capability, append the same selection to FINAL_MANIFEST.md
python3 scripts/select_result.py 4 --claim "Three activations help" --probes "probe_01,probe_03,probe_07" --paper
```

Creates `analysis/SELECTED_NN.md` with the claim, the iteration, and every file needed to
check it. It reads `Kind` from `analysis/ITERATION_LOG.md`; for a panel, `--probes` is
required and names which arms support the claim, so a panel is never reported as though all
of it succeeded. Supplying `--probes` for a recorded single-point iteration is also refused.

Nothing is copied and nothing is deleted. The evidence stays in `results/logs/` where it
was produced, and this record points at it; a duplicate can drift from the original, and a
pointer cannot.

It refuses when the number is not recorded as an iteration, when its script is missing,
when it has not been run, and when a selection record already exists.

With the Paper capability, `--paper` appends a detailed entry to `FINAL_MANIFEST.md` using
the same claim, script, supporting probes, and exact log path. The helper can write this
because running `select_result.py` is the researcher's explicit decision that the evidence
is reportable; it never chooses a result on its own and never edits an existing manifest
entry.

## new_utility.py

```bash
python3 scripts/new_utility.py "download benchmark" --purpose "Fetch the benchmark archive"
```

Creates `scripts/utilities/<name>.py` with logging already wired. It takes no iteration
number and adds no row, because a utility is not an attempt at the research question.

If what you are writing tests something, it is an iteration: use `new_iteration.py` so it
is numbered and recorded.

## shared/logging.py

`TeeLogger` writes to the console and a file at once, capturing stdout, stderr, warnings,
uncaught tracebacks, and an explicit `SUCCEEDED` or `FAILED` status. Generated scripts also
call `write_provenance()` before the experiment:

```python
log_path = setup_logging(SCRIPT_NAME, PROJECT_ROOT / "results" / "logs")
with TeeLogger(log_path):
    write_provenance(project_root=PROJECT_ROOT, config={})
    ...
```

That header records the Python executable and version, installed dependency versions, Git
commit when available, command-line arguments, configuration, host and visible device,
and the size and SHA-256 identity of input files. Home-directory paths are replaced with
`<HOME>` and the host name is hashed, so a shared log does not publish a username or
workstation name. Pass `input_paths=[...]` when the script uses inputs outside `data/`;
otherwise regular files under `data/` are inventoried. Checksums are cached by path, size,
and modification time so large real datasets are not re-read unchanged on every run.

Everything the run produced ends up in one unique file named
`<script_name>_<timestamp>_<microseconds>.log`. Immediate reruns cannot replace one another.
Iteration scripts also append the status and exact log path to
`analysis/RUN_HISTORY.md`, so a crash remains visible even if the iteration is rerun
successfully later. A traceback that appeared only in a terminal is not part of the
evidence; this is what stops that happening.

## shared/iterations.py

Iteration numbering, path lookup, and the append-only log writer, shared by the three
workflow helpers so they agree on where things live. Import from it if you write a helper
of your own:

```python
from scripts.shared.iterations import next_iteration_number, project_root
```

## generate_manifest.py

```bash
python3 scripts/generate_manifest.py
python3 scripts/generate_manifest.py --output analysis/MANIFEST_2024-01-15.md
```

Prints the inventory it finds. With `--output` it writes to a new file, and refuses to
overwrite an existing one.

## monitor_template.py

```bash
python3 scripts/monitor_template.py results/progress.json --log results/logs/script_01_baseline_*.log
python3 scripts/monitor_template.py results/progress.json --watch --interval 60
```

Reads a JSON progress file an experiment writes, and optionally summarizes the tail of a
log. It observes only: it does not start, stop, or manage a process or a scheduler job.

## Adding helpers

Project-specific utilities belong in `scripts/shared/`, imported as
`from scripts.shared.<module> import ...`. See `scripts/shared/README.md`.

A helper may create a file that does not exist, append an entry to a record whose format
it owns, and replace a placeholder it wrote itself. It must never alter text a researcher
wrote.

That last clause is the whole rule. A helper filling its own `[Record after interpreting]`
has not overwritten anyone, and the history keeps every value regardless. A helper editing
your sentence has destroyed a conclusion, which is why it appends and tells you instead.
