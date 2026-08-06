# Demo: Proteomics Differential Abundance

> ### Status: legacy
>
> **Read this demo for its scientific reasoning, not as a guide to the current workflow.**
>
> Its science still runs — the dependencies are declared and correct, and the analyses are sound.
> But the completed project below predates the current toolkit, so it is not a SMAIRT project the
> installed tool recognises: it has no `smairt.yaml`, `smairt check` will refuse it, and it still
> ships retired helpers (`new_script.py`, `new_experiment.py`, `finalize_iteration.py`) that the
> current scaffold does not create.
>
> The steps in this file describe hand-creating numbered scripts. That is not how the current
> workflow works. Today a track starts with `scripts/new_track.py`, iterations come from
> `scripts/new_iteration.py`, outcomes are recorded with `scripts/record_outcome.py`, and
> reportable results with `scripts/select_result.py` — so numbering is the tool's job, not yours.
>
> **For the current workflow**, see [`../enzyme_kinetics/DEMO.md`](../enzyme_kinetics/DEMO.md)
> (fully current), [`../lunar/DEMO.md`](../lunar/DEMO.md), or
> [`../peptide_digest/DEMO.md`](../peptide_digest/DEMO.md), and
> [`../../docs/workflow.md`](../../docs/workflow.md).


**You are given:** the background and the research question.

**You build:** the synthetic data generator and the differential-abundance
analysis using SMAIRT.

There are **no solution scripts here**. The goal is to experience using SMAIRT
to go from a question to an answer with an AI assistant, on a biology workflow
that lets you iterate a few times.

> New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first
> (install, sign in, attach files, approve edits).

---

## Background / Why this matters

**The field:** In **proteomics**, a common experiment measures how much of each
protein is present in two conditions - say, cells with a drug (**treated**)
versus without it (**control**) - across thousands of proteins at once. The goal
is to find which proteins genuinely change, a task called **differential
abundance analysis**. The same statistical machinery is used across genomics,
transcriptomics, and much of modern biology.

**The core idea:** for each protein you run a statistical test asking "is the
difference between conditions bigger than random noise?" The catch: when you test
*thousands* of proteins at once, some will look "significant" by pure chance. So
you must correct for **multiple testing** (the Benjamini-Hochberg / FDR
procedure) to keep the fraction of false discoveries under control. A **volcano
plot** then shows which proteins are both strongly and reliably changed.

---

## The question

Given a two-condition protein-abundance matrix (e.g. **treated vs. control**),
which proteins are **differentially abundant**, and how well can a per-protein
test plus multiple-testing correction **recover the proteins we know are truly
changed** while controlling false positives?

Full context, hypothesis, and metrics are in
[`background/01_initial_question.md`](background/01_initial_question.md).

### Key terms

- **Differential abundance:** a protein whose measured level genuinely differs
  between conditions (not just noise).
- **Synthetic data with a planted answer:** you generate the matrix yourself and
  decide in advance which proteins are truly changed, so you can check whether
  the analysis recovers them before trusting it on real data.
- **p-value:** the chance of seeing a difference this large if nothing really
  changed. Small = surprising under "no change".
- **Multiple testing / FDR:** testing thousands of proteins at p < 0.05 yields
  many false positives by chance. Benjamini-Hochberg (BH) correction controls
  the **false-discovery rate** (the expected fraction of your hits that are
  wrong).
- **Volcano plot:** log2 fold-change (x) vs. -log10 p-value (y); the standard
  visual for "big *and* significant" changes.
- **Recall:** the fraction of the truly-changed proteins your analysis found.

---

## Steps

0. **Set up your environment first** (run from this folder,
   `proteomics_de/`):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate     # Windows PowerShell: .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   This installs only the scientific Python dependencies for the demo.


   Windows users: if PowerShell blocks activation, run
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal,
   then try `.venv\Scripts\Activate.ps1` again. In Command Prompt, use
   `.venv\Scripts\activate.bat`.

1. **Create a fresh SMAIRT project** with the installed CLI:
   ```bash
   smairt new
   ```
   Use the guided prompts to choose the demo name, research question, domain,
   starting phase, and assistant. The installed `smairt` command is the only
   supported generator.



2. **Seed your project with the background:**
   ```bash
   cp proteomics_de/background/01_initial_question.md <your-new-project>/background/
   ```

3. **Configure Zoo Code, then open the project in VS Code and prime it.** New to
   AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first. It
   covers installing Zoo Code, signing in, and how to attach files and approve
   edits.

   Basic Zoo Code configuration for this demo:
   - Install **Zoo Code** from the VS Code Extensions panel.
   - Set **API Provider** to **OpenAI Compatible**. Any OpenAI-compatible
     endpoint works (OpenAI, Anthropic, OpenRouter, Azure OpenAI, a local server
     such as Ollama / LM Studio, or an institutional gateway).
   - Use **API Base URL**: your provider's documented base URL (for example,
     `https://api.openai.com/v1` for OpenAI).
   - Paste an **API Key** from your chosen provider.
   - Select a **Model** by difficulty. This is an **advanced** track, so prefer a
     larger, stronger reasoning model for the statistics, multiple-testing, and
     higher-fidelity noise/missingness steps. Larger models tend to perform better
     on this kind of multi-iteration statistical work.
   >
   > **Markdown preview tip:** press `Cmd+Shift+V` on Mac or `Ctrl+Shift+V` on
   > Windows to render this file in VS Code.

   Open your new project folder in VS Code (**File > Open Folder...**). In the
   Zoo Code chat, paste this direct prompt:

   ```text
   I'm starting a SMAIRT project to answer the question in
   background/01_initial_question.md. Please read these files before doing any
   work:
   1. prompts/AI_CONTEXT.md
   2. prompts/CODE_CONVENTIONS.md
   3. background/01_initial_question.md

   Follow the SMAIRT workflow described there: numbered scripts, output to console
   + results/logs/; use the tracked raw log as the execution record.
   Don't write any code yet. First summarize the question and propose a first
   hypothesis and an experiment to test it.
   ```

   Read its reply. You decide whether the proposed hypothesis/experiment is
   reasonable before moving on.

