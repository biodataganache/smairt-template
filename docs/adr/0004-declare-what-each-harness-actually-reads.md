# ADR 0004: Declare What Each Harness Actually Reads

Status: Accepted

## Context

SMAIRT wrote one pointer file per assistant from a hard-coded map of six paths, and every
pointer received an identical body. Two of those six were wrong. `ZOO.md` is not a path Zoo
Code reads; Zoo Code reads `.roo/rules/`, falls back to `.roorules`, and also reads
`AGENTS.md`. A `.mdc` file in `.cursor/rules` without frontmatter is a manual rule that stays
dormant until it is @-mentioned, and Cursor ignores a plain `.md` there entirely.

Project Check tested only that the pointer file existed, so both failures were silent. A
researcher selecting Zoo Code or Cursor received a file their assistant never loaded and a
tool that reported the project healthy. An earlier review noted that Zoo Code had no pointer;
the remedy invented a filename rather than adopting the documented convention, which is how an
unread file came to be declared tool guidance.

Continuing with a path map cannot fix this, because the map has no place to record the two
facts that matter: what body format makes a file load, and which previously written paths are
now wrong.

## Decision

A harness is described by a declared descriptor rather than a path. `harnesses.yaml` records,
per assistant, the artifact that assistant genuinely reads, the body format that causes it to
load, whether it reads `AGENTS.md`, its launch command, and the legacy paths SMAIRT previously
wrote.

Format drives the body. Zoo Code and Cursor share a frontmatter schema of `description`,
`globs`, and `alwaysApply`, so one renderer serves both and emits `alwaysApply: true`. Claude
Code and the `AGENTS.md` family receive plain markdown. Because Zoo Code, OpenCode, Codex, and
Cursor all read `AGENTS.md`, it is the shared spine and native files are thin activators
pointing at `prompts/AI_CONTEXT.md`. Activators stay minimal, since an always-applied rule
costs context on every request.

Project Check verifies loadability rather than existence. A pointer present in a format its
harness cannot load is reported as a defect.

A legacy pointer is rewritten to a deprecation note naming the correct path. It is never
deleted, and a researcher-modified one is reported and left alone.

## Consequences

- A harness path claim is now testable against vendor documentation, so an invented path cannot ship again.
- Adding a harness is a descriptor entry rather than edits scattered across the generator, check, and launch paths.
- Two formats must be rendered and tested where one sufficed, and a frontmatter change in either vendor is a maintenance obligation.
- Existing Zoo Code projects gain a correct file and keep a deprecated one, so the project is briefly larger by one explanatory file.
- Project Check reports defects in projects that previously passed, which is the intended correction of a false negative.
- `AGENTS.md` becoming the spine means four harnesses share one reviewed file rather than four near-duplicates.
