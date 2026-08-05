# 05 - Bind every reported number to a logged run

**What to build:** Within the `evidence` capability, add `scripts/shared/metrics.py` exposing
`report_metric(name, value, condition=..., seed=...)` so an experiment records its measurements
to `results/metrics/iteration_NN.json` as it runs, each row binding a value to the condition,
seed, and exact log path that produced it; then add `scripts/verify_claims.py`, which extracts
numerics from an analysis, matches each against the registry scoped per condition so a value
correct for one condition is not accepted for another, and reports every claim it cannot match.
The registry is written only by instrumented code at run time, so an assistant may compose an
analysis but cannot introduce a number into the evidence. The verifier reports and never edits
an analysis, and is never invoked by Project Check, because the tool must not refuse scientific
work.

**Blocked by:** 04 - Bind every citation to a resolvable identifier.

**Status:** ready-for-agent

- [ ] A generated iteration script records metrics to `results/metrics/iteration_NN.json`.
- [ ] Each row records metric, value, condition, seed, and the exact log path.
- [ ] `report_metric` appends and never overwrites an existing row.
- [ ] `verify_claims.py` reports a number absent from the registry.
- [ ] A claim matching a row under a different condition is reported rather than accepted.
- [ ] The verifier leaves every analysis file byte-identical.
- [ ] The verifier is unreachable from `smairt-lab check` and blocks nothing.
- [ ] `analysis/CLAIMS.md` records each claim's verdict, support, and limitations.
- [ ] Goldens gain an evidence-enabled case.
