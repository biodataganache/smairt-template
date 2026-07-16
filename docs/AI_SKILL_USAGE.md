# SMAIRT AI Skill Usage

This branch adds a portable AI skill at `skills/smairt-research/`.

## What was generated

- `skills/smairt-research/SKILL.md`: the main skill instructions.
- `skills/smairt-research/references/workflow.md`: optional details an assistant can load when needed.
- `skills/smairt-research/agents/openai.yaml`: UI metadata for OpenAI-style skill catalogs.

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

## Use as an OpenAI-style skill

Copy or package the full folder:

```text
skills/smairt-research/
```

The required entry point is `SKILL.md`. The `references/` folder is loaded only when the assistant needs extra workflow detail. The `agents/openai.yaml` file is optional UI metadata.

## Use through MCP

An MCP connector is useful when developers want the assistant to discover this workflow without manually pasting files. A minimal connector can expose:

- `smairt://skill/SKILL.md`
- `smairt://skill/workflow.md`
- `start_smairt_session`
- `continue_smairt_session`
- optionally, a `compile_smairt_context` tool that runs `scripts/compile_for_ai.py` in a generated SMAIRT project

MCP is a delivery layer here; the skill remains the source of truth.

For testing the MCP server with Claude before any shared deployment, see
`docs/LOCAL_MCP_TESTING.md`.

The skill does not need to be added to a generated project by default unless the maintainers want every new SMAIRT project to ship with it. A follow-up change could copy `skills/smairt-research/` into `{{ cookiecutter.project_slug }}/skills/` if that is the preferred distribution model.

## Shareable developer example

```text
I want to package SMAIRT as an AI skill. The skill entry point is `skills/smairt-research/SKILL.md`, with additional workflow detail in `skills/smairt-research/references/workflow.md`.

Please wire this into our assistant runtime so it can be invoked when users ask for AI-assisted computational research, scientific-method experiment loops, synthetic-to-real-data progression, experiment logging, or context reload across AI chats. If using MCP, expose the skill files as read-only resources and add prompts for starting and continuing a SMAIRT session.
```
