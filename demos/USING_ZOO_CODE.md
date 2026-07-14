# Using Zoo Code (for first time AI users)

Zoo Code is an AI assistant built into VS Code. In these demos it reads your
project files, writes code for you, and can run commands in the terminal.
**You stay in charge**: you review and approve everything. This page explains
the setup and the few actions you'll repeat throughout a demo. No prior AI
experience needed.

---

## 1. Install Zoo Code in VS Code

1. Open **VS Code**.
2. Click the **Extensions** icon in the left sidebar (the four squares icon), or
   press `Cmd+Shift+X` (Mac) / `Ctrl+Shift+X` (Windows).
3. Search for **Zoo Code** and click **Install**.
4. When it finishes, you'll see a new **Zoo Code** icon in the left sidebar.

## 2. Sign in / connect

Zoo Code works with any OpenAI-compatible endpoint, so you can use OpenAI,
Anthropic, OpenRouter, Azure OpenAI, a local server such as Ollama or LM Studio,
or an institutional gateway. Pick whichever provider you have access to.

1. Click the **Zoo Code** icon in the left sidebar to open its chat panel.
2. Open Zoo Code settings and set **API Provider** to **OpenAI Compatible**.
3. Set **API Base URL** to your provider's documented base URL (for example,
   `https://api.openai.com/v1` for OpenAI). If you use a local server or an
   institutional gateway, use the base URL it gives you.
4. Paste an **API Key** from your chosen provider.
5. Select a **Model**. Choose it by task difficulty (see the next section).
6. You'll know it's ready when the chat box at the bottom of the panel is active
   and you can type into it.

### Choosing a model by difficulty

- **Simple / beginner tasks:** a fast, lightweight reasoning model is usually
  enough. It iterates quickly and costs less.
- **Intermediate tasks:** a mid-tier model improves multi-step reasoning and
  code quality.
- **Advanced tasks (e.g. database-backed or multi-file work):** prefer a larger,
  stronger reasoning model. Larger models tend to perform better on harder
  problems.

Start small and step up to a larger model if the assistant struggles. Each
demo's `DEMO.md` notes the difficulty of that track so you can pick accordingly.

## 3. Open your project folder

Always open the **folder of the SMAIRT project you generated** (not the whole
repo) so Zoo Code's file context is focused:

- Use **File > Open Folder...** and choose your generated project (e.g.
  `lunar_free_return/`).
- Open the built in terminal with **Terminal > New Terminal** (or
  `` Ctrl+` ``). Make sure your virtual environment is active. Your prompt
  should show `.venv`. If not, run `source .venv/bin/activate`.
- **Windows tip:** if you are using PowerShell, activate with
  `.venv\Scripts\Activate.ps1`. If PowerShell blocks scripts, run
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal
  and try the activation command again. In Command Prompt, use
  `.venv\Scripts\activate.bat`.
- **Markdown preview tip:** while viewing any `.md` instruction file in VS Code,
  press `Cmd+Shift+V` on Mac or `Ctrl+Shift+V` on Windows to render it as a
  formatted preview.

---

## 4. The three actions you'll repeat

### a) "Prime" the assistant (do this once at the start)

Priming = giving the AI the context it needs before asking for work. Open the Zoo
Code chat and paste a direct prompt telling it to read the context files from the
workspace. Use the demo-specific prompt in your `DEMO.md`, or, if you are unsure what a good iteration-1 request looks like, read [`FIRST_SCRIPT_GUIDE.md`](FIRST_SCRIPT_GUIDE.md) first. Then start with:

```text
Please read these project files before doing any work:
1. prompts/AI_CONTEXT.md: the SMAIRT method and your role
2. prompts/CODE_CONVENTIONS.md: how to format code, logs, and outputs
3. background/01_initial_question.md: my research question and background

After reading them, summarize the research question, the SMAIRT workflow rules you
will follow, and the smallest first experiment to run. Do not write code yet.
```

### b) Ask for work (one step at a time)

Type a request in plain English, e.g. *"Write a script that..."*. The assistant
will propose new files or edits. Keep requests **small and specific**. Ask for
one script or one change at a time so you can follow what it's doing. A strong
pattern for iteration 1 is: one narrow validation task, one baseline, and one
piece of output you can inspect. [`FIRST_SCRIPT_GUIDE.md`](FIRST_SCRIPT_GUIDE.md)
shows examples.

### c) Review, then approve

When Zoo Code proposes a file edit, it shows you a **diff** (green = added,
red = removed). **Read it before approving.** You can:

- **Approve / Save** to apply the change, or
- **Reject** and tell it what to fix in plain English.

When it wants to **run a command** (like `python script_01_....py`), it asks
first. Approve it to run in your terminal, and the output comes back into the
chat.

> This review step is the whole point of SMAIRT: the AI proposes, **you decide**.
> If something looks wrong, say so. That is you doing the science.

---

## 5. The SMAIRT loop, in plain terms

For each question you investigate, you repeat this cycle (your `DEMO.md` gives
demo-specific prompts for each step):

1. **Hypothesis:** write one testable sentence in a numbered file such as
   `hypotheses/HYPOTHESIS_01.md`.
2. **Ask:** request a small script from Zoo Code to test it.
3. **Review:** read the proposed code; approve or correct it.
4. **Run:** let it run the script; look at the output.
5. **Interpret:** decide what the result means in a numbered analysis file such as
   `analysis/ANALYSIS_01.md`. Was the hypothesis supported? Surprising?
6. **Next:** note the next thing to try, and repeat.

After a run, paste the output into the comment block at the bottom of the script
(Zoo Code can do this for you). That is the SMAIRT "breadcrumb trail".

---

## 6. If you get stuck

- **Assistant did something wrong?** Tell it in plain English: *"That's not
  right because... please change it to..."*. Catching mistakes is good science.
- **Command fails?** Copy the error into the chat and ask it to fix it.
- **Lost the thread?** Ask: *"Summarize what we've done so far and what the next
  step is,"* or run `python scripts/compile_for_ai.py` and paste the result back
  in.
- **`command not found`?** Your virtual environment probably isn't active. See
  step 3 above.
- **Assistant stuck in a way a retry won't fix?** Don't keep retrying. Open a
  **new task** (the `+` in Zoo Code), keep your project folder open, and re-prime
  it from your files. Your `DEMO.md` Troubleshooting section has a ready to paste
  "resume" prompt. Your work is safe on disk; SMAIRT is built to pick back up
  from the breadcrumb trail.
