# {{ cookiecutter.project_name }} — Agent Instructions

This is a **SMAIRT** project (Scientific Method with AI Research Template). You are
starting this project to answer the question in `background/01_initial_question.md`.

**Read these files before doing any work:**

1. `prompts/AI_CONTEXT.md` — your role and the SMAIRT workflow
2. `prompts/CODE_CONVENTIONS.md` — code formatting conventions
3. `background/01_initial_question.md` — the research question and starting context
{% if cookiecutter.agent_topology == 'orchestrated' %}
## Memory & roles (orchestrated mode)

This project runs in **orchestrated topology**. Treat memory as files, not chat:

- `PROJECT_STATE.md` — layer 1: where we are right now (read at every session start)
- `FINDINGS.md` — layer 2: durable, scoped findings (read before designing anything)
- `prompts/COMPACTION.md` — how to compact, promote findings, and restart cheaply
- `prompts/roles/ORCHESTRATOR.md` — your default role: design, delegate, review, own memory
- `prompts/roles/BUILDER.md` — the disposable worker you spawn for execution-heavy tasks
- `prompts/handoffs/` — Build Brief / Build Report templates for delegation

Default to acting as the **Orchestrator**: keep this thread lean, delegate noisy
execution (debugging, big logs) to Builders, and never trust a Builder's result
without checking the log file.
{% endif %}
## SMAIRT workflow

Follow the workflow described in those files:

- **Numbered scripts** — name experiment scripts `script_XX_brief_description.py`
  (or track-based: `script_A01_...`, `script_B01_...`).
- **Dual output** — every run writes to **the console *and* `results/logs/`**
  (use `TeeLogger` from `scripts/shared/logging`).
{% if cookiecutter.workflow_mode == 'browser_paste' %}- **Pasted-output comment block** — at the end of each script, append the run's
  console output as a comment block at the bottom of the file. This project uses
  the legacy **browser-paste** convention, where the script itself preserves
  results because the AI may not have direct file access.
{% else %}- **Audit trail, not paste blocks** — results live in `results/logs/` and the
  per-iteration `analysis/ANALYSIS_XX.md` files. Do **not** paste console output
  into scripts as comments; read the log files directly. (This is the IDE-native
  default; see `prompts/AI_CONTEXT.md`.)
{% endif %}

## On first contact with this project

**Don't write any code yet.** First:

1. Summarize the research question.
2. Propose a first hypothesis.
3. Propose an experiment to test it.

Wait for the collaborator to confirm or adjust before generating any scripts.

---

Research Question: {{ cookiecutter.initial_research_question }}
