# Demo: Bring Your Own Problem

**You are given:** a question worksheet.  

**You build:** everything, on your own question, using SMAIRT.

---

## Background / Why this matters

The other demos in this collection hand you a ready-made scientific question. This
track is different: **you supply the question**, from your own research, coursework,
or curiosity, and SMAIRT gives you the scaffolding and guardrails to attack it with
an AI assistant.

You do not need a polished project or even data to start. What you need is a
question that can be made **computable** (a machine can produce evidence about it),
**evaluable** (you can tell whether an answer is good), **bounded** (small enough
for one iteration), and **honest** (its assumptions and limits are stated). The
[`QUESTION_WORKSHEET.md`](QUESTION_WORKSHEET.md) walks you through shaping any rough
idea into that form. If you have no data yet, the recommended move - just like every
other demo here - is to **start synthetic**: generate data with a known, built-in
answer so you can confirm your method works before trusting it on real data.

---

### Key terms

- **SMAIRT loop:** hypothesis, ask AI for code, review, run, interpret, log, then
  repeat. One trip = one "iteration".
- **Hypothesis:** a specific, testable prediction (not just a topic).
- **Synthetic data:** data you generate with a known, built-in structure, so you
  can confirm a method works before trusting it on messy real data.
- **Breadcrumb trail:** the numbered scripts + logs + notes SMAIRT leaves behind,
  so anyone (including the AI later) can see what you tried and why.

---

## Steps

0. **Set up your environment first** (run from this folder, `bring_your_own/`):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate     # On Windows, use WSL: the SMAIRT CLI is not supported natively
   pip install -r requirements.txt
   ```
   later means this step was skipped or your venv isn't active.

   Windows users: run this demo inside WSL. The SMAIRT CLI is not supported on native
   Windows, so PowerShell activation instructions have been removed rather than left to
   imply support that does not exist.

1. **Fill in [`QUESTION_WORKSHEET.md`](QUESTION_WORKSHEET.md)** first. It forces
   your idea into a shape one SMAIRT iteration can move (computable, evaluable,
   bounded, honest). If you have no data yet, plan a synthetic-first start.

2. **Generate a fresh SMAIRT project** (run from this folder, venv active):
   ```bash
   smairt new
   ```
   Answer the guided questions one at a time, review the choices, and confirm
   creation. Suggested choices (adapt them to your problem):

   | Prompt | Suggested answer |
   |--------|------------------|
   | Project name | your project name |
   | Slug | accept or edit the generated slug |
   | Researcher | your name |
   | Email | optional |
   | Description | one line about your project |
   | Research question | your worksheet question |
   | Domain | closest field or Not sure yet |
   | Assistant | Zoo Code or your preferred supported assistant |
   | Starting phase | synthetic, downloaded, or real |
   | Optional capabilities | Paper or HPC only when needed |
   | License | MIT or another reviewed choice |
   | Git | yes when available |

   This creates a folder named after your project_slug.

3. **Write your `background/01_initial_question.md`** in the new project using
   your worksheet answers (question + what's known + data notes). You can do
   this by hand, or ask Zoo Code: *"Turn my filled-in worksheet (pasted below)
   into a `background/01_initial_question.md` with clear Question and Hypothesis
   sections, plus any additional relevant context."* Then paste your worksheet.

4. **Configure Zoo Code, then open the project in VS Code and prime it.** New to
   AI assistants? Read [`../USING_AN_AI_ASSISTANT.md`](../USING_AN_AI_ASSISTANT.md) first
   (install, sign in, attaching files, approving edits).

   Basic Zoo Code configuration for this demo:
   - Install **Zoo Code** from the VS Code Extensions panel.
   - Set **API Provider** to **OpenAI Compatible**. Any OpenAI-compatible
     endpoint works (OpenAI, Anthropic, OpenRouter, Azure OpenAI, a local server
     such as Ollama / LM Studio, or an institutional gateway).
   - Use **API Base URL**: your provider's documented base URL (for example,
     `https://api.openai.com/v1` for OpenAI).
   - Paste an **API Key** from your chosen provider.
   - Select a **Model** by difficulty. This track is **flexible**, so match the
     model to your problem's complexity: a lightweight model for simple questions,
     a larger, stronger reasoning model as the problem gets harder.
   >
   > **Markdown preview tip:** press `Cmd+Shift+V` on Mac or `Ctrl+Shift+V` on
   > Windows to render this file in VS Code.

   Open your new project folder (**File > Open Folder...**). In the Zoo Code chat,
   paste this direct prompt:

   ```text
   I'm starting a SMAIRT project to answer the question in
   background/01_initial_question.md. Please read these files before doing any
   work:
   1. prompts/AI_CONTEXT.md
   2. prompts/CODE_CONVENTIONS.md
   3. background/01_initial_question.md

   Follow the SMAIRT workflow described there. Don't write code yet. First
   summarize my question, propose a first hypothesis, and suggest an experiment
   that would produce evidence about it.
   ```

