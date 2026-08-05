# ADR 0010: Defer the MCP Server and Mirror the Helpers When It Arrives

Status: Accepted

## Context

Exposing SMAIRT's helpers over a tool protocol would let a stage-aware context plan replace an
assistant reading many prompt files, which is the largest remaining context saving after typed
memory. It would also let an external orchestrator drive a project directly.

Against that, a server is a running process and per-harness configuration in several formats,
and it can only be judged once the artifacts it would expose exist. Whether native skills
alone suffice is an empirical question, and answering it first avoids building a protocol
surface around registries and cards whose shape may still move.

Wrapping harness command-line tools was considered and rejected outright. It would make the
tool an agent runtime, contradicting the position that the dashboard manages workspace
utilities while scientific work stays with the assistant, and it would mean tracking the
flags, authentication, and configuration of six independently churning tools. It is also
unnecessary: another system already ships runners for several harnesses, and a project whose
artifacts are legible can be driven by any orchestrator without becoming one.

## Decision

The server is deferred. Native skills and thin activators ship first, and whether a server is
warranted is decided from experience with them.

When it arrives, it mirrors the existing helper scripts and holds no authority of its own.
Every tool is a thin wrapper over the same code a researcher runs by hand, so the two paths
cannot diverge and the project remains fully usable without the server.

The tool never orchestrates a harness command-line tool. Legibility of artifacts, not
orchestration, is how external automation is supported.

## Consequences

- The fork ships without a running process to install or debug, and every capability is reachable by hand.
- The largest context saving is realized through the memory index rather than a protocol, which is less efficient and much simpler.
- An external orchestrator must invoke helper scripts rather than call tools, which is more verbose and equally capable.
- Because the server would mirror the helpers, deferring it costs no design work: the helpers are the interface.
- Declining orchestration keeps the boundary between workspace management and scientific work intact and avoids six moving integration targets.
- Should the server prove unnecessary, nothing has been built that must be removed.
