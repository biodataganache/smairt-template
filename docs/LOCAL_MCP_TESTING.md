# Testing the SMAIRT Skill with Claude

This guide shows how to test the SMAIRT research skill as an MCP server before
proposing any shared registry or hosted deployment.

The easiest demo path is to run the MCP server locally, expose it temporarily
with ngrok, and add it to Claude as a custom connector. This lets someone test
the workflow in Claude web without installing or debugging Claude Code.

## What this proves

The MCP server exposes the SMAIRT workflow to Claude as discoverable tools,
prompts, and read-only resources. A user can then ask Claude to use SMAIRT, and
Claude can call the server for the project-start or project-continuation
workflow.

The initial server is intentionally read-only. It returns the skill instructions
and structured SMAIRT prompts; it does not modify files or send data anywhere.

## Requirements

- Python 3.10 or newer
- This repository cloned locally
- An ngrok account
- Access to Claude custom connectors

Claude custom connectors using remote MCP are available in Claude web, but setup
depends on the account type. Individual Pro or Max users can add a custom
connector themselves. Team or Enterprise users may need an organization owner to
add the connector before members can enable it.

## 1. Create a Python environment

From the repository root:

```bash
python3 -m venv .venv-smairt-mcp
source .venv-smairt-mcp/bin/activate
python -m pip install -r skills/smairt-research/requirements.txt
```

## 2. Get an ngrok auth token

1. Sign in or create an account at `https://dashboard.ngrok.com/`.
2. Open `Your Authtoken` in the ngrok dashboard.
3. Copy the token.
4. Set it in your shell:

```bash
export NGROK_AUTHTOKEN="paste-your-token-here"
ngrok config add-authtoken "$NGROK_AUTHTOKEN"
```

Do not commit the token to the repository.

## 3. Start the SMAIRT MCP server in HTTP mode

From the repository root, with the Python environment activated:

```bash
python skills/smairt-research/mcp_server.py \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 8000
```

Leave this terminal running.

## 4. Start the ngrok tunnel

In a second terminal:

```bash
ngrok http 8000
```

Copy the HTTPS forwarding URL that ngrok prints. The MCP endpoint is that URL
with `/mcp` appended:

```text
https://your-ngrok-domain.ngrok-free.app/mcp
```

## 5. Add the connector in Claude web

In Claude web:

1. Open `Settings`.
2. Go to `Customize` and then `Connectors`.
3. Add a custom connector.
4. Paste the ngrok MCP URL, ending in `/mcp`.
5. Add the connector.
6. In a new chat, enable the connector from the chat tools/connectors menu.

For Team or Enterprise Claude accounts, an organization owner may need to add
the custom connector first. After that, individual users can connect and enable
it in their own chats.

## 6. Try the skill in chat

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

- Claude recognizes that the SMAIRT MCP connector is relevant.
- Claude calls a SMAIRT tool such as `start_smairt_session` or
  `get_smairt_skill`.
- Claude responds with a scientific-method workflow organized around
  Background, Hypothesis, Methods, Results, Analysis, and Future Directions.

## Available tools

The server currently exposes:

- `get_smairt_skill`: returns the skill instructions and workflow reference.
- `start_smairt_session`: creates a structured prompt for starting a SMAIRT
  research project.
- `continue_smairt_session`: creates a structured prompt for interpreting recent
  results and choosing next experiments.

It also exposes read-only resources:

- `smairt://skill/SKILL.md`
- `smairt://skill/workflow.md`

## Optional: Test with Claude Code

If Claude Code is already installed and working, you can test without ngrok by
registering the same server as a local stdio MCP server:

```bash
claude mcp add --scope local --transport stdio smairt-research -- \
  "$(pwd)/.venv-smairt-mcp/bin/python" \
  "$(pwd)/skills/smairt-research/mcp_server.py"
```

Then start Claude Code from the repository root and run:

```text
/mcp
```

You should see a server named `smairt-research` with available tools.

## Troubleshooting

If the Python server does not start, confirm that the environment was created
and that the server script compiles:

```bash
source .venv-smairt-mcp/bin/activate
python -m py_compile skills/smairt-research/mcp_server.py
```

If Claude web cannot connect, check:

- The Python server terminal is still running.
- The ngrok terminal is still running.
- The connector URL starts with `https://` and ends with `/mcp`.
- Your Claude account can add custom connectors, or an organization owner has
  added the connector for the workspace.

This is only a proof of value. Shared MCP catalog registration can be considered
later if the remote connector workflow is useful.
