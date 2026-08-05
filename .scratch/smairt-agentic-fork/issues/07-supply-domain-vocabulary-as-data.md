# 07 - Supply domain vocabulary and baselines as data

**What to build:** Add `domains/<id>.yaml` packs declaring a display name, vocabulary,
standard baselines, hypothesis-stage and analysis-stage critique roles, known pitfalls, and
metric conventions, resolved from the `project.domain` field already in the contract and
falling back to `generic` for an unrecognized value. Ship packs for `generic`,
`computational-biology`, and `machine-learning`, and require that adding a domain is a YAML
file plus a fixture with no code change. A pack supplies vocabulary and roles only; it never
prescribes a method, selects a baseline, or asserts what is novel.

**Blocked by:** 06 - Make accumulated lessons retrievable.

**Status:** ready-for-agent

- [ ] A project resolves its pack from `project.domain`.
- [ ] An unrecognized domain resolves to `generic` without error.
- [ ] Each shipped pack declares every documented field.
- [ ] Adding a pack requires no change outside `domains/` and test fixtures.
- [ ] Critique roles differ meaningfully between the biology and ML packs.
- [ ] No pack prescribes a statistical method or names a result as novel.
- [ ] A test asserts every pack validates against the schema.
- [ ] `docs/DOMAINS.md` documents the schema and how to add a pack.
