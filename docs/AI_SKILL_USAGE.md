# SMAIRT AI Skill Usage

This branch adds a portable AI skill at `skills/smairt-research/`.

## What was generated

- `skills/smairt-research/SKILL.md`: the main skill instructions.
- `skills/smairt-research/references/workflow.md`: optional details an assistant can load when needed.
- `skills/smairt-research/agents/openai.yaml`: UI metadata for OpenAI/Codex-style skill catalogs.

## Use in an existing ChatGPT or Claude workflow

For a low-friction test, add the two Markdown files as project/context knowledge, custom instructions, or a pinned prompt:

1. `skills/smairt-research/SKILL.md`
2. `skills/smairt-research/references/workflow.md`

Then start with:

```text
Use the SMAIRT research skill for this project.

Research question: [your question]
Current phase: synthetic
Current hypothesis: [your hypothesis or "please help define it"]

Help me design the first testable experiment, generate a numbered script, log output to results/logs, and create a results comment block so the project can be reloaded into future AI sessions.
```

## Use as a Codex/OpenAI-style skill

Copy or package the full folder:

```text
skills/smairt-research/
```

The required entry point is `SKILL.md`. The `references/` folder is loaded only when the assistant needs extra workflow detail. The `agents/openai.yaml` file is optional UI metadata.

## Runtime Scope

These are instruction packages, not MCP servers or API clients. SMAIRT does not
configure external providers. In generated projects, Zoo Code supplies any
enabled Brave and Exa tools while `prompts/LITERATURE_RESEARCH.md` defines the
human-reviewed scientific workflow around them.

## PR path

You can push this branch and open a PR for review. The branch can be reviewed before the skill is treated as part of the template:

```bash
git push -u origin codex-smairt-ai-skill
```

The skill does not need to be added to a generated project by default unless the maintainers want every new SMAIRT project to ship with it. A follow-up PR could copy `skills/smairt-research/` into `{{ cookiecutter.project_slug }}/skills/` if that is the preferred distribution model.

## Shareable developer example

```text
I want to package SMAIRT as an AI skill. The skill entry point is `skills/smairt-research/SKILL.md`, with additional workflow detail in `skills/smairt-research/references/workflow.md`.

Please wire this into our assistant runtime so it can be invoked when users ask for AI-assisted computational research, scientific-method experiment loops, synthetic-to-real-data progression, experiment logging, or context reload across AI chats.
```
