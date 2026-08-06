# Demo: Lunar / Artemis II Free-Return

**You are given:** the background and the research question.  

**You build:** the orbital model and the free-return search using SMAIRT.

There are **no solution scripts here**. The goal is to experience using SMAIRT
to go from a question to an answer with an AI assistant.

> New to AI assistants? Read [`../USING_ZOO_CODE.md`](../USING_ZOO_CODE.md) first
> (install, sign in, attach files, approve edits).

---

## Background / Why this matters

**The field:** This is **orbital mechanics** (astrodynamics) - the physics of how
spacecraft move under gravity. It is the math NASA uses to plan every mission to
the Moon, including **Artemis II**, the crewed flight that will loop around the
Moon and return.

**The core idea:** a spacecraft in a low orbit around Earth fires its engine once
(the **trans-lunar injection**, or TLI, burn) to fling itself toward the Moon. If
the aim and speed are just right, the Moon's gravity bends the path around the far
side and slings the craft *back* to Earth with **no further engine burns** - a
**free-return** trajectory. This is exactly the safety feature that brought the
Apollo 13 crew home after their spacecraft was crippled.

---

## The question

Can you find a **Trans-Lunar Injection (TLI) burn** from a low-Earth parking orbit that produces a
**free-return** trajectory that loops behind the Moon and comes back to a low
Earth perigee with no further burns?

Full context, hypothesis, and metrics are in
[`background/01_initial_question.md`](background/01_initial_question.md).

### Key terms

- **Parking orbit:** a low circular orbit (here ~400 km altitude) where a
  spacecraft coasts before heading to the Moon.
- **TLI (trans-lunar injection) burn:** the engine firing that boosts the
  spacecraft out of its parking orbit and onto a path toward the Moon. "How much
  burn" = how much speed (delta-v) you add.
- **Free-return:** a trajectory shaped so the Moon's gravity slings the craft
  back to Earth on its own, with no return engine burn needed (the Apollo 13
  safety trick).
- **Perigee / return perigee:** the closest point to Earth; the *return* perigee
  is how close the craft comes back to Earth after the lunar flyby. Low ≈ good.
- **CR3BP (Circular Restricted Three-Body Problem):** the standard simplified
  model of a small body moving under Earth + Moon gravity, with the Moon on a
  circular orbit. Your simulator will use it.
- **Jacobi constant:** an energy-like quantity that stays fixed along a correct
  CR3BP trajectory. If your simulation conserves it, the math is trustworthy; if
  it drifts, the result is junk.
- **delta-v:** change in velocity (km/s), the standard "cost" measure for a burn.

---

## Steps

0. **Set up your environment first** (run from this folder, `lunar/`):
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
   cp lunar_free_return/background/01_initial_question.md <your-new-project>/background/
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

   Open your new `lunar_free_return/` folder in VS Code
   (**File > Open Folder...**). In the Zoo Code chat, paste this direct prompt:

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
   with an example that tests the key assumptions for the lunar free-return
   question. Create the first numbered script in experiments/01_synthetic/.

   Before writing code, briefly state what assumptions the script tests, what
   result would make those assumptions credible, and how we could scale up in
   further scripts once this first example is validated to model more and more of
   the realistic lunar free-return case. Follow the project code conventions for
   logging, figures, and the output comment block.
   ```

   How to handle the AI response:
   - If the plan tests assumptions clearly and the script is focused enough to
     review, say: `Proceed with building the script.`
   - Before running anything, check whether the code conserves the Jacobi constant,
     keeps units explicit, and measures return perigee **after** the lunar flyby.
   - If the assistant jumps straight to a final answer, redirect it:
     `Slow down. First create a focused assumption-testing script and explain the
     assumptions I should review before running it. `
   - If the run finds no free-return, prompt it further. Ask it to inspect the log,
     refine the TLI search near escape speed, and explain why the new range makes
   sense.
   - If the reported numbers look implausible, for example TLI burn far from
     ~3.1 km/s or LEO speed far from ~7.7 km/s, ask the assistant to show the unit
     conversion and compare against textbook values before continuing.

5. **Interpret and log.** In `analysis/ANALYSIS_01.md`, note: did the loop
   close? is the burn sensible? what are the model's limits (planar, point-mass,
   circular Moon)? Record your key judgment call in
   `prompts/intellectual_contribution.md`. That reasoning is the science.

---

## What "done" looks like

A trajectory that reaches the Moon and returns to a near-Earth perigee, reported
in real units with its assumptions stated honestly and reproducible from your
in Step 0; CPU-only, no network needed.)

> **Going further (optional, later):** relax the simplifying assumptions one at a
> time, for example add the Sun's perturbation or move from the planar to a 3D
> model, and report how much the required TLI burn and return perigee shift.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `No such file or directory: .../.venv/bin/...` | The venv was deleted/moved. Recreate it: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. |
| Jacobi drift is large (≫ 1e-6) | Integration is inaccurate. Ask the AI to lower solver tolerances (`rtol`/`atol`) or use a higher-order method. |
| "No free-return found" | Expected at first. Widen/refine the TLI sweep near escape speed, and integrate long enough to capture the return leg. |
| Trajectory escapes or never reaches the Moon | TLI burn too large (escapes) or too small (falls back). Narrow the sweep between those extremes. |
| Numbers look implausible (e.g. burn ≫ 3 km/s) | Check units. Mixing non-dimensional and SI is the usual culprit. Ask the AI to show the unit conversion. |
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
