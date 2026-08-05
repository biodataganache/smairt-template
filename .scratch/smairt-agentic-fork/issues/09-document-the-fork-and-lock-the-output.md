# 09 - Document the fork and lock the generated output

**What to build:** Bring user-facing documentation into line with what the fork now generates:
update `README.md`, `QUICKSTART.md`, the tutorials, and `CONTEXT.md`'s glossary and invariants
to cover harness descriptors, assistant sets, the evidence capability, typed memory, domain
packs, and gate tokens; consolidate the prompt directory so `AI_CONTEXT.md` remains the single
canonical source and the overlapping priming and index files stop restating it; record the
seven architectural decisions as ADRs; and regenerate every golden so the full generated
surface is locked against accidental drift.

**Blocked by:** 08 - Name the researcher's decisions and record the critique.

**Status:** ready-for-agent

- [ ] `README.md` and `QUICKSTART.md` describe the fork's generated workspace accurately.
- [ ] `CONTEXT.md` defines harness descriptor, assistant set, reference registry, metrics registry, memory card, domain pack, and gate.
- [ ] `CONTEXT.md` invariants state that no registry is written by an assistant and no check refuses scientific work.
- [ ] ADRs 0004 through 0010 are committed.
- [ ] The prompt directory has no two files restating the same guidance.
- [ ] Goldens cover base, paper, hpc, evidence, and multi-assistant cases.
- [ ] Every release gate passes.
- [ ] `docs/scaffold-transition.md` records the scaffold version bump with no migration implied.
