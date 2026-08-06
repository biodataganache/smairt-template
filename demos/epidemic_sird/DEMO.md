# Demo: Epidemic Modeling (SIRD Infection-Recovery-Death)

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

**You build:** the SIRD compartmental model and the outbreak analysis using
SMAIRT.

There are **no solution scripts here**. The goal is to experience using SMAIRT
to go from a question to an answer with an AI assistant, on a small, checkable
epidemic-modeling problem you can iterate on.

> New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first
> (install, sign in, attach files, approve edits).

---

## Background / Why this matters

**The field:** When a new infectious disease appears, public-health teams must
forecast how fast it will spread, whether hospitals will be overwhelmed, and how
many people will recover or die. The classic tool is a **compartmental model** -
a small set of **differential equations** describing how people move between
states of an epidemic over time. These models informed real decisions during
COVID-19, influenza pandemics, and Ebola outbreaks.

**The core idea:** the **SIRD** model splits a population into four groups -
**S**usceptible (can catch it), **I**nfected (sick and contagious),
**R**ecovered (immune), and **D**eceased - and writes a rate equation for each.
People flow S -> I as the disease transmits, then I -> R or I -> D. A single
number, the **basic reproduction number R0**, predicts the outcome: if each
infected person infects more than one other on average (R0 > 1), the outbreak
grows to a peak; if fewer (R0 < 1), it fades. Because the population is closed,
the totals must always add up (S + I + R + D stays constant), which gives a
built-in way to check that the math is right.

---

## The question

Given infection, recovery, and death rates, how does a SIRD outbreak evolve -
what is the **peak number simultaneously infected** and when does it occur, and
what fraction of the population ends up **recovered versus deceased** - and does
the epidemic grow or fade as predicted by **R0**?

Full context, hypothesis, and metrics are in
[`background/01_initial_question.md`](background/01_initial_question.md).

### Key terms

- **Compartmental model:** a model that divides a population into states and
  writes a differential equation for the flow between them.
- **S, I, R, D:** Susceptible, Infected, Recovered, Deceased - the four SIRD
  compartments. Their sum is the (constant) total population `N`.
- **beta (infection rate):** how quickly susceptible people become infected on
  contact with infected people.
- **gamma (recovery rate):** rate at which infected people recover; `1/gamma` is
  the mean infectious period.
- **mu (death rate):** rate at which infected people die from the disease.
- **R0 (basic reproduction number):** `beta / (gamma + mu)`; average new
  infections caused by one case. `R0 > 1` grows, `R0 < 1` fades.
- **Epidemic peak:** the maximum of `I(t)` - the moment the most people are sick
  at once (the "flatten the curve" target).
- **Conservation check:** `S + I + R + D = N` at all times; a built-in test that
  the numerical solution is correct.
- **Numerical ODE solver:** the SIRD system is nonlinear with no closed-form
  solution, so it is integrated numerically (e.g. `scipy.integrate.solve_ivp`).

---

## Steps

0. **Set up your environment first** (run from this folder, `epidemic_sird/`):
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
   cp sird_epidemic_model/background/01_initial_question.md <your-new-project>/background/
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
   - Select a **Model** by difficulty. This is an **intermediate** track, so a
     mid-tier reasoning model is a good default for the model implementation and
     the R0 / parameter-sweep analysis. Step up to a larger model if the assistant
     struggles.
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
   with a single, checkable scenario. Create the first numbered script in
   experiments/01_synthetic/ that (a) implements the SIRD equations with the
   suggested parameters (N, beta, gamma, mu, one infected seed), (b) integrates
   them over time with a numerical ODE solver, and (c) verifies that
   S + I + R + D stays equal to N at every step and plots the four curves.

   Before writing code, briefly state the parameters you'll use, what would make
   the result credible (the conservation check plus a sensible epidemic shape),
   and how later scripts will sweep beta to vary R0. Follow the project code
   conventions for logging, figures, and the output comment block.
   ```

   How to handle the AI response:
   - If the plan integrates the SIRD system and checks conservation, say:
     `Proceed with building the script.`
   - Before trusting results, check that **S + I + R + D = N** holds to numerical
     tolerance at all times, that the compartments stay non-negative, and that the
     computed **R0 = beta / (gamma + mu)** is reported alongside the curves.
   - If the assistant only plots curves without the conservation check, redirect
     it: `Add the S+I+R+D = N conservation check as an explicit assertion; that is
     how we validate the solver.`
   - **Second iteration:** sweep `beta` (hence R0) and show the infected peak
     growing and shifting; locate the R0 = 1 threshold that separates a growing
     outbreak from one that fades immediately.
   - **Third iteration:** report the **final size** (fraction Recovered vs.
     Deceased at long time) as `mu` changes, and discuss the "flatten the curve"
     interpretation of lowering `beta`.

5. **Interpret and log.** In `analysis/ANALYSIS_01.md`, note: did S+I+R+D stay
   conserved? what was the peak infected count and its timing? did the outbreak
   grow when R0 > 1 and fade when R0 < 1? how did the recovered/deceased split
   change with the death rate? Record your key judgment call (e.g. which
   intervention - lowering beta vs. shortening the infectious period - you'd
   prioritize, and why) in `prompts/intellectual_contribution.md`. That reasoning
   is the science.

---

## What "done" looks like

A working SIRD model whose S, I, R, D curves conserve the total population, a
clear demonstration that the outbreak grows when R0 > 1 and fades when R0 < 1, a
reported epidemic peak (size and timing) and final recovered-vs-deceased split,
and a parameter-sweep plot showing how the infected peak shifts with `beta`, all
numpy/scipy/matplotlib, installed in Step 0; CPU-only, no network needed.)

> **Going further (optional, later):** fit `beta`, `gamma`, and `mu` to a small
> published outbreak time series (e.g. an early COVID-19 or influenza curve),
> report the estimated R0 with its uncertainty, and state the model's limitations
> honestly.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `No such file or directory: .../.venv/bin/...` | The venv was deleted/moved. Recreate it: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. |
| S + I + R + D drifts away from N | Solver tolerance too loose or a sign error in the equations. Tighten `rtol`/`atol` and re-check the flow terms. |
| A compartment goes negative | Step too large or wrong sign; use an adaptive solver (`solve_ivp`) and verify `dS/dt` is negative, `dD/dt`/`dR/dt` non-negative. |
| No epidemic peak appears | With R0 < 1 that's correct (outbreak fades). To see a peak, raise `beta` so R0 = beta/(gamma+mu) > 1. |
| Infected count explodes past N | The `S*I/N` normalization is likely missing. The transmission term must divide by `N`. |
| Curves look right but R0 seems off | Recompute `R0 = beta / (gamma + mu)`; make sure the death rate `mu` is included in the denominator. |
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
