# Demo: Peptide digestion (in-silico trypsin)

**Status: current scaffold, imported history.** This is a valid SMAIRT project on the installed
scaffold and `smairt check` passes. Its three iterations were run before the current execution
record existed, so `analysis/ITERATION_LOG.md` is an imported index and `analysis/RUN_HISTORY.md`
is empty. The science and its interpretations are original; the per-execution record for those
original runs was never captured and has not been invented.

> **About the numbers in this guide.** The figures quoted below were produced by an earlier SMAIRT
> release, and no CI job re-runs this science. They record what the original runs reported. This demo
> is pure standard library apart from one plot, so its results are deterministic and a difference
> would indicate a real change in the digestion rules rather than a numerical library version.


**Level:** beginner. **Runtime:** under a second per iteration. Pure standard library except for
one plot. No network, no data download.

**The question:** for a given protein sequence, what peptides does trypsin produce, and which fall
in the mass and length window a mass spectrometer can actually observe?

---

## Why this matters

In bottom-up proteomics, proteins are not measured directly. They are cut into peptides by a
protease — almost always trypsin — and the mass spectrometer measures the peptides. To know which
protein a measurement came from, you have to predict what peptides trypsin *would* produce. This
in-silico digestion underpins every database search.

## Why this is a good first demo

The rules are deterministic, so **"correct" is unambiguous**. You can write the expected peptides
for a short sequence by hand and check exact equality. Most science does not offer that, and it
makes this the cleanest place to learn the loop: when an iteration fails here, the method is
wrong, not the statistics.

## What the three iterations establish

| Iteration | Hypothesis | Result |
|---|---|---|
| 01 | Rule-based digestion reproduces hand-curated peptides exactly | Supported. Exact match on curated cases |
| 02 | The digester handles missed cleavages for N = 0, 1, 2 | Supported. Verified against hand-curated expectations |
| 03 | Mass and length filtering selects the observable peptides | Supported. Bounds behaved as predicted |

Trypsin cuts after lysine (K) and arginine (R), except when followed by proline (P). Real
digestion is rarely complete, which is why iteration 02 adds **missed cleavages**: allowing
trypsin to skip up to N valid sites and merge adjacent peptides. Iteration 03 then keeps only
peptides a spectrometer can see, filtering on length and mass.

---

## Run it

From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate          # On Windows, use WSL: the SMAIRT CLI is not supported natively
pip install -r requirements.txt
cd peptide_digest
python experiments/01_synthetic/script_01_tryptic_digestion_smoke_test.py
python experiments/01_synthetic/script_02_missed_cleavages_validation.py
python experiments/01_synthetic/script_03_peptide_filtration.py
```

Check the project's structure at any time:

```bash
smairt check
```

These scripts predate the current generated frame: they log through `TeeLogger` but do not call
`record_run_status`, so running them adds nothing to `analysis/RUN_HISTORY.md`. A project you build
with `new_iteration.py` records every run there automatically.

---

## Build it yourself

```bash
smairt new
```

Answer the prompts, then seed the question:

```bash
cp peptide_digest/background/01_initial_question.md <your-project>/background/
```

New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first.

Prime the assistant before asking for code:

```text
I'm starting a SMAIRT project to answer the question in
background/01_initial_question.md. Read these first:
1. prompts/AI_CONTEXT.md
2. prompts/CODE_CONVENTIONS.md
3. background/01_initial_question.md

Follow the workflow described there. Don't write code yet. Summarize the question
and propose a first hypothesis with quantitative success criteria.
```

Then run the loop. The helpers own the numbering:

```bash
python3 scripts/new_track.py "What peptides does trypsin produce from a sequence?" synthetic
# Write the prediction and both criteria into hypotheses/HYPOTHESIS_01.md. Commit them.
python3 scripts/new_iteration.py "tryptic digestion smoke test" synthetic --hypothesis HYPOTHESIS_01
# Implement the science in the generated script, then run it.
# Write analysis/ANALYSIS_01.md.
python3 scripts/record_outcome.py 01 --outcome "..."
python3 scripts/select_result.py 01 --claim "..."
```

`new_track.py` deliberately does not create a script: the criteria get committed first.
`record_outcome.py` refuses until the analysis exists.

Suggested sequence: exact digestion against hand-curated cases, then missed cleavages, then
observability filtering.

### What to watch for

- **Write the expected peptides by hand first.** The whole value of this problem is that you can.
  A test whose expectation came from the code proves nothing.
- **Get the proline rule right.** Trypsin does not cut K or R when followed by P. This is the most
  common bug, and a hand-curated case containing `KP` will catch it.
- **Check the terminal peptide.** Off-by-one errors hide at the sequence end, where there is no
  following residue to test.
- **Use monoisotopic masses and say so.** Average masses give different numbers; mixing them
  silently shifts every result.
- **Count, don't eyeball.** Missed cleavages at N=2 produce more peptides than you expect; assert
  the count against a hand calculation.

## What "done" looks like

Criteria committed before each run, an analysis per iteration, a passing `smairt check`, and
conclusions traceable to a log in `results/logs/`. Because correctness is exact here, an iteration
either matches its curated expectation or it does not — record which.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Peptide list has one too many or too few | Off-by-one at a terminus, or the proline exception is not applied |
| Masses disagree with published values | Monoisotopic versus average masses, or the water mass for the peptide terminus is missing |
| Missed-cleavage counts look wrong | At N=2 the count grows faster than intuition suggests. Check against a hand calculation on a short sequence |
| Everything is filtered out | Mass and length bounds are too tight, or masses are in the wrong units |
| `No module named matplotlib` | Only iteration 03's plot needs it. `pip install -r requirements.txt` |
| `record_outcome.py` refuses | Write `analysis/ANALYSIS_NN.md` first. An outcome before interpretation is a guess |
| Assistant edits the wrong file | Re-attach `prompts/AI_CONTEXT.md` and restate the current step |

### The assistant is stuck

Start a fresh chat rather than retrying. Attach `prompts/AI_CONTEXT.md`,
`prompts/CODE_CONVENTIONS.md`, and `background/01_initial_question.md`, then ask it to read
`experiments/`, `results/logs/`, and `analysis/ITERATION_LOG.md` and summarize where the work stands.
