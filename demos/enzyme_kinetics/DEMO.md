# Demo: Enzyme Kinetics (Michaelis-Menten)

**You are given:** the background and the research question.

**You build:** the synthetic data generator and the Km/Vmax fitting using
SMAIRT.

There are **no solution scripts here**. The goal is to experience using SMAIRT
to go from a question to an answer with an AI assistant, on a small biochemistry
problem you can iterate on.

> New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first
> (install, sign in, attach files, approve edits).

---

## Background / Why this matters

**The field:** Enzymes are the protein catalysts that run the chemistry of life,
speeding up reactions in your cells by orders of magnitude. **Enzyme kinetics**
is the study of *how fast* an enzyme works and *how* that speed changes as you
give it more raw material (substrate). It is one of the oldest and most practical
corners of biochemistry: it underlies drug design (many drugs are enzyme
inhibitors), metabolic engineering, and clinical diagnostics.

**The core idea in one picture:** if you feed an enzyme more and more substrate,
its reaction rate climbs quickly at first, then levels off. It cannot go faster
than a maximum speed set by how much enzyme is present. Two numbers capture this
curve: **Vmax** (the top speed) and **Km** (how much substrate you need to reach
half of that top speed, a proxy for how tightly the enzyme grabs its substrate).

---

## The question

Given measurements of reaction velocity (v) at several substrate concentrations
([S]), what are the enzyme's **Km and Vmax**, and how accurately can we recover
them, especially when the measurements are noisy?

Full context, hypothesis, and metrics are in
[`background/01_initial_question.md`](background/01_initial_question.md).

### Key terms

- **Michaelis-Menten kinetics:** the standard model of enzyme rate vs. substrate:
  `v = Vmax * [S] / (Km + [S])`. Rate rises, then saturates.
- **Vmax:** the maximum reaction rate when the enzyme is fully saturated.
- **Km:** the substrate concentration that gives half of Vmax; a measure of how
  tightly the enzyme binds its substrate.
- **Nonlinear least-squares fit:** fitting the curved equation directly to the
  data (e.g. `scipy.optimize.curve_fit`). The modern, preferred method.
- **Lineweaver-Burk plot:** an old shortcut that plots 1/v vs. 1/[S] to make a
  straight line. Easy by hand, but the reciprocals amplify noise and bias the
  estimate, which this demo shows.
- **Synthetic data with known truth:** you generate v from Km/Vmax you choose, so
  you can check whether your fit recovers them before using real data.

---

## Steps

0. **Set up your environment first** (run from this folder,
   `enzyme_kinetics/`):

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
   cp background/01_initial_question.md enzyme_kinetics/background/
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
   - Select a **Model** by difficulty. This is a **beginner** track, so a fast,
     lightweight reasoning model is usually plenty. Step up to a larger model
     only if the assistant struggles.
   >
   > **Markdown preview tip:** press `Cmd+Shift+V` on Mac or `Ctrl+Shift+V` on
   > Windows to render this file in VS Code.
   >

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
   with a synthetic example. Create the first numbered script in
   experiments/01_synthetic/ that (a) generates velocity-vs-substrate data from
   KNOWN Km and Vmax with a little noise, (b) fits Km and Vmax with a nonlinear
   least-squares fit, and (c) reports how close the fitted values are to the
   known truth, with a plot of the fitted curve over the data.

   Before writing code, briefly state the true parameters you'll plant, what
   recovery error would make the method credible, and how later scripts will
   raise the noise and add the Lineweaver-Burk comparison. Follow the project code
   conventions for logging, figures, and the output comment block.
   ```

   How to handle the AI response:

   - If the plan plants known parameters and checks recovery against them, say:
     `Proceed with building the script.`
   - Before trusting results, check it uses a **fixed random seed**, sensible
     initial guesses for the fit, and compares fitted Km/Vmax **against the
     planted truth**, not just an R^2.
   - If the assistant only reports an R^2 with no truth comparison, redirect it:
     `On synthetic data, report the recovery error against the known Km and Vmax; that is the experiment.`
   - **Second iteration:** raise the noise and compare nonlinear fit vs.
     Lineweaver-Burk parameter recovery; show the linearized method's bias.
   - **Third iteration:** generate data with a competitive or noncompetitive
     inhibitor and confirm the expected shift in apparent Km/Vmax.
5. **Interpret and log.** In `analysis/ANALYSIS_01.md`, note: how well did each
   method recover Km/Vmax? at what noise level did Lineweaver-Burk break down?
   did the inhibition model behave as predicted? Record your key judgment call
   (e.g. which method you trust and why) in
   `prompts/intellectual_contribution.md`. That reasoning is the science.

---

## What "done" looks like

On synthetic data: fitted Km/Vmax that recover the planted truth within a small
error, a clear demonstration that the nonlinear fit beats Lineweaver-Burk as
noise grows, and a fitted-curve plot, all reproducible from your breadcrumb
Step 0; CPU-only, no network needed.)

> **Going further (optional, later):** fit a small published v-vs-[S] dataset.
> Truth is unknown, so report confidence intervals and compare to literature
> values; state that shift honestly in your log.

---

## Troubleshooting

| Symptom                                            | Likely cause / fix                                                                                                                 |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `No such file or directory: .../.venv/bin/...`   | The venv was deleted/moved. Recreate it:`python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. |
| Fit doesn't converge / gives nonsense              | Bad initial guesses. Seed Km near the [S] of half-max and Vmax near the highest observed v.                                        |
| Fitted Vmax keeps climbing                         | Substrate range doesn't reach saturation. Extend [S] well above Km so the plateau is sampled.                                      |
| Lineweaver-Burk looks as good as the nonlinear fit | Noise is too low to expose the bias. Increase noise; the reciprocal plot should degrade faster.                                    |
| Results change every run                           | No fixed random seed. Set and log a seed so the synthetic truth is reproducible.                                                   |
| Inhibition iteration shows no change               | Check which parameter the model should move (competitive -> Km up; noncompetitive -> Vmax down) and that the generator applies it. |
| Zoo Code edits the wrong file / drifts             | Re-attach`AI_CONTEXT.md` + your `background/01_initial_question.md` and restate the current step.                              |

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

