# SMAIRT Quick Start Guide

Get a SMAIRT project running in under 5 minutes.

---

## Prerequisites

- Python 3.8+
- An AI assistant (Zoo Code recommended, or Cursor, Windsurf, ChatGPT, Claude)

---

## Step 1: Install Cookiecutter

```bash
pip install cookiecutter
```

---

## Step 2: Generate Your Project

```bash
cookiecutter gh:biodataganache/smairt-cookiecutter
```

You'll be prompted for:
- **Project name** — Your research project name
- **Project mode** — `standard` (exploration) or `paper_driven` (paper-first)
- **Workflow mode** — `ide_native` (recommended for Zoo Code/Cursor) or `browser_paste`
- **AI tool** — Which AI tool you primarily use
- **Research question** — What you're investigating
- **Starting phase** — Where to begin: `synthetic`, `downloaded`, or `real`

---

## Step 3: Orient Your AI

### IDE-Native (Zoo Code, Cursor, Windsurf)

Open your project in VSCode and tell your AI:

```
Please read prompts/AI_CONTEXT.md to understand this project.
Then read prompts/CONTEXT_INDEX.md to know what files to reference.
```

That's it. Your AI now understands the workflow.

### Optional: Configure Reviewed Literature Search in Zoo Code

1. Open Zoo Code settings.
2. Enable or configure Brave Search and enter its key only in Zoo's key field.
3. Enable or configure Exa and enter its key only in Zoo's key field.
4. Return to the generated SMAIRT project.
5. Run `/smairt-literature-search` and confirm Zoo can access both tools.

Never paste provider keys into chat or put them in `.env`, Markdown, scripts,
logs, or project configuration. If a tool is unavailable, Zoo should explain
the GUI setup without asking for the key.

Brave and Exa discover candidates. SMAIRT records the search and requires the
researcher to approve sources before Zoo creates local folders under
`references/`. Researchers can then place papers, supplements, and data in those
folders for long-term local grounding.

### Browser-Paste (ChatGPT, Claude web)

Give your AI these 3 files:
1. `prompts/AI_CONTEXT.md` — Its role and workflow
2. `prompts/CODE_CONVENTIONS.md` — How to write code
3. `prompts/KNOWN_PATTERNS.md` — Patterns to reuse, errors to avoid

Use prompts from `prompts/SESSION_START.md` to start sessions.

---

## Step 4: Review Relevant Literature

When prior work informs the question, ask the AI to read
`prompts/LITERATURE_RESEARCH.md`. In Zoo Code, run:

```text
/smairt-literature-search [optional topic]
```

Approve the search strategy, review the deduplicated candidates, and select
which sources should enter the local reference corpus. Search results are not
treated as evidence until the researcher approves and verifies them.

---

## Step 5: Write Your First Hypothesis

Create `hypotheses/HYPOTHESIS_01.md` (use the template in `hypotheses/HYPOTHESIS_TEMPLATE.md`):

```markdown
# Hypothesis 01 — [Your prediction]

## Status: PENDING

## Hypothesis Statement
**Prediction**: [What you expect to happen]
**Rationale**: [Why you expect this]
**Success criteria**: [How to tell if it worked]
```

---

## Step 6: Run Your First Experiment

Ask your AI to create a script that tests your hypothesis. It will:
1. Follow naming conventions (`script_01_description.py`)
2. Use `TeeLogger` for dual console/file output
3. Place it in the appropriate phase directory
4. Include the hypothesis reference in the docstring

Run the script and let the AI interpret the results.

---

## Step 7: Record Results

After running an experiment:
1. **AI reads the log file** and interprets results
2. **AI writes analysis** to `analysis/ANALYSIS_01.md`
3. **AI suggests next hypothesis** based on findings
4. **You update** `prompts/intellectual_contribution.md` with your key decisions
5. **Update** `prompts/KNOWN_PATTERNS.md` if new patterns or errors were discovered

---

## Step 7: Iterate

```
Hypothesis_01 → script_01 → ANALYSIS_01 → Hypothesis_02 → script_02 → ...
```

As the project grows:
- Fork into tracks (A, B, C...) for parallel investigations
- Create plans before complex multi-step work
- Extract repeated code to `scripts/shared/`
- Keep `KNOWN_PATTERNS.md` current

---

## What's Next?

- Read `docs/12_STEPS.md` for the full methodology
- Read `docs/SMAIRT_PHILOSOPHY.md` for the "why"
- Check `prompts/SESSION_START.md` for situation-specific prompts
- See `TUTORIAL.md` for a complete walkthrough

---

## Quick Reference

| Task | Action |
|------|--------|
| Start new project | `cookiecutter gh:biodataganache/smairt-cookiecutter` |
| Orient AI | Point to `prompts/AI_CONTEXT.md` |
| New hypothesis | Create `hypotheses/HYPOTHESIS_XX.md` |
| New experiment | Ask AI to create script following conventions |
| Record results | AI writes `analysis/ANALYSIS_XX.md` |
| Track patterns | Update `prompts/KNOWN_PATTERNS.md` |
| Plan complex work | Create `plans/PLAN_description.md` |
| Cross-tool transfer | Run `python scripts/compile_for_ai.py` |
| Track contributions | Update `prompts/intellectual_contribution.md` |
