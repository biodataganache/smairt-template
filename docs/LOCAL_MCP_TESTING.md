# Testing the SMAIRT Skill with Claude Code

This guide shows how to test the SMAIRT research skill as a local MCP server.
It is intended for early local evaluation before proposing any shared registry
or hosted deployment.

This test does not require a public URL or an MCP catalog entry. Claude Code
starts the MCP server as a local stdio process.

## What this proves

The local MCP server exposes the SMAIRT workflow to Claude Code as discoverable
tools, prompts, and read-only resources. A user can then ask Claude to use
SMAIRT, and Claude can call the local server for the project-start or
project-continuation workflow.

The initial server is intentionally read-only. It returns the skill instructions
and structured SMAIRT prompts; it does not modify files or send data anywhere.

## Requirements

- Python 3.10 or newer
- Claude Code installed and signed in
- This repository cloned locally

## 1. Create a Python environment

From the repository root:

```bash
python3 -m venv .venv-smairt-mcp
source .venv-smairt-mcp/bin/activate
python -m pip install -r skills/smairt-research/requirements.txt
```

## 2. Register the local MCP server with Claude Code

Run this from the repository root after activating the environment:

```bash
claude mcp add --scope local --transport stdio smairt-research -- \
  "$(pwd)/.venv-smairt-mcp/bin/python" \
  "$(pwd)/skills/smairt-research/mcp_server.py"
```

The `--scope local` option keeps this configuration private to your current
Claude Code project instead of committing shared configuration to the repository.

## 3. Confirm Claude Code can see the server

Start Claude Code from the repository root:

```bash
claude
```

Inside Claude Code, run:

```text
/mcp
```

You should see a server named `smairt-research` with available tools.

## 4. Try the skill in chat

Ask Claude:

```text
Use the SMAIRT research skill.

Research question: Can graph neural networks improve prediction of protein
complex stability?
Current phase: synthetic
Current hypothesis: help me define one

Design the first testable experiment and show the expected SMAIRT project
updates.
```

Expected behavior:

- Claude recognizes that the SMAIRT MCP server is relevant.
- Claude calls a SMAIRT tool such as `start_smairt_session` or
  `get_smairt_skill`.
- Claude responds with a scientific-method workflow organized around
  Background, Hypothesis, Methods, Results, Analysis, and Future Directions.

## Available local tools

The server currently exposes:

- `get_smairt_skill`: returns the skill instructions and workflow reference.
- `start_smairt_session`: creates a structured prompt for starting a SMAIRT
  research project.
- `continue_smairt_session`: creates a structured prompt for interpreting recent
  results and choosing next experiments.

It also exposes read-only resources:

- `smairt://skill/SKILL.md`
- `smairt://skill/workflow.md`

## Troubleshooting

If Claude Code does not show the server, confirm that the environment was
created and that the server script compiles:

```bash
source .venv-smairt-mcp/bin/activate
python -m py_compile skills/smairt-research/mcp_server.py
```

If you need to remove the local registration and add it again:

```bash
claude mcp remove smairt-research
```

Then repeat the registration command above.

## Later deployment

This local test is only a proof of value. Remote HTTP testing and shared MCP
catalog registration can be considered later if the local workflow is useful.
