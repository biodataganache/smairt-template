# Demo: Lunar free-return trajectory

**Status: current scaffold, imported history.** This is a valid SMAIRT project on the installed
scaffold and `smairt check` passes. Its three iterations were run before the current execution
record existed, so `analysis/ITERATION_LOG.md` is an imported index and `analysis/RUN_HISTORY.md`
is empty. The science and its interpretations are original; the per-execution record for those
original runs was never captured and has not been invented.

> **About the numbers in this guide.** The figures quoted below were produced by an earlier SMAIRT
> release with unpinned scientific dependencies, and no CI job re-runs this science. They record
> what the original runs reported; they are not a promise about what your machine will print. A
> small numerical difference usually means a different `numpy`/`scipy` build, not a broken demo.


**Level:** beginner. **Runtime:** seconds to a couple of minutes per iteration. CPU only, no
network, no data download.

**The question:** can a translunar-injection burn from a low-Earth parking orbit produce a
free-return — looping behind the Moon and coming back to a low Earth perigee with no further burns?

---

## Why this matters

Artemis II will fly astronauts on a lunar free-return: a path that uses only the Moon's gravity to
swing the spacecraft around the far side and back to Earth, needing no major return burn. If the
main engine failed after translunar injection, the spacecraft would still come home. That is the
principle that brought Apollo 13 back.

This project reproduces one in the planar **Circular Restricted Three-Body Problem** for the
Earth-Moon system: simplified, but physically real, and pure Python.

## What the three iterations establish

| Iteration | Hypothesis | Result |
|---|---|---|
| 01 | A free-return corridor exists and can be found by sweeping TLI speed | Supported. Corridor at 10.9270–10.9360 km/s; best case returns to 118.0 km perigee after a 23,938.3 km lunar flyby |
| 02 | A slower burn gives a direct leading-hemisphere lunar impact | Supported. Found below the free-return corridor, with Jacobi-constant drift under 1e-6 |
| 03 | A resonant burn can produce three loops before returning | **Partially supported.** Safe flight and low-Earth return achieved, but only 1.2711 loops — a physical constraint, not a bug |

Iteration 03 is the one worth reading. The prediction asked for three loops and the physics
allowed 1.27. The analysis records that as a constraint it identified rather than restating the
prediction as though it had held.

Each iteration checks the **Jacobi constant**, a quantity the CR3BP conserves. Drift below 1e-6
is what makes the trajectory a result rather than an integration artefact.

---

## Run it

From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate          # On Windows, use WSL: the SMAIRT CLI is not supported natively
pip install -r requirements.txt
cd lunar_free_return
python experiments/01_synthetic/script_01_trajectory_sweep.py
python experiments/01_synthetic/script_02_lunar_intercept.py
python experiments/01_synthetic/script_03_multi_loop_return.py
```

Iteration 01 printed the corridor `10.9270 to 10.9360 km/s` and a closest lunar approach of
`23938.3 km` when this project was recorded, under an earlier SMAIRT release and whatever
`numpy`/`scipy` versions were current then. Those figures are **not pinned and not checked by CI**,
so treat a difference as a prompt to look at your solver versions and integration tolerances rather
than as a defect. The scientific conclusion — that a free-return corridor exists and is narrow — is
what the iteration establishes.

Check the project's structure at any time:

```bash
smairt check
```

Note that these scripts predate the current generated frame: they write logs through `TeeLogger`
but do not call `record_run_status`, so running them adds nothing to `analysis/RUN_HISTORY.md`.
A project you build yourself with `new_iteration.py` will record every run there automatically.

---

## Build it yourself

```bash
smairt new
```

Answer the prompts, then seed the question:

```bash
cp lunar_free_return/background/01_initial_question.md <your-project>/background/
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

Then run the loop. The helpers own the numbering, so you never name a script yourself:

```bash
python3 scripts/new_track.py "Can a TLI burn produce a free-return trajectory?" synthetic
# Write the prediction and both criteria into hypotheses/HYPOTHESIS_01.md. Commit them.
python3 scripts/new_iteration.py "trajectory sweep" synthetic --hypothesis HYPOTHESIS_01
# Implement the science in the generated script, then run it.
# Write analysis/ANALYSIS_01.md.
python3 scripts/record_outcome.py 01 --outcome "..."
python3 scripts/select_result.py 01 --claim "..."
```

`new_track.py` deliberately does not create a script: the criteria get committed first, which is
what keeps the test a test. `record_outcome.py` refuses until the analysis exists.

Suggested sequence: sweep TLI speed for a free-return corridor, then look for a direct lunar
intercept, then try a resonant multi-loop return.

### What to watch for

- **Check a conserved quantity.** In the CR3BP that is the Jacobi constant. Without it you cannot
  tell a real trajectory from an integrator that drifted.
- **Use an event-terminated integration** for impacts, so the run stops at the surface rather than
  integrating through the Moon.
- **Watch your units.** Non-dimensional CR3BP units are easy to mix with km and km/s; the scripts
  print the conversion factors for that reason.
- **Record what the sweep resolution was.** A corridor 0.009 km/s wide is invisible at 0.05 km/s
  steps, and "no corridor found" would be the wrong conclusion.

## What "done" looks like

Criteria committed before each run, an analysis per iteration, a passing `smairt check`, and
conclusions traceable to a log in `results/logs/`. If a prediction only partly holds, say so —
iteration 03 here is the model for that.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No module named scipy` | Activate the venv and `pip install -r requirements.txt` from this folder |
| Trajectory escapes or hits Earth | TLI speed is outside the corridor. Sweep more finely; the corridor is under 0.01 km/s wide |
| Jacobi constant drifts above 1e-6 | Tighten the integrator tolerances (`rtol`/`atol`) before trusting anything else |
| Integration runs forever | No terminating event, or the trajectory is on an escape path. Cap the integration time |
| Numbers differ from those above | Check the scipy version and the integration tolerances |
| `record_outcome.py` refuses | Write `analysis/ANALYSIS_NN.md` first. An outcome before interpretation is a guess |
| Assistant edits the wrong file | Re-attach `prompts/AI_CONTEXT.md` and restate the current step |

### The assistant is stuck

Start a fresh chat rather than retrying. Attach `prompts/AI_CONTEXT.md`,
`prompts/CODE_CONVENTIONS.md`, and `background/01_initial_question.md`, then ask it to read
`experiments/`, `results/logs/`, and `analysis/ITERATION_LOG.md` and summarize where the work stands.
