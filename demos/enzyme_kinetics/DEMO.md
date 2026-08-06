# Demo: Enzyme kinetics (Michaelis-Menten)

**Level:** beginner. **Runtime:** under a minute per iteration, CPU only, no network.

**The question:** given reaction velocity measured at several substrate concentrations, what are
the enzyme's Km and Vmax, and how accurately can they be recovered when measurements are noisy?

`enzyme_kinetics/` is a completed SMAIRT project you can read and run. Use it either as a
worked example, or as the answer key while you build your own.

---

## Why this matters

Enzymes are the protein catalysts that run the chemistry of life. Feed one more substrate and its
reaction rate climbs, then levels off at a maximum set by how much enzyme is present. Two numbers
describe that curve: **Vmax**, the top speed, and **Km**, the substrate concentration giving half
of Vmax, which acts as a proxy for how tightly the enzyme binds. Enzyme kinetics underlies drug
design, metabolic engineering, and clinical diagnostics.

The model is `v = Vmax * [S] / (Km + [S])`.

## Why this demo is worth reading

The second iteration's prediction was **wrong**, and the demo keeps it that way.

The Lineweaver-Burk plot is a classical shortcut that fits `1/v` against `1/[S]` to get a straight
line. It is taught as noise-sensitive, so iteration 02 predicted it would fail before nonlinear
fitting. It did not. Nonlinear fitting failed first, at 10% noise, because the prediction assumed
a noise model the experiment did not use. Because the criteria were committed before the run, the
result reads as a finding about noise models rather than as a mistake to be quietly fixed.

That is the workflow's actual purpose. See `analysis/ANALYSIS_02.md`.

---

## Run the completed project

From this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd enzyme_kinetics
python experiments/01_synthetic/script_01_synthetic_nonlinear_fit.py
python experiments/01_synthetic/script_02_noise_lineweaver_comparison.py
python experiments/02_downloaded/script_03_puromycin_real_fit.py
```

Each run appends to `analysis/RUN_HISTORY.md` and writes a timestamped log under `results/logs/`.
Reruns never overwrite an earlier log.

Check the project's structure at any time:

```bash
smairt check
```

## What each iteration establishes

| Iteration | Hypothesis | Result |
|---|---|---|
| 01 | Nonlinear fitting recovers planted Vmax and Km within 10% at 3% noise | Supported. Vmax 2.6% error, Km 6.4% |
| 02 | Lineweaver-Burk fails the criterion at a lower noise level than nonlinear | **Not supported.** Nonlinear failed first, at 10%, on Km |
| 03 | The method gives credible parameters on the public Puromycin dataset | Supported. Treated Vmax higher, non-overlapping intervals |

Km is harder to recover than Vmax in all three, because Vmax is constrained by the plateau where
many points sit while Km depends on curvature that fewer points cover. Iteration 03 reports that
its Km confidence intervals overlap, so the Km difference between conditions is *not* claimed.

## Data

`data/downloaded/puromycin_rates.csv` is 23 rows from R's `datasets::Puromycin` (Treloar 1974).
Provenance, columns, SHA-256, and the R snippet that regenerates it are in
`data/downloaded/README.md`.

---

## Build it yourself

Create a project and let the tool own the numbering:

```bash
smairt new
```

Answer the prompts, then seed the question and open a chat with an AI assistant:

```bash
cp enzyme_kinetics/background/01_initial_question.md <your-project>/background/
```

New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) for install and setup.

Prime the assistant:

```text
I'm starting a SMAIRT project to answer the question in
background/01_initial_question.md. Read these first:
1. prompts/AI_CONTEXT.md
2. prompts/CODE_CONVENTIONS.md
3. background/01_initial_question.md

Follow the workflow described there. Don't write code yet. Summarize the question
and propose a first hypothesis with quantitative success criteria.
```

Then run the loop for each iteration:

```bash
python3 scripts/new_track.py "<your question>" synthetic     # first track only
# write the prediction and both criteria into hypotheses/HYPOTHESIS_01.md, and commit them
python3 scripts/new_iteration.py "nonlinear fit" synthetic --hypothesis HYPOTHESIS_01
# implement the science in the generated script, then run it
# write analysis/ANALYSIS_01.md
python3 scripts/record_outcome.py 01 --outcome "..."
```

`record_outcome.py` refuses until the analysis exists, and `new_track.py` deliberately does not
create a script: the criteria are committed first, which is what keeps the test a test.

Suggested sequence: synthetic recovery at low noise, then a noise sweep comparing methods with
enough replicates to report medians, then a public dataset where truth is unknown.

### What to watch for

- Report recovery error against the **planted truth**, not just R^2. On synthetic data, that
  comparison *is* the experiment.
- Offset the initial guess from the truth, or the fit may just be restating the answer.
- Use a fixed seed and record it. `write_provenance` puts the config in the log.
- Use enough replicates to report **medians**. One near-singular reciprocal fit dominates a mean.
- Write the criteria before the run. Iteration 02 is only a finding because of this.

## What "done" looks like

Three iterations with committed criteria, three analyses, one selected result, a passing
`smairt check`, and a conclusion traceable to a log in `results/logs/`. If a prediction fails,
record that it failed.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No module named scipy` | Activate the venv and `pip install -r requirements.txt` from this folder |
| Fit does not converge | Initial guesses are far off. Seed Km near the `[S]` of half-max and Vmax near the largest observed velocity |
| Fitted Vmax keeps climbing | The substrate range never saturates. Extend `[S]` well above Km |
| Lineweaver-Burk looks fine | Expected at low noise, and at moderate noise too. See `analysis/ANALYSIS_02.md` |
| Results change every run | No fixed seed. Set one and record it in `CONFIG` |
| `record_outcome.py` refuses | Write `analysis/ANALYSIS_NN.md` first. An outcome before interpretation is a guess |
| Assistant edits the wrong file | Re-attach `prompts/AI_CONTEXT.md` and restate the current step |

### The assistant is stuck

Start a fresh chat rather than retrying. Your project files hold the context: attach
`prompts/AI_CONTEXT.md`, `prompts/CODE_CONVENTIONS.md`, and
`background/01_initial_question.md`, then ask it to read `experiments/`, `results/logs/`, and
`analysis/ITERATION_LOG.md` and summarize where the work stands.
