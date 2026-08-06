# Using an AI assistant with a SMAIRT demo

SMAIRT projects are plain files — Markdown, Python, YAML — so any coding assistant can work in
one, and none is required. This page explains the handful of actions you repeat in every demo,
in terms that apply whichever assistant you chose when you created the project.

**You stay in charge.** The assistant proposes; you review and approve. That review step is not
overhead, it is the science.

New to this and want click-by-click setup instructions? [`USING_ZOO_CODE.md`](USING_ZOO_CODE.md)
walks through one specific assistant, Zoo Code in VS Code, from installation onward. The workflow
below is the same either way.

---

## Before you start

Whichever assistant you use, get these three things true:

1. **The assistant can read your project folder.** Open the generated project directory itself
   (for example `lunar_free_return/`), not the whole demos repository. A narrower folder means the
   assistant reads the right files.
2. **Your virtual environment is active.** Your shell prompt should show `.venv`. If it does not,
   run `source .venv/bin/activate`.
3. **You are on a supported platform.** macOS, Linux, or Windows via WSL. The SMAIRT CLI is not
   supported on native Windows, so every documented command assumes a POSIX shell.

SMAIRT recorded your assistant choice when the project was created. `smairt settings` shows it,
and `smairt settings --assistant <name>` changes it.

## Choosing a model

Match the model to the work, not to the price list:

- **Simple or beginner tasks:** a fast, lightweight model is usually enough, and it iterates
  quickly.
- **Intermediate tasks:** a mid-tier model noticeably improves multi-step reasoning and code
  quality.
- **Advanced work spanning several files:** prefer a larger reasoning model.

Start small and step up if the assistant struggles. Each `DEMO.md` states the difficulty of that
track so you can choose deliberately.

---

## The three actions you repeat

### 1. Prime the assistant, once at the start

Priming means giving the assistant its context before asking for any work. Every SMAIRT project
ships the files it needs:

```text
Please read these project files before doing any work:
1. prompts/AI_CONTEXT.md: the SMAIRT method and your role
2. prompts/CODE_CONVENTIONS.md: how to format code, logs, and outputs
3. background/01_initial_question.md: my research question and background

After reading them, summarize the research question, the SMAIRT workflow rules you
will follow, and the smallest first experiment to run. Do not write code yet.
```

Each `DEMO.md` gives a priming prompt tuned to that demo. If you are unsure what a good first
request looks like, read [`FIRST_SCRIPT_GUIDE.md`](FIRST_SCRIPT_GUIDE.md).

### 2. Ask for one thing at a time

Request work in plain English, and keep each request small and specific — one script, or one
change. Small steps are followable steps, and a change you can follow is a change you can check.

### 3. Review before you approve

The assistant will show you proposed edits as a diff, and will ask before running a command.
Read the diff. Then approve it, or say plainly what is wrong and what it should be instead.

> This is the whole point of SMAIRT: the assistant proposes, **you decide**. Catching a mistake
> is not a setback; it is the part that makes the result yours.

---

## The SMAIRT loop, in plain terms

For each question you investigate, you repeat one cycle. Your `DEMO.md` supplies demo-specific
prompts for each step.

1. **Hypothesise.** Write one testable sentence in a numbered file such as
   `hypotheses/HYPOTHESIS_01.md`.
2. **Ask.** Request a small script that tests it.
3. **Review.** Read the proposed code, then approve or correct it.
4. **Run.** Execute the script and look at the output.
5. **Interpret.** Record what the result means in a numbered file such as
   `analysis/ANALYSIS_01.md`. Was the hypothesis supported? Was anything surprising?
6. **Decide what is next**, and repeat.

Every run writes a complete record to `results/logs/`. That log is the evidence behind the result,
and it is what lets you answer "why do we believe this?" six months later.

---

## If you get stuck

| Situation | What to do |
|---|---|
| The assistant did something wrong | Say so plainly: *"That is not right because… please change it to…"* |
| A command failed | Paste the error into the chat and ask for a fix |
| You lost the thread | Ask it to summarise what you have done so far and what the next step is |
| `command not found` | Your virtual environment is probably inactive; run `source .venv/bin/activate` |
| The assistant is stuck in a loop a retry will not fix | Stop retrying. Start a fresh conversation, keep the project folder open, and re-prime it from your files. Each `DEMO.md` has a ready-to-paste resume prompt |

Your work is safe on disk. SMAIRT is built so that a new conversation can pick the thread back up
from the files, because the files — not the chat history — are the record.
