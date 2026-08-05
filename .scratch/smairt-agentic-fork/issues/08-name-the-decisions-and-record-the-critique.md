# 08 - Name the researcher's decisions and record the critique

**What to build:** Give the five decisions the twelve steps assign to the researcher stable
gate tokens `G1` through `G5` covering the research question, the hypothesis, the decision
criterion, the revise-advance-stop decision, and the contribution record, so an assistant can
be told to stop at a named gate and a project can record that it did. Add
`analysis/CRITIQUE_NN.md` recording adversarial critique with roles drawn from the domain
pack, distinguishing objections answered from objections accepted as limitations, since
structured critique was the largest single quality contributor in the published ablation. Add
a `Decision` column to `ITERATION_LOG.md` recording `Proceed`, `Refine`, or `Pivot`, which
names the choice step 11 already requires. No gate is decided by the tool or the assistant.

**Blocked by:** 07 - Supply domain vocabulary and baselines as data.

**Status:** ready-for-agent

- [ ] `docs/12_STEPS.md` names each gate with its token and owner.
- [ ] Guidance instructs an assistant to stop at a named gate and present options.
- [ ] `analysis/CRITIQUE_NN.md` exists as a template using domain-supplied roles.
- [ ] The critique template separates answered objections from accepted limitations.
- [ ] `ITERATION_LOG.md` records `Proceed`, `Refine`, or `Pivot` per iteration.
- [ ] The decision column is written by an existing helper, not by an assistant editing the table.
- [ ] No component selects a gate outcome, ranks a direction, or scores a hypothesis.
- [ ] A test asserts the gate tokens are stable and documented.