4. **Start the SMAIRT loop with one focused request.** After the assistant has
   summarized the question and proposed a first hypothesis, paste a prompt like
   this. Treat the reply as a proposal: you may accept, narrow, or redirect it.

   ```text
   Based on background/01_initial_question.md and the SMAIRT conventions, start
   with a synthetic-data example that tests the key assumptions for the
   differential-abundance question. Create the first numbered script in
   experiments/01_synthetic/ that (a) generates a protein-abundance matrix where
   I KNOW which proteins are truly changed, (b) runs a per-protein t-test, and
   (c) reports recall and the observed false-discovery rate against that known
   truth.

   Before writing code, briefly state what assumptions the script tests, what
   result would make those assumptions credible, and how we could make later
   scripts more realistic. Follow the project code conventions for logging,
   figures, and the output comment block.
   ```

   How to handle the AI response:
   - If the plan tests assumptions clearly and the script is focused enough to
     review, say: `Proceed with building the script.`
   - Before trusting results, check that the analysis runs on **log2**
     intensities, uses a **fixed random seed**, and compares results **against
     the planted truth** (recall + observed FDR), not just a count of hits.
   - If the assistant jumps straight to "here are the significant proteins",
     redirect it: `Slow down. First confirm on synthetic data that we recover the
     planted proteins at the chosen FDR before interpreting any hit list.`
   - **Second iteration:** ask it to add Benjamini-Hochberg correction and show
     how many false positives appear *without* it. This is the core lesson and a
     natural next loop.
   - **Third iteration:** ask it to add missing values (proteins not detected in
     some samples) and decide filter vs. impute, then re-check recall/FDR.

5. **Interpret and log.** In `analysis/ANALYSIS_01.md`, note: did BH control
   the observed FDR near the threshold? what was recall? what broke when you
   added missing values? Record your key judgment call (e.g. your imputation
   choice and why) in `prompts/intellectual_contribution.md`. That reasoning is
   the science.

---

## What "done" looks like

On synthetic data: a volcano plot with the planted true positives highlighted, a
reported recall and observed FDR that track your BH threshold, and an honest note
on what the missing-value handling did. Reproducible from your breadcrumb trail.
installed in Step 0; CPU-only, no network needed.)

> **Going further (optional, later):** once the synthetic workflow is solid, you
> can swap in a small real `proteinGroups`-style intensity table. The ground
> truth is no longer known, so you shift from "recall" to reasoning about effect
> sizes and prior biology. State that shift honestly in your log.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `No such file or directory: .../.venv/bin/...` | The venv was deleted/moved. Recreate it: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. |
| Almost everything is "significant" | You're testing raw p-values without correction. Add Benjamini-Hochberg FDR; recount hits. |
| Recall is ~0 even on synthetic data | Effect size too small vs. noise, or you tested on raw (not log2) intensities. Increase planted fold-change or fix the transform. |
| Observed FDR is far above your threshold | Correction not applied, or applied per-comparison instead of across all proteins. Ask the AI to apply BH across the full p-value vector. |
| Results change every run | No fixed random seed. Set and log a seed so the synthetic truth is reproducible. |
| t-test errors on proteins with missing values | Filter proteins with too few observations, or impute before testing; state which and why. |
| Zoo Code edits the wrong file / drifts | Re-attach `AI_CONTEXT.md` + your `background/01_initial_question.md` and restate the current step. |

### Zoo Code is stuck (an error a retry won't fix)

If the assistant gets into a broken state, don't keep retrying. **Start a fresh
task/chat** (in Zoo Code, open a new task with the `+` button) and re-prime it
from your breadcrumb trail. SMAIRT is designed for exactly this: your project
files hold the context.

1. Save your work (your scripts/logs are already on disk).
2. Open the new task with your project folder still open.
3. Attach `prompts/AI_CONTEXT.md`, `prompts/CODE_CONVENTIONS.md`, and
   `background/01_initial_question.md`, then paste:

   ```text
   I'm resuming a SMAIRT project (the question is in
   background/01_initial_question.md) after my previous AI session got stuck.
   Please read AI_CONTEXT.md and CODE_CONVENTIONS.md and follow the SMAIRT
   workflow. To get back up to speed, read my existing files:
   - experiments/ (my numbered scripts so far)
   - results/logs/ (run outputs)
   - analysis/ANALYSIS_01.md (what I concluded so far)
   Summarize where the project stands and what the next step is. Don't rewrite
   working code. Continue from here.
   ```
   to hand over the whole trail at once.
