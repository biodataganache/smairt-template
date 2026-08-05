# 06 - Make accumulated lessons retrievable

**What to build:** Introduce `memory/` holding typed cards under `patterns/`, `episodes/`,
`decisions/`, and `lessons/`, each carrying frontmatter with a kind, stage, confidence,
retrieval hints, an updated timestamp, an optional `supersedes`, and mandatory non-empty
`evidence_paths`, because a lesson that cites no evidence cannot be re-examined and is an
assertion rather than a finding. Add `memory/INDEX.md` declaring which kinds each stage loads
first, so an assistant retrieves a handful of relevant cards instead of reading every prompt
file in the project. Reduce `KNOWN_PATTERNS.md` to conventions and environment facts and point
it at `memory/`, rewriting no existing researcher content, and mark a superseded card rather
than deleting it so a reversal stays visible.

**Blocked by:** 01 - Establish the SMAIRT Lab baseline.

**Status:** ready-for-agent

- [ ] A new project contains `memory/` with the four kind directories and `INDEX.md`.
- [ ] A card without `evidence_paths` fails validation with a clear message.
- [ ] `INDEX.md` names the kinds each stage loads first.
- [ ] A superseded card is marked and retained, never deleted.
- [ ] `KNOWN_PATTERNS.md` retains conventions and points at `memory/`.
- [ ] An existing `KNOWN_PATTERNS.md` in a project is not rewritten.
- [ ] A test asserts every shipped card validates against the frontmatter schema.
- [ ] Guidance states memory never substitutes for a log or an analysis.
