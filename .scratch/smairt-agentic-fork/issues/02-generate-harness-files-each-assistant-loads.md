# 02 - Generate harness files each assistant actually loads

**What to build:** Replace the six ad-hoc pointer paths with a declarative `harnesses.yaml`
naming, per assistant, the project artifact that assistant genuinely reads, the body format
that makes it load, whether it reads `AGENTS.md`, its launch command, and any legacy paths
SMAIRT previously wrote; then render bodies by format so Zoo Code receives
`.roo/rules/smairt.md` and Cursor receives `.cursor/rules/smairt.mdc`, both with
`description`, `globs`, and `alwaysApply: true`, while `CLAUDE.md` and `AGENTS.md` stay plain
markdown. Rewrite an unmodified `ZOO.md` to a deprecation note naming the correct path, never
deleting it and never touching a modified one. Extend Project Check to test loadability rather
than mere existence, and state per selected harness in the creation summary, verbose check, and
a new `docs/HARNESSES.md` what was written, whether it loads automatically, and why project
rules are preferred over global rules.

**Blocked by:** 01 - Establish the SMAIRT Lab baseline.

**Status:** ready-for-agent

- [ ] A Zoo Code project contains `.roo/rules/smairt.md` and Zoo Code loads it without being asked.
- [ ] A Cursor project contains `.cursor/rules/smairt.mdc` with `alwaysApply: true`.
- [ ] An existing unmodified `ZOO.md` is rewritten to a deprecation note naming `.roo/rules/smairt.md`.
- [ ] A modified `ZOO.md` is reported and left byte-identical.
- [ ] `smairt-lab check` reports `harness-pointer-not-loadable` for a frontmatter-less `.mdc`.
- [ ] `smairt-lab check` reports `legacy-harness-pointer` when a legacy path is present, with a repair.
- [ ] `docs/HARNESSES.md` records each harness's artifact, activation, `AGENTS.md` support, and global-rules position.
- [ ] A test asserts every descriptor pointer and format against the vendor-documented convention.
- [ ] A test asserts every assistant's generated artifact is loadable per its descriptor.