5. **Run one SMAIRT iteration.** Ask for an analysis that tests your hypothesis.
   A general-purpose first prompt:

   ```text
   Create `script_01` in the experiment folder matching the current phase.
   If I am starting synthetic-first, use `experiments/01_synthetic/`. If I am
   starting real-data-first, use `experiments/03_real_data/`. If I don't have data
   yet, generate synthetic data with a known, controllable structure so we can
   confirm the method works before using real data. Print results to console and
   capture the complete execution record in `results/logs/`.
   ```
   Then review the proposed code, approve and run it, interpret the result
   yourself, log it in `analysis/ANALYSIS_01.md`, and decide the next step. See
   more starter prompts under "Suggested starter prompts" below.

---

## Safety rails

- Review AI output before trusting it (inputs, assumptions, metric, does it
  answer the hypothesis?).
- **Data sensitivity:** do not paste restricted/proprietary/personal data into
  an external AI service. Use synthetic stand-ins or local-only tools and note
  it.

## Suggested starter prompts

See [`QUESTION_WORKSHEET.md`](QUESTION_WORKSHEET.md) for the checklist; adapt a
domain quick-start (data science / ML / general Python / "no data yet") to your
problem.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `No such file or directory: .../.venv/bin/...` | The venv was deleted/moved. Recreate it (the `python3 -m venv .venv` + install lines). |
| Your script needs a library that isn't installed | `pip install <package>` into the active venv, then re-run. |
| AI's result seems too good / circular | Check it isn't testing on the same data it learned from; ask for a held-out check. |
| Can't tell if the result answers the question | Your hypothesis or metric is probably fuzzy. Revisit the worksheet's "metric" and "what would change my mind" rows. |
| Working with sensitive data | Don't paste it into an external AI; use a synthetic stand-in or a local-only model, and note it in your log. |
| Zoo Code drifts off task | Re-attach `AI_CONTEXT.md` + your `background/01_initial_question.md` and restate the current step. |

### Zoo Code is stuck (an error a retry won't fix)

Don't keep retrying. **Start a fresh task/chat** (in Zoo Code, open a new task
with the `+` button) and re-prime it from your breadcrumb trail. Your project
files hold the context.

1. Keep your project folder open in the new task.
2. Attach `prompts/AI_CONTEXT.md`, `prompts/CODE_CONVENTIONS.md`, and your
   `background/01_initial_question.md`, then paste:

   ```text
   I'm resuming a SMAIRT project (question in background/01_initial_question.md)
   after my previous AI session got stuck. Please read AI_CONTEXT.md and
   CODE_CONVENTIONS.md and follow the SMAIRT workflow. To catch up, read my
   existing files:
   - experiments/ (numbered scripts)
   - results/logs/ (run outputs)
   - analysis/ANALYSIS_01.md (conclusions so far)
   Summarize where the project stands and the next step. Don't rewrite working
   code. Continue from here.
   ```
   to hand over the whole trail at once.
