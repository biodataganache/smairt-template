# SMAIRT AI Skill Usage

The portable skills under `skills/` describe the supported SMAIRT research
workflow. They are instruction references for coding assistants; project
creation remains the responsibility of the installed `smairt` CLI.

## Available Skills

- `skills/smairt-research/` covers the core scientific workflow.
- `skills/smairt-paper-driven/` adds publication-focused guidance. Despite its
  historical name, it is an overlay on the core workflow, not a separate mode.

Each folder contains a `SKILL.md`, optional detail under `references/`, and
optional catalog metadata under `agents/`.

## Use

Install SMAIRT and create the project first:

```bash
uv tool install .
smairt new
```

Then make the relevant skill folder available to an assistant that supports
skills, or direct the assistant to read its `SKILL.md`. The assistant should
also read the generated project's `prompts/AI_CONTEXT.md` and work with project
files directly.

The expected audit trail is:

```text
question/background -> hypothesis -> phase experiment -> results/logs
  -> analysis/decision -> study report
```

Paper-enabled projects retain that chain and add `paper/` as a publication
overlay. Skills do not create projects, replace the CLI, validate scientific
claims, or imply an external assistant integration.
